import fitz
import os
import re
import pandas as pd


def normalize_test_type(value):
    value = value.upper().strip()

    # Remove spaces between single characters
    value = re.sub(r'(?<=\b[A-Z])\s+(?=[A-Z]\b)', '', value)

    # Remove all spaces when the word is mostly single letters
    if re.fullmatch(r'(?:[A-Z]\s+)+[A-Z]', value):
        value = value.replace(" ", "")

    return value



def normalize_field(value):

    # Remove spaces between characters/digits
    value = re.sub(r'\s+', '', value)

    return value.strip()

def normalize_text(value):
    value = re.sub(r'\s+', ' ', value)
    return value.strip()

def normalize_nps(value):
    value = str(value).strip()

    # Remove all spaces
    value = re.sub(r'\s+', '', value)

    # Common fractions
    fraction_map = {
        '1/2': '0.5',
        '3/4': '0.75',
        '11/2': '1.5',
        '21/2': '2.5',
        '31/2': '3.5',
        '41/2': '4.5'
    }

    if value in fraction_map:
        value = fraction_map[value]

    # Convert numeric strings cleanly
    try:
        num = float(value)
        if num.is_integer():
            return str(int(num))
        return str(num)
    except ValueError:
        return value


def normalize_ocr(line):

    # Fix minus spacing
    line = re.sub(r'-\s+', '-', line)

    # Fix broken decimals
    line = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', line)

    # Remove extra spaces
    line = re.sub(r'\s+', ' ', line).strip()

    return line



def normalize_pdf_line(line):

    line = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', line)

    line = re.sub(
        r'-\s*((?:\d\s*)+)\.\s*((?:\d\s*)+)',
        lambda m: '-' +
        re.sub(r'\s+', '', m.group(1)) +
        '.' +
        re.sub(r'\s+', '', m.group(2)),
        line
    )

    line = re.sub(r'(?<=\d)\s(?=\d)', '', line)

    line = re.sub(r'\s+', ' ', line).strip()

    return line




