import streamlit as st
import pandas as pd
import tempfile
import os

from extractor import process_pdf

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="PDF FILE EXTRACTION",
    page_icon="📄",
    layout="wide"
)

col1, col2 = st.columns([1, 8])

with col1:
    st.image("logo.jpg", width=120)

with col2:
    st.title("ISO DWG DETAILS EXTRACTOR")
    st.caption("Daewoo E&C - Mozambique LNG PJ")

st.markdown("---")

# ============================================
# Sidebar
# ============================================

st.sidebar.title("📂 Extracted PDF Files")
st.sidebar.markdown("---")
st.sidebar.write("### Uploaded PDFs")


# ============================================
# Upload PDFs
# ============================================

uploaded_files = st.file_uploader(
    "Select PDF Files",
    type="pdf",
    accept_multiple_files=True
)


# ============================================
# Sidebar File List
# ============================================


if uploaded_files:

    st.sidebar.header("📂 Uploaded PDFs")

    for pdf in uploaded_files:
        st.sidebar.write(f"📄 {pdf.name}")

    st.sidebar.markdown("---")



# ============================================
# Process PDFs
# ============================================

if uploaded_files:

    st.success(f"{len(uploaded_files)} PDF(s) selected.")

    col1, col2 = st.columns([3,1])

    with col1:
        extract = st.button(
        "Extract Drawing Register",
        use_container_width=True,
        type="primary"
    )

    with col2:
        clear = st.button(
        "🗑 Clear",
        use_container_width=True
    )

    if clear:
     st.rerun()

    if extract:

        dfs = []

        progress = st.progress(0)

        status = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):

            status.info(f"Processing {uploaded_file.name}")

            uploaded_file.seek(0)

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                tmp.write(uploaded_file.read())

                tmp_path = tmp.name

            try:
                df = process_pdf(
                    tmp_path,
                    original_name=uploaded_file.name
                )

                print(type(df))

                dfs.append(df)

            except Exception as e:
                st.exception(e)
                raise

            os.remove(tmp_path)

            progress.progress((i + 1) / len(uploaded_files))

        final_df = pd.concat(
            dfs,
            ignore_index=True
        )

        status.success("✅ Extraction Completed Successfully")

       
        # ============================================
        # Preview Table
        # ============================================

        st.subheader("📋 Extracted Drawing Register")

        st.dataframe(
            final_df,
            use_container_width=True
        )

        # ============================================
        # Download Excel
        # ============================================

        excel_name = "Extracted Data.xlsx"

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
        st.markdown("---")

        st.caption(
            """
            **ISO DWG DETAILS EXTRACTOR v1.0.0**

            Daewoo E&C – Mozambique LNG Project

            © 2026 All Rights Reserved
            """
        )