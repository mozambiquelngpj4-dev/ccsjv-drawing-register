import streamlit as st
import pandas as pd
import tempfile
import os
import time

from extractor import process_pdf


# ==========================================================
# APPLICATION VERSION
# ==========================================================

APP_VERSION = "1.1.5"


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="ISO DWG DETAILS EXTRACTOR",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


# ==========================================================
# MODERN CSS
# ==========================================================

st.markdown("""

<style>

.stApp{
    background:#F4F7FC;
}


/* HEADER */

.header{

    background:linear-gradient(135deg,#0F4C81,#1976D2);

    padding:30px;

    border-radius:20px;

    box-shadow:0px 8px 20px rgba(0,0,0,.15);

    margin-bottom:20px;

}


.title{

    color:#e8b346;

    font-size:48px;

    font-weight:700;

}


.subtitle{

    color:#EAF4FF;

    font-size:20px;

}



/* BUTTONS */

div.stButton>button{

    width:100%;

    height:55px;

    border-radius:12px;

    font-size:17px;

    font-weight:bold;

}


div.stDownloadButton>button{

    width:100%;

    height:55px;

    border-radius:12px;

    font-size:16px;

    font-weight:bold;

}



/* METRICS */

div[data-testid="stMetric"]{

    background:white;

    padding:20px;

    border-radius:15px;

    box-shadow:0px 4px 12px rgba(0,0,0,.08);

}



/* SIDEBAR */

[data-testid="stSidebar"]{

    background:#0B1F36;

}


[data-testid="stSidebar"] *{

    color:white;

}



</style>

""",
unsafe_allow_html=True
)



# ==========================================================
# HEADER
# ==========================================================


logo_col, title_col = st.columns([1,6])


with logo_col:

    st.image(
        "23.jpg",
        width=210
    )



with title_col:

    st.markdown(
    f"""

<div class="header">

<div class="title">
ISO DWG DETAILS EXTRACTOR
</div>


<div class="subtitle">
Engineering Drawing Register Extraction System
</div>


<div style="
margin-top:15px;
font-size:15px;
color:#DCEEFF;
">

📄 Multi PDF Processing |
⚙️ Automated Data Extraction |
📊 Drawing Register Generation

</div>


</div>

""",
unsafe_allow_html=True
)



st.markdown("---")



# ==========================================================
# SIDEBAR
# ==========================================================


st.sidebar.title("📂 PROJECT FILES")

st.sidebar.markdown("---")


st.sidebar.info(
"""
Upload one or more ISO drawing PDFs.

Supported:

• Standard PDF

• Multi-sheet Drawings

• OCR Processed PDFs

"""
)



# ==========================================================
# INFORMATION CARD
# ==========================================================


st.info(
"""

### 📄 Supported Drawings

✅ Standard exported PDF drawings

✅ Multi-sheet ISO drawings

✅ OCR processed drawings

⚠ Editable/vector PDFs may require OCR

"""
)



# ==========================================================
# FILE UPLOAD
# ==========================================================


st.subheader(
"📤 Upload ISO Drawings"
)


uploaded_files = st.file_uploader(

    "Choose one or more PDF files",

    type="pdf",

    accept_multiple_files=True,

    key=f"pdf_{st.session_state.uploader_key}"

)

# ==========================================================
# CHECK TOTAL UPLOAD SIZE
# ==========================================================

if uploaded_files:

    total_size = sum(pdf.size for pdf in uploaded_files)
    total_mb = total_size / (1024 * 1024)

    st.info(f"📦 Total upload size: {total_mb:.1f} MB")

    if total_mb > 200:

        st.error("❌ Total uploaded files exceed 200 MB.")

        st.stop()



# ==========================================================
# SIDEBAR FILE DISPLAY
# ==========================================================


if uploaded_files:


    st.sidebar.subheader(
        "📄 Uploaded PDFs"
    )


    for pdf in uploaded_files:

        st.sidebar.write(
            f"📄 {pdf.name}"
        )



# ==========================================================
# MAIN PROCESS
# ==========================================================


if uploaded_files:


    st.success(
        f"✅ {len(uploaded_files)} PDF(s) selected."
    )


    m1,m2,m3,m4 = st.columns(4)


    with m1:

        st.metric(
            "Uploaded PDFs",
            len(uploaded_files)
        )


    with m2:

        st.metric(
            "Status",
            "Ready"
        )


    with m3:

        st.metric(
            "Version",
            APP_VERSION
        )


    with m4:

        st.metric(
            "Engine",
            "PDF Parser"
        )



    st.markdown("")


    col1,col2 = st.columns([3,1])


    with col1:

        extract = st.button(
            "***Extract Drawing Register***",
            type="primary",
            use_container_width=True
        )


    with col2:

        clear = st.button(
            "🗑 CLEAR",
            use_container_width=True
        )



    if clear:

        st.session_state.uploader_key += 1

        st.rerun()



    if extract:


        start_time=time.time()


        dfs=[]


        progress=st.progress(0)

        status=st.empty()



        for index,uploaded_file in enumerate(uploaded_files):


            status.info(
            f"""
⚙️ Processing:

📄 {uploaded_file.name}

Progress:

{index+1}/{len(uploaded_files)}
"""
            )



            uploaded_file.seek(0)



            tmp_path=None


            try:


                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:


                    tmp.write(
                        uploaded_file.read()
                    )

                    tmp_path=tmp.name



                original_name=os.path.splitext(
                    uploaded_file.name
                )[0]



                df=process_pdf(
                    tmp_path,
                    original_name=original_name
                )



                if df is not None and not df.empty:

                    dfs.append(df)



            except Exception as e:


                st.error(
                    f"❌ {uploaded_file.name}: {e}"
                )



            finally:


                if tmp_path and os.path.exists(tmp_path):

                    os.remove(tmp_path)



            progress.progress(
                (index+1)/len(uploaded_files)
            )
            
        progress.empty()


        elapsed = time.time() - start_time



        if not dfs:

            st.error(
                "❌ No drawing data was extracted."
            )

            st.stop()



        status.success(
            "✅ Extraction Completed Successfully!"
        )



        # ==================================================
        # COMBINE DATA
        # ==================================================


        final_df = pd.concat(
            dfs,
            ignore_index=True
        )



        # ==================================================
        # FORMAT NPS COLUMN
        # ==================================================


        def format_nps(value):

            if pd.isna(value):

                return ""


            value=str(value).strip()


            if not value:

                return ""


            value=value.replace(
                '"',
                ""
            )


            if value.endswith(".0"):

                value=value[:-2]


            return value + '"'




        if "NPS(IN)" in final_df.columns:


            final_df["NPS(IN)"] = (

                final_df["NPS(IN)"]

                .apply(format_nps)

            )



        # ==================================================
        # EXPORT FILES
        # ==================================================


        excel_file=None


        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".xlsx"
        ) as tmp_excel:


            excel_file=tmp_excel.name



        final_df.to_excel(

            excel_file,

            index=False,

            engine="openpyxl"

        )



        csv_data = final_df.to_csv(
            index=False
        )



        st.markdown("---")


        st.subheader(
            "📋 Extracted Drawing Register"
        )



        download1,download2 = st.columns(2)



        with download1:


            with open(
                excel_file,
                "rb"
            ) as f:


                st.download_button(

                    label="📥 Download Excel",

                    data=f,

                    file_name="Extracted_Drawing_Register.xlsx",

                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                    use_container_width=True

                )




        with download2:


            st.download_button(

                label="📥 Download CSV",

                data=csv_data,

                file_name="CCSJV_Drawing_Register.csv",

                mime="text/csv",

                use_container_width=True

            )




        # ==================================================
        # DATA PREVIEW
        # ==================================================


        st.markdown("")


        with st.expander(

            "👁 Preview Extracted Data",

            expanded=True

        ):


            st.dataframe(

                final_df,

                use_container_width=True,

                hide_index=True,

                height=750

            )




        # ==================================================
        # SUMMARY DASHBOARD
        # ==================================================


        st.markdown("---")


        s1,s2,s3,s4 = st.columns(4)



        with s1:


            st.info(

            f"""
📄 **PDF Files**

{len(uploaded_files)}

"""
            )



        with s2:


            st.info(

            f"""
📑 **Records**

{len(final_df)}

"""
            )



        with s3:


            st.success(

            """
✅ **Status**

Completed

"""
            )



        with s4:


            st.info(

            f"""
⏱ **Time**

{elapsed:.1f}s

"""
            )




        # remove temporary Excel

        if os.path.exists(excel_file):

            os.remove(excel_file)



# ==========================================================
# FOOTER
# ==========================================================


st.markdown("---")


st.markdown(

f"""

<div style="
text-align:center;
padding:20px;
">


<h4 style="color:#0F4C81;">

🌏 ISO DWG DETAILS EXTRACTOR

</h4>


<p style="color:gray;">

Version <b>{APP_VERSION}</b>

</p>


<p style="color:gray;">

Developed by: <b>InFiniXity</b>

</p>

<p style="color:gray;">

Developed for: <b>Piping Department</b>

</p>


<p style="color:gray;">

© 2026 All Rights Reserved

</p>


</div>


""",

unsafe_allow_html=True

)            