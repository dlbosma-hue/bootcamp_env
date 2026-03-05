"""
Streamlit UI for Media Diversity Watch
Submits a company name to the Railway API and displays the report.
"""

import requests
import streamlit as st

API_URL = "https://bootcampenv-production.up.railway.app/research"

COMPANIES = ["NPR", "The Guardian", "New York Times", "Al Jazeera English"]
COMMUNITIES = ["All Communities", "Women and Gender Equality", "LGBTQ+ Communities",
               "Racial and Ethnic Minorities", "People with Disabilities"]
FOCUS_MAP = {
    "All Communities": "all",
    "Women and Gender Equality": "women",
    "LGBTQ+ Communities": "lgbtq",
    "Racial and Ethnic Minorities": "race",
    "People with Disabilities": "disability",
}

st.set_page_config(page_title="Media Diversity Watch", page_icon="📊", layout="wide")

st.title("Media Diversity Watch")
st.caption("Autonomous inclusivity research agent — powered by LangGraph ReAct")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    company_option = st.selectbox("Media outlet", ["Custom..."] + COMPANIES)
    if company_option == "Custom...":
        company = st.text_input("Enter company name", placeholder="e.g. BBC News")
    else:
        company = company_option

with col2:
    focus_label = st.selectbox("Focus community", COMMUNITIES)
    focus = FOCUS_MAP[focus_label]

st.divider()

if st.button("Run Inclusivity Audit", type="primary", disabled=not company):
    with st.spinner(f"Researching {company}... this takes 1–2 minutes"):
        try:
            response = requests.post(
                API_URL,
                json={"company": company, "focus": focus},
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            st.error("Request timed out after 5 minutes. Try again.")
            st.stop()
        except requests.RequestException as e:
            st.error(f"API error: {e}")
            st.stop()

    st.success(f"Report complete — Overall Score: **{data['overall_score']}/10**")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Overall Score", f"{data['overall_score']}/10")
    with col_b:
        status = "Good Standing" if data["overall_score"] >= 7 else "Needs Review" if data["overall_score"] >= 4 else "Flagged"
        st.metric("Status", status)
    with col_c:
        st.metric("Date", data["date"])

    if data.get("summary"):
        st.info(data["summary"])

    if data.get("community_scores"):
        st.subheader("Community Scores")
        cols = st.columns(len(data["community_scores"]))
        for i, (community, score) in enumerate(data["community_scores"].items()):
            with cols[i]:
                st.metric(community, f"{score}/10")

    if data.get("harm_flags"):
        st.subheader("Harm Flags")
        for flag in data["harm_flags"]:
            st.warning(flag)

    st.subheader("Full Report")
    st.markdown(data["report_text"])
