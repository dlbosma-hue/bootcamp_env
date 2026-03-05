"""
Streamlit UI for Media Diversity Watch
Submits a company name to the n8n webhook, which runs the full pipeline:
Railway agent → Notion report → Slack notification.
"""

import requests
import streamlit as st

WEBHOOK_URL = "https://dlbosma.app.n8n.cloud/webhook/media-agent"

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
st.info("Reports are saved automatically to Notion and a Slack notification is sent on completion.")

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
                WEBHOOK_URL,
                json={"company": company, "focus": focus},
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            st.error("Request timed out after 5 minutes. Try again.")
            st.stop()
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
            st.stop()

    score = data.get("overall_score", "—")
    st.success(f"Audit complete for **{company}** — Score: **{score}/10**. Report saved to Notion.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Overall Score", f"{score}/10" if score != "—" else "—")
    with col_b:
        if score != "—":
            status = "Good Standing" if score >= 7 else "Needs Review" if score >= 4 else "Flagged"
            st.metric("Status", status)

    if data.get("summary"):
        st.info(data["summary"])