def process_pdf(pdf_path, original_name=None):

    drawing_register = []


    if original_name:
        file = original_name
    else:
        file = os.path.basename(pdf_path)



    doc = fitz.open(pdf_path)
    nps_lookup = {}

    # =================================================
    # FIRST PASS - BUILD NPS LOOKUP FOR ENTIRE PDF
    # =================================================

    for page_no in range(doc.page_count):

        page = doc.load_page(page_no)
        text = page.get_text("text")

       # normalized_lines = [
           # normalize_ocr(line)
          #  for line in text.splitlines()
        #]

        normalized_text = "\n".join(
            normalize_pdf_line(normalize_ocr(line))
            for line in text.splitlines()
            )

        table_rows = re.findall(

            r'(\d+(?:\.\d+)?)\s+'
            r'([A-Z0-9]+)\s+'
            r'([A-Z\s]+?)\s+'
            r'(\d+(?:\.\d+)?)\s+'
            r'(-?\d+(?:\.\d+)?)\s+'
            r'(-?\d+(?:\.\d+)?)\s+'
            r'(\d+(?:\.\d+)?)\s+'
            r'([A-Za-z\.]+(?:\s+[A-Za-z\.]+)*)\s*'
            r'(\d+(?:\.\d+)?)?\s*'
            r'([A-Za-z0-9/]+)?',

            normalized_text,
            re.I
        )

        for row in table_rows:

            nps_key = normalize_nps(row[0])

            if nps_key not in nps_lookup:

                nps_lookup[nps_key] = {

                    "INSUL TYPE": normalize_field(row[2]),
                    "INSUL THK": normalize_field(row[3]),
                    "OPER.TEMP": normalize_field(row[4]),
                    "DES.TEMP": normalize_field(row[5]),
                    "DES.PRESS": normalize_field(row[6]),
                    "TEST TYPE": normalize_text(row[7]),
                    "TEST PRESS": normalize_field(row[8]) if row[8] else "",
                    "PNT SYS": normalize_field(row[9])

                }

    for page_no in range(doc.page_count):

        page = doc.load_page(page_no)

        text = page.get_text("text")


        #normalized_lines = [
          #  normalize_ocr(line)
          #  for line in text.splitlines()
        #]


        normalized_text = "\n".join(
            normalize_pdf_line(normalize_ocr(line))
            for line in text.splitlines()
            )


        lines = [
            normalize_pdf_line(line)
            for line in text.splitlines()
            if line.strip()
        ]



        print("\n==========================")
        print(f"PDF : {file}")
        print(f"PAGE: {page_no+1}")
        print("==========================")

        for l in lines:
            print(l)



        # =================================================
        # INITIAL VALUES
        # =================================================

        drawing_no = ""
        ccsjv_dwg = ""
        line_no = ""
        pid_no = ""
        revision = ""

        nps = ""
        line_class = ""

        insul_type = ""
        insul_thk = ""

        oper_temp = ""
        des_temp = ""
        des_press = ""

        test_type = ""
        test_press = ""

        pnt_sys = ""



        # =================================================
        # DRAWING NUMBER FROM FILE NAME
        # =================================================

        filename = os.path.splitext(file)[0]

        filename = re.sub(
            r"_\d+$",
            "",
            filename
        )

        drawing_no = filename.replace("_","/")



        # =================================================
        # EXTRACT HEADER INFORMATION
        # =================================================

        for line in lines:



            # -------------------------------
            # CCSJV DRAWING
            # -------------------------------

            m = re.search(
                r"MZ-\d{3}-CCX-PI-ISO-[A-Z0-9-]+",
                line,
                re.I
            )

            if m:
                ccsjv_dwg = m.group()



            # -------------------------------
            # LINE NUMBER
            # -------------------------------

            m = re.search(
                r'\d{3}-(?:\d+(?:/\d+)?(?:\.\d+)?)"?-[A-Z]{1,3}-\d{4}[A-Z]?-?[A-Z0-9]+-[A-Z0-9]+',
                line,
                re.I
            )


            if m:
                line_no = m.group()



            # -------------------------------
            # PID NUMBER
            # -------------------------------

            m = re.search(
                r'(MZ-\d{3}-CCX-[A-Z]{2}-PID-\d{5}-\d{2}|'
                r'[A-Z]+\d*-\d{3}-\d{3}/\d{3}|'
                r'\d{3}-\d{5}(?:-\d+)+|'
                r'NA)',
                line,
                re.I
            )

            if m:
                pid_no = m.group()



        # =================================================
        # EXTRACT NPS FROM LINE NUMBER
        # =================================================

        if line_no:

            m = re.search(
                r'^\d{3}-(\d+(?:/\d+)?(?:\.\d+)?)',
                line_no
            )


            if m:
                nps = m.group(1)




        # =================================================
        # LINE CLASS
        # =================================================

        if line_no:

            m = re.search(
                r'-([A-Z0-9]+)-[A-Z0-9]+$',
                line_no
            )


            if m:
                line_class = m.group(1)



        # =================================================
        # REVISION
        # =================================================

        m = re.search(
            r"([A-Z0-9])\s+ISSUED FOR CONSTRUCTION",
            normalized_text,
            re.I
        )

        if m:
            revision = m.group(1)



        # =================================================
        # EXTRACT ALL TABLE ROWS
        # =================================================


        table_rows = re.findall(

            r'(\d+(?:\.\d+)?)\s+'
            r'([A-Z0-9]+)\s+'
            r'([A-Z\s]+?)\s+'
            r'(\d+(?:\.\d+)?)\s+'
            r'(-?\d+(?:\.\d+)?)\s+'
            r'(-?\d+(?:\.\d+)?)\s+'
            r'(\d+(?:\.\d+)?)\s+'
            r'([A-Za-z\.]+(?:\s+[A-Za-z\.]+)*)\s*'
            r'(\d+(?:\.\d+)?)?\s*'
            r'([A-Za-z0-9/]+)?',

            normalized_text,

            re.I
        )



        print("TABLE ROWS:")
        print(table_rows)



        # =================================================
        # GET TABLE DATA FROM ANY PAGE IN PDF
        # =================================================

        lookup_nps = normalize_nps(nps)

        if lookup_nps in nps_lookup:

            info = nps_lookup[lookup_nps]

            insul_type = info["INSUL TYPE"]
            insul_thk = info["INSUL THK"]
            oper_temp = info["OPER.TEMP"]
            des_temp = info["DES.TEMP"]
            des_press = info["DES.PRESS"]

            test_type = normalize_test_type(info["TEST TYPE"])

            if test_type == "NOTREQUIRED":
                test_press = ""
            else:
                test_press = info["TEST PRESS"]

                pnt_sys = info["PNT SYS"]


        # =================================================
        # SAVE RESULT
        # =================================================


        drawing_register.append({


            "ISO DWG": file,

            "Sheet No": page_no+1,

            "Drawing No": ccsjv_dwg,

            "CCSJV DWG No": drawing_no,

            "Line No": line_no,

            "PID No": pid_no,

            "Revision": revision,

            "NPS(IN)": nps,

            "LINE CLASS": line_class,

            "INSUL TYPE": insul_type,

            "INSUL THK": insul_thk,

            "OPER.TEMP": oper_temp,

            "DES.TEMP": des_temp,

            "DES.PRESS": des_press,

            "TEST TYPE": test_type,

            "TEST PRESS": test_press,

            "PNT SYS": pnt_sys

        })



    doc.close()

    df = pd.DataFrame(drawing_register)
    
    df = df.fillna("")

    return df

