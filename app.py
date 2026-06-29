import streamlit as st
import pandas as pd
import tempfile
import os
import fitz
from PIL import Image

from extractor import process_pdf

def preview_pdf(uploaded_pdf, page_no=0):

    uploaded_pdf.seek(0)

    doc = fitz.open(
        stream=uploaded_pdf.read(),
        filetype="pdf"
    )

    page = doc.load_page(page_no)

    pix = page.get_pixmap(matrix=fitz.Matrix(2,2))

    image = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    doc.close()

    uploaded_pdf.seek(0)

    return image
# ============================================
# Page Configuration
# ============================================
st.set_page_config(
    page_title="CCSJV Drawing Register",
    page_icon="📄",
    layout="wide"
)

# ============================================
# Header
# ============================================
st.title("📄 CCSJV Drawing Register Extractor")
st.caption("Mozambique LNG Project")

st.markdown("---")

# ============================================
# Sidebar
# ============================================
st.sidebar.title("📂 CCSJV Drawing Register")

st.sidebar.markdown("---")

st.sidebar.write("### Uploaded PDFs")


# ============================================
# File Upload
# ============================================
# ============================================
# File Upload
# ============================================
uploaded_files = st.file_uploader(
    "Select PDF Files",
    type="pdf",
    accept_multiple_files=True
)

# ============================================
# Sidebar - Uploaded PDFs
# ============================================
if uploaded_files:

    st.sidebar.header("📂 Uploaded PDFs")

    pdf_names = [pdf.name for pdf in uploaded_files]

    selected_name = st.sidebar.selectbox(
        "Preview PDF",
        pdf_names
    )

    selected_pdf = next(
        pdf for pdf in uploaded_files
        if pdf.name == selected_name
    )

    st.sidebar.markdown("---")

    for pdf in uploaded_files:
        if pdf.name == selected_name:
            st.sidebar.success(f"📄 {pdf.name}")
        else:
            st.sidebar.write(f"📄 {pdf.name}")
            
# ============================================
# PDF Preview
# ============================================
if uploaded_files:

    st.subheader("📄 PDF Preview")

    image = preview_pdf(selected_pdf)

    st.image(
        image,
        caption=f"{selected_name} - Page 1",
        use_container_width=True
    )

# ============================================
# Process
# ============================================
if uploaded_files:

    st.success(f"{len(uploaded_files)} PDF(s) selected.")

    if st.button("🚀 Extract Drawing Register"):

        dfs = []

        progress = st.progress(0)

        status = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):

            status.info(f"Processing {uploaded_file.name}")

            uploaded_file.seek(0)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

                tmp.write(uploaded_file.read())

                tmp_path = tmp.name

            df = process_pdf(
                tmp_path,
                original_name=uploaded_file.name
            )

            dfs.append(df)

            os.remove(tmp_path)

            progress.progress((i + 1) / len(uploaded_files))

        final_df = pd.concat(
            dfs,
            ignore_index=True
        )

        status.success("Extraction Completed Successfully")

        # ============================================
        # Statistics
        # ============================================

        col1, col2, col3 = st.columns(3)

        col1.metric("PDF Files", len(uploaded_files))

        col2.metric("Sheets", len(final_df))

        col3.metric(
            "Drawing Numbers",
            final_df["Drawing No"].astype(bool).sum()
        )

        st.markdown("---")

        # ============================================
        # Preview
        # ============================================

        st.subheader("Preview")

        st.dataframe(
            final_df,
            use_container_width=True
        )

        # ============================================
        # Download Excel
        # ============================================

        excel_name = "CCSJV_Drawing_Register.xlsx"

        final_df.to_excel(
            excel_name,
            index=False,
            engine="openpyxl"
        )

        with open(excel_name, "rb") as f:

            st.download_button(
                "📥 Download Excel",
                f,
                file_name=excel_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # ============================================
        # Download CSV
        # ============================================

        csv = final_df.to_csv(index=False)

        st.download_button(
            "📄 Download CSV",
            csv,
            file_name="CCSJV_Drawing_Register.csv",
            mime="text/csv"
        )