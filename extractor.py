import fitz
import os
import re
import pandas as pd

def normalize_ocr(line):
    # Fix minus spacing
    line = re.sub(r'-\s+', '', line)

    # Join digits/letters split by spaces
    line = re.sub(r'(?<=\w)\s+(?=\w)', '', line)

    # Fix broken decimals
    line = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', line)

    # Remove extra spaces
    line = re.sub(r'\s+', ' ', line).strip()

    return line



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



    for page_no in range(doc.page_count):

        page = doc.load_page(page_no)

        text = page.get_text("text")


        normalized_lines = [
            normalize_ocr(line)
            for line in text.splitlines()
        ]


        normalized_text = "\n".join(normalized_lines)


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
                r'(MZ-\d{3}-CCX-[A-Z]{2}-PID-\d{5}-\d{2}|[A-Z]+\d*-\d{3}-\d{3}/\d{3}|\d{3}-\d{5}(?:-\d+)+)',
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
            text,
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
            r'([A-Z]+)\s+'
            r'(\d+(?:\.\d+)?)\s+'
            r'(-?\d+(?:\.\d+)?)\s+'
            r'(-?\d+(?:\.\d+)?)\s+'
            r'(\d+(?:\.\d+)?)\s+'
            r'([A-Za-z\.]+)\s+'
            r'(\d+(?:\.\d+)?)\s+'
            r'([A-Z0-9]+)',

            normalized_text,

            re.I
        )



        print("TABLE ROWS:")
        print(table_rows)



        # =================================================
        # SELECT ROW MATCHING NPS
        # =================================================

        for row in table_rows:


            row_nps = row[0]


            if row_nps == nps:


                insul_type = row[2]

                insul_thk = row[3]

                oper_temp = row[4]

                des_temp = row[5]

                des_press = row[6]

                test_type = row[7]

                test_press = row[8]

                pnt_sys = row[9]


                break




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



    columns = [

        "Drawing No",
        "CCSJV DWG No",
        "Line No",
        "PID No",
        "Revision",
        "NPS(IN)",
        "LINE CLASS",
        "INSUL TYPE",
        "INSUL THK",
        "OPER.TEMP",
        "DES.TEMP",
        "DES.PRESS",
        "TEST TYPE",
        "TEST PRESS",
        "PNT SYS"

    ]



    df[columns] = (

        df[columns]
        .replace("", pd.NA)
        .ffill()
        .fillna("")

    )



    return df