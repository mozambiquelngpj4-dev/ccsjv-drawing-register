import streamlit as st
import pandas as pd
import tempfile
import os

from extractor import process_pdf

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="CCSJV Drawing Register",
    page_icon="📄",
    layout="wide"
)

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

    if st.button("🚀 Extract Drawing Register"):

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

        status.success("✅ Extraction Completed Successfully")

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
        # Extraction Quality
        # ============================================

        total_sheets = len(final_df)

        required_fields = [
            "Drawing No",
            "Line No",
            "PID No"
        ]

        complete_rows = (
            final_df[required_fields]
            .replace("", pd.NA)
            .dropna()
            .shape[0]
        )

        success_rate = (
            complete_rows / total_sheets * 100
            if total_sheets else 0
        )

        duplicate_drawings = (
            final_df["Drawing No"]
            .loc[final_df["Drawing No"] != ""]
            .duplicated()
            .sum()
        )

        st.subheader("📊 Extraction Quality")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Success Rate",
            f"{success_rate:.1f}%"
        )

        c2.metric(
            "Missing Drawing No",
            final_df["Drawing No"].eq("").sum()
        )

        c3.metric(
            "Missing Line No",
            final_df["Line No"].eq("").sum()
        )

        c4.metric(
            "Duplicate Drawings",
            duplicate_drawings
        )

        st.markdown("---")

        # ============================================
        # Missing Information
        # ============================================

        st.subheader("⚠ Missing Information")

        missing_summary = pd.DataFrame({

            "Field": [
                "Drawing No",
                "CCSJV DWG",
                "Line No",
                "PID No",
                "Revision",
                "NPS(IN)",
                "LINE CLASS"
            ],

            "Missing": [
                final_df["Drawing No"].eq("").sum(),
                final_df["CCSJV DWG"].eq("").sum(),
                final_df["Line No"].eq("").sum(),
                final_df["PID No"].eq("").sum(),
                final_df["Revision"].eq("").sum(),
                final_df["NPS(IN)"].eq("").sum(),
                final_df["LINE CLASS"].eq("").sum()
            ]
        })

        st.dataframe(
            missing_summary,
            use_container_width=True
        )

        duplicates = final_df[
            final_df.duplicated(
                "Drawing No",
                keep=False
            ) &
            (final_df["Drawing No"] != "")
        ]

        if not duplicates.empty:

            st.warning("Duplicate Drawing Numbers Found")

            st.dataframe(
                duplicates,
                use_container_width=True
            )

        st.markdown("---")

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