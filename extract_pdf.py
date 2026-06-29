import fitz
import os
import re
import pandas as pd

def process_pdf(pdf_path):

    drawing_register = []

    file = os.path.basename(pdf_path)

    doc = fitz.open(pdf_path)

    # ======================================================
    # Process every page
    # ======================================================
    for page_no in range(doc.page_count):

        page = doc.load_page(page_no)
        text = page.get_text("text")

        lines = [line.strip() for line in text.splitlines() if line.strip()]
       
        print("\n==========================")
        print(f"PDF : {file}")
        print(f"Page: {page_no+1}")
        print("==========================")

        for line in lines:
            print(line)

        # --------------------------------------------------
        # Initialize variables
        # --------------------------------------------------
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

        # ---------------------------------------
        # Drawing Number
        # ---------------------------------------
        drawing_no = ""

        matches = re.findall(
            r"\b\d{3}-(?!PG\b)[A-Z]{1,3}-\d{4}/\d{3}\b",
            text
        )

        if matches:
            drawing_no = matches[-1]

        # ----------------------------
        # Other Fields
        # ----------------------------
        for line in lines:

            # CCSJV Drawing Number
            if line.startswith("MZ-") and "ISO" in line:
                ccsjv_dwg = line

            # Line Number
            elif '"' in line and re.search(r"\d{3}-\d+\"-[A-Z]{1,3}-", line):
                line_no = line

            # PID Number
            elif "PR-PID" in line:
                m = re.search(
                    r"MZ-\d{3}-CCX-PR-PID-\d{5}-\d{2}",
                    text
                )

                if m:
                    pid_no = m.group()

        # ==================================================
        # Revision
        # ==================================================
        m = re.search(
            r"([A-Z0-9])\s+ISSUED FOR CONSTRUCTION",
            text,
            re.IGNORECASE
        )

        if m:
            revision = m.group(1)

        # ==================================================
        # Process Data Table
        # ==================================================

        table_pattern = re.search(
            r'(\d+(?:\.\d+)?)\s+'          # NPS
            r'([A-Z0-9]+)\s+'              # Line Class
            r'([A-Z]+)\s+'                 # Insulation Type
            r'(\d+(?:\.\d+)?)\s+'          # Insulation Thickness
            r'(\d+(?:\.\d+)?)\s+'          # Operating Temp
            r'(\d+(?:\.\d+)?)\s+'          # Design Temp
            r'(\d+(?:\.\d+)?)\s+'          # Design Pressure
            r'([A-Z]+)\s+'                 # Test Type
            r'(\d+(?:\.\d+)?)',            # Test Pressure
            text
        )

        if table_pattern:
            nps = table_pattern.group(1)
            line_class = table_pattern.group(2)
            insul_type = table_pattern.group(3)
            insul_thk = table_pattern.group(4)
            oper_temp = table_pattern.group(5)
            des_temp = table_pattern.group(6)
            des_press = table_pattern.group(7)
            test_type = table_pattern.group(8)
            test_press = table_pattern.group(9)

        # ==================================================
        # Save Record
        # ==================================================
        drawing_register.append({

            "PDF": file,
            "Sheet": page_no + 1,
            "Drawing No": drawing_no,
            "CCSJV DWG": ccsjv_dwg,
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

    # ==========================================================
    # Create DataFrame
    # ==========================================================
    drawing_df = pd.DataFrame(drawing_register)

    column_order = [
        "PDF",
        "Sheet",
        "Drawing No",
        "CCSJV DWG",
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

    drawing_df = drawing_df.reindex(columns=column_order)

    return drawing_df