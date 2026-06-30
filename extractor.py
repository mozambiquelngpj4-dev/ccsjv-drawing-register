import fitz
import os
import re
import pandas as pd

def process_pdf(pdf_path, original_name=None):

    drawing_register = []

    if original_name:
        file = original_name
    else:
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
        # Drawing Number (from PDF filename)
        # Example:
        # 033-AV-0026_512_0.pdf
        # -> 033-AV-0026/512
        # ---------------------------------------

        filename = os.path.splitext(file)[0]

        # Remove the trailing "_0", "_1", etc.
        filename = re.sub(r"_\d+$", "", filename)

        # Replace the remaining "_" with "/"
        drawing_no = filename.replace("_", "/")

        # ----------------------------
        # Other Fields
        # ----------------------------
        for line in lines:

            # CCSJV Drawing Number
                m = re.search(
                    r"MZ-\d{3}-CCX-PI-ISO-[A-Z0-9-]+",
                    text,
                    re.IGNORECASE
            )

                if m:
                    ccsjv_dwg = m.group()
          
            # ==========================================
            # Line Number
            # ==========================================

                m = re.search(
                    r'\d{3}-.*?-[A-Z]{2}-\d{4}-[A-Z0-9]+-[A-Z]',
                    text
                )

                if m:
                    line_no = m.group()

            # ==========================================
            # Line Number
            # ==========================================

                m = re.search(
                    r'\d{3}-[\d\.]+"{1,2}-[A-Z]{2}-\d{4}-[A-Z0-9]+-[A-Z]',
                    text
                )

                if m:
                    line_no = m.group()

            # ==========================================
            # PID Number
            # ==========================================

                m = re.search(
                    r"MZ-\d{3}-CCX-PR-PID-[A-Z0-9-]+",
                    text,
                    re.IGNORECASE
)

                if m:
                    pid_no = m.group()

            # ==========================================
            # NPS (from Line Number)
            # ==========================================

                nps = ""

                if line_no:

                    m = re.search(
                        r'-(\d+(?:\.\d+)?)"{1,2}',
                        line_no
                    )

                    if m:
                        nps = m.group(1)
                
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

            # Keep NPS from Line Number
            if not nps:
                 nps = table_pattern.group(1)

            # Keep Line Class from Line Number
            if not line_class:
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
            "Drawing No": ccsjv_dwg,
            "CCSJV DWG": drawing_no,
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

    columns_to_fill = [
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

    drawing_df[columns_to_fill] = (
    drawing_df[columns_to_fill]
    .replace("", pd.NA)
    .ffill()
    .fillna("")
)

    return drawing_df
