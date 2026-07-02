import streamlit as st
import pandas as pd
import tempfile
import os

from extractor import process_pdf

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="ISO DWG DETAILS EXTRACTION",
    page_icon="🗂️",
    layout="wide"
)

if "show_table" not in st.session_state:
    st.session_state.show_table = False

st.markdown("""
<style>
.header{
    background:  
    padding:20px;
    border-radius:12px;
    margin-bottom:15px;
}
.title{
    color:#566D7E;
    font-size:65px;
    font-weight:bold;
}
.subtitle{
    color:#566D7E;
    font-size:25px;
}

.button{
    color:#657383;
    font-size:25px;
}

</style>
""", unsafe_allow_html=True)

col1,col2 =st.columns([1,6])

with col1:
    st.image("23.jpg", width=250)

with col2:
    st.markdown("""
    <div class="header">
        <div class="title">
            ISO DWG DETAILS EXTRACTOR
        </div>
        <div class="subtitle">
            PDF FILES - Details - Extract
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# Sidebar
# ============================================

st.sidebar.title("**EXTRACTED PDF FILES**")
st.sidebar.markdown("---")
#st.sidebar.write("### UPLOADED PDFs")


# ============================================
# Upload PDFs
# ============================================

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

st.info(
    """
    ℹ️ **Supported PDF Types**

    ✔ Standard exported PDF drawings – Fully supported

    ⚠ Editable/Vector PDF drawings – Some engineering details may not be extracted completely.
    """
)

st.subheader("📄 UPLOAD ISO DRAWINGS")

uploaded_files = st.file_uploader(
    "**Select PDF Files**",
    type="pdf",
    accept_multiple_files=True,
    key=f"pdf_uploader_{st.session_state.uploader_key}"
)



# ============================================
# Sidebar File List
# ============================================


if uploaded_files:

    st.sidebar.header("**UPLOADED PDFs**")

    for pdf in uploaded_files:
        st.sidebar.write(f"📄 {pdf.name}")
    st.sidebar.markdown("---")



# ============================================
# Process PDFs
# ============================================

if uploaded_files:

    st.success(f"{len(uploaded_files)} PDF(s) selected.")

    # ============================================
    # Dashboard Metrics
    # ============================================

    button1, button2, button3, button4 = st.columns([3,1,1,1])

    with button1:
        extract = st.button(
            "Extract Drawing Register",
            use_container_width=True,
            type="primary"
        )

    with button2:
        clear = st.button(
            "🗑 Clear",
            use_container_width=True
        )

    with button3:
        excel_placeholder = st.empty()

    with button4:
        csv_placeholder = st.empty()

    if clear:
        st.session_state.uploader_key += 1
        st.rerun()

    if extract:

        dfs = []

        progress = st.progress(0)
        status = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):

            percent = int(((i + 1) / len(uploaded_files)) * 100)

            status.markdown(f"""
            <div style="
            background:linear-gradient(135deg,#0B4F8C,#1565C0);
            padding:30px;
            border-radius:15px;
            box-shadow:0px 4px 12px rgba(0,0,0,0.25);
            text-align:center;
            color:white;
            margin-bottom:10px;
            ">

            <div style="font-size:48px;">
            ⚙️
            </div>

            <div style="
            font-size:28px;
            font-weight:bold;
            margin-top:10px;
            ">
            Extracting Drawing Register...
            </div>

            <div style="
            font-size:18px;
            margin-top:15px;
            color:#E3F2FD;
            ">
            📄 <b>{uploaded_file.name}</b>
            </div>

            <div style="
            font-size:16px;
            margin-top:10px;
            ">
            Processing <b>{i+1}</b> of <b>{len(uploaded_files)}</b> PDF(s)
            </div>

            <div style="
            font-size:22px;
            font-weight:bold;
            margin-top:10px;
            color:#FFD54F;
            ">
            {percent}% Complete
            </div>

            <div style="
            width:100%;
            background:#E3F2FD;
            border-radius:10px;
            height:18px;
            margin-top:20px;
            overflow:hidden;
            ">

            <div style="
            width:{percent}%;
            height:18px;
            background:#4CAF50;
            transition:width .4s;
            ">
            </div>

            </div>

            <div style="
            margin-top:20px;
            font-size:15px;
            color:#E3F2FD;
            ">
            Please wait while the ISO drawings are being analyzed...
            </div>

            </div>
            """, unsafe_allow_html=True)

            uploaded_file.seek(0)

            with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
            ) as tmp:

                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Process PDF
            df = process_pdf(
                tmp_path,
                original_name=uploaded_file.name
            )

            dfs.append(df)

            os.remove(tmp_path)

            progress.progress((i + 1) / len(uploaded_files))

        # ==========================================
        # After ALL PDFs are processed
        # ==========================================

        final_df = pd.concat(
            dfs,
            ignore_index=True
        )

        # Format NPS column
        if "NPS" in final_df.columns:
            final_df["NPS"] = (
            final_df["NPS"]
            .astype(str)
            .str.strip()
            .replace("nan", "")
            .apply(lambda x: f'{x}"' if x else "")
            )

        progress.empty()

        status.success("✅ Extraction Completed Successfully!")
      
        # ============================================
        # Preview Table
        # ============================================
        excel_name = "Extracted Data.xlsx"

        final_df.to_excel(
            excel_name,
            index=False,
            engine="openpyxl"
        )
        
        # Create CSV
        csv = final_df.to_csv(index=False)

        st.subheader("📋 Extracted Drawing Register")

        with open(excel_name, "rb") as f:
            excel_placeholder.download_button(
                "📥 Excel",
                data=f,
                file_name=excel_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        csv_placeholder.download_button(
            "📥 CSV",
            data=csv,
            file_name="CCSJV_Drawing_Register.csv",
            mime="text/csv",
            use_container_width=True
            )
            
        with st.expander("👁 View Table Preview", expanded=False):
            st.dataframe(
            final_df,
            use_container_width=True,
            hide_index=True
            )

        
        # ============================================
        # Preview Table
        # ============================================

        if st.session_state.show_table:
            st.dataframe(
                final_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("---")

        st.caption(
            """
            **ISO DWG DETAILS EXTRACTOR v1.1.4**
            
            Developed by: Piping Department

            Developed for: DAEWOO E & C

            © 2026 All Rights Reserved
            """
        )