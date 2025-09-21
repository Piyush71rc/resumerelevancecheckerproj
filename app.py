# app.py
import streamlit as st
from fpdf import FPDF
import io
import pandas as pd
from resume_parser import extract_text
from jd_parser import extract_skills_from_jd
from matcher import final_score
from db import create_tables, insert_evaluation, fetch_all_evaluations, clear_evaluations
import plotly.graph_objects as go
import plotly.express as px

# ===== Custom CSS for shifting UI up =====
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;   /* default ~6rem hota hai */
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.set_page_config(
    page_title="Automated Resume Relevance Checker",
    page_icon="📄",
    layout="wide",         # Make it full width, desktop-friendly
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* Headings */
    h1 { font-size:36px !important; color:#2E86C1; }
    h2 { font-size:28px !important; color:#117A65; }
    h3 { font-size:22px !important; }

    /* Body text */
    p, div, li { font-size:18px !important; }

    /* Metrics box */
    .stMetric { font-size:20px !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { font-size:18px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* General Styling */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        font-size: 18px;
        line-height: 1.6;
        word-wrap: break-word;
        white-space: normal !important;
    }

    /* Shift main content upwards */
    section.main > div {
        padding-top: 0px;
    }

    /* Headings */
    h1 { font-size: 36px !important; color: #2E86C1; }
    h2 { font-size: 28px !important; color: #117A65; }
    h3 { font-size: 22px !important; color: #B03A2E; }

    /* Metric boxes */
    .stMetric {
        font-size: 20px !important;
        background-color: #F8F9F9;
        border-radius: 12px;
        padding: 10px;
        margin: 5px 0;
        text-align: center;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        font-size: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Initialize DB
create_tables()

st.header("Automated Resume Relevance Checker")
# Tabs
tab1, tab2 = st.tabs(["Evaluate Resumes", "Dashboard"])


with tab1:

    # Uploads
    jd_file = st.file_uploader("Job Description (PDF/DOCX/TXT)", type=['pdf','docx','txt'])
    resume_files = st.file_uploader("Resumes (PDF/DOCX)", type=['pdf','docx'], accept_multiple_files=True)

    results_list = []

    if st.button("Evaluate Resumes") and jd_file and resume_files:
        # ✅ Extract JD text once
        jd_text = extract_text(jd_file, jd_file.name)
        if not jd_text:
            jd_text = ""

        # ✅ Extract JD skills once
        jd_skills = extract_skills_from_jd(jd_text, jd_file.name)
        if not jd_skills:
            jd_skills = []

        # ✅ Helper to flatten
        def flatten_list(skills):
            flat = []
            if isinstance(skills, list):
                for s in skills:
                    if isinstance(s, list):
                        flat.extend(s)
                    else:
                        flat.append(s)
            return flat

        # ✅ Loop resumes
        for rfile in resume_files:
            resume_text = extract_text(rfile, rfile.name)
            if not resume_text:
                resume_text = ""

            result = final_score(resume_text, jd_text, jd_skills)
            result["resume_name"] = rfile.name
            results_list.append(result)

            matched_flat = flatten_list(result['matched_skills'])
            missing_flat = flatten_list(result['missing_skills'])

            insert_evaluation(
                "Software Engineer",
                rfile.name,
                result['score'],
                result['verdict'],
                matched_flat,
                missing_flat
            )


            # ===== Plotly Pie Chart (Correct for Skills) =====
            matched_count = len(result['matched_skills'])
            missing_count = len(result['missing_skills'])

            fig = px.pie(
                values=[len(result['matched_skills']), len(result['missing_skills'])],
                names=['Matched', 'Missing'],
                title=f"Relevance: {rfile.name}",
                color_discrete_map={'Matched':'green', 'Missing':'red'}
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)


            # ===== LLM Feedback =====
            # feedback = generate_feedback(resume_text, jd_text, result['missing_skills'])
            # st.write(feedback)


with tab2:
    st.header("Placement Team Dashboard")

    if st.button("🗑️ Clear All Records"):
        clear_evaluations()
        st.success("All evaluation records deleted successfully! Please refresh tab to see changes.")

    rows = fetch_all_evaluations()
    
    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Job Title", "Candidate Name", "Score", "Verdict", "matched_flat", "missing_flat"])

        # ===== Sidebar Filters =====
        with st.sidebar:
            st.header("Dashboard Filters")
            job_filter = st.selectbox("Filter by Job Title", ["All"] + df["Job Title"].unique().tolist())
            verdict_filter = st.selectbox("Filter by Verdict", ["All"] + df["Verdict"].unique().tolist())
            filtered_df = df.copy()
            min_score = st.slider("Minimum Score Filter", min_value=0, max_value=100, value=0)
            filtered_df = filtered_df[filtered_df["Score"] >= min_score]
            top_n = st.slider("Select Top N Resumes to Display", min_value=1, max_value=10, value=5)
        
        # ===== Skill Gap Horizontal Bar Chart =====
        # Collect missing skills counts
        skill_counts = {}
        for ms in filtered_df["missing_flat"]:
            for skill in ms.split(', '):
                skill_counts[skill.strip()] = skill_counts.get(skill.strip(), 0) + 1  # strip spaces

        # Plotly horizontal bar chart

        
        # if skill_counts:
        #     df_skills = pd.DataFrame({
        #         "Skill": list(skill_counts.keys()),
        #         "Count": list(skill_counts.values())
        #     }).sort_values("Count", ascending=True)

        #     fig = px.bar(
        #         x=10,
        #         y=6,
        #         orientation="h",
        #         text=10,
        #         title="Missing Skills Distribution",
        #         color="red",
        #         color_continuous_scale="reds",
        #         template="plotly_white"
        #     )

        #     fig.update_traces(textposition="outside")
        #     fig.update_layout(
        #         xaxis_title="Number of Resumes Missing Skill",
        #         yaxis_title="Skill",
        #         title_x=0.5,
        #         margin=dict(l=120, r=40, t=80, b=40)
        #     )
        #     fig.update_layout(height=300, margin=dict(l=40, r=40, t=40, b=40))
        #     st.plotly_chart(fig, use_container_width=True)
        # else:
        #     st.info("✅ No missing skills for this batch!")



        # ===== Apply Filters =====
        if job_filter != "All":
            filtered_df = filtered_df[filtered_df["Job Title"] == job_filter]
        if verdict_filter != "All":
            filtered_df = filtered_df[filtered_df["Verdict"] == verdict_filter]
        
        # ===== Top N resumes =====
        filtered_df = filtered_df.sort_values(by="Score", ascending=False)
        top_resumes = filtered_df.head(top_n)

        def plot_verdict_chart(filtered_df):
            verdict_df = filtered_df["Verdict"].value_counts().reset_index()
            verdict_df.columns = ["Verdict", "Count"]

            fig = px.bar(
                verdict_df,
                x="Verdict",
                y="Count",
                color="Verdict",
                text="Count",
                title="Verdict Distribution",
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            # Make bars thinner + text outside
            fig.update_traces(textposition="outside", width=0.4)

            fig.update_layout(
                title_x=0.3,
                xaxis_title="",
                yaxis_title="Number of Resumes",
                showlegend=False,
                height=300,        # compact height
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

        plot_verdict_chart(filtered_df)


        # ===== Batch Summary =====
        st.subheader("Batch Summary")
        total_resumes = len(filtered_df)
        avg_score = round(filtered_df["Score"].mean(), 2)
        col1, col2 = st.columns(2)

        with col1:
            fig_total = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = total_resumes,
                title={'text': "Total Resumes", 'font': {'size':18}},
                number={'font': {'size':42}},
                gauge={'axis': {'range':[0, max(50,total_resumes+5)]},
                    'bar': {'color':'teal'},
                    'bgcolor':'lightgray'},
                domain={'x':[0,0.9], 'y':[0,0.8]}   # full domain
            ))
            fig_total.update_layout(height=250, margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_total, use_container_width=True)

        with col2:
            fig_avg = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_score,
                title={'text': "Average Score", 'font': {'size':18}},
                number={'font': {'size':42}},
                gauge={'axis': {'range':[0,100]},
                    'bar': {'color':'orange'},
                    'bgcolor':'lightgray'},
                domain={'x':[0,0.9], 'y':[0,0.8]}  # full domain
            ))
            fig_avg.update_layout(height=250, margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_avg, use_container_width=True)


        # ===== Colored Score Function =====
        def score_color(score):
            if score >= 75: return '🟢'
            elif score >= 50: return '🟡'
            else: return '🔴'

        # ===== Top N Highlight (Cards Layout) =====

        st.subheader(f"Top {top_n} Resumes")
        cols = st.columns([1]*min(top_n,4))

        for i, (idx, res) in enumerate(top_resumes.iterrows()):
            # resume_file_path = f"sample_data/{res['Candidate Name']}"
            # with open(resume_file_path, "rb") as f:
            #     pdf_bytes = f.read()
            
            with cols[i % 4]:
                # Card
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(145deg, #0f2c54, #1a3d7c);
                        padding:20px;
                        border-radius:20px;
                        border:2px solid #26466d;
                        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
                        height:150px;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        text-align:center;
                    ">
                        <p style='font-size:16px; font-weight:bold; color:#ffffff; margin:0'>{res['Candidate Name']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Score & Verdict
                st.markdown(
                    f"""
                    <div style='text-align:center; margin-top:5px'>
                        <p style='font-size:14px; font-weight:bold; color:#00e676; margin:2px'>Score: {res['Score']}</p>
                        <p style='font-size:13px; color:#f0f0f0; margin:2px'>Verdict: {res['Verdict']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Centered Download Button
                col1, col2, col3 = st.columns([1,2,1])
                # with col2:
                #     st.download_button(
                #         label="Open Resume",
                #         data=pdf_bytes,
                #         file_name=res['Candidate Name'],
                #         mime="application/pdf",
                #         key=f"download_{i}"
                #     )




        # ===== Download CSV =====
        



        # PDF buffer ready for download only
        csv = filtered_df.to_csv(index=False).encode("utf-8")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="evaluations.csv",
                mime="text/csv"
            )

        
    else:
        st.write("⚠️ No evaluations found yet. Please upload resumes first.")
