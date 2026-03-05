"""
Streamlit UI for Media Diversity Watch
Submits a company name to the n8n webhook, which runs the full pipeline:
Railway agent → Notion report → Slack notification.
The webhook responds immediately (202) — report arrives in Notion in ~2 minutes.
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
st.info("The report will appear in Notion and a Slack notification will be sent when complete (~2 minutes).")

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
    with st.spinner(f"Submitting audit for {company}..."):
        try:
            response = requests.post(
                WEBHOOK_URL,
                json={"company": company, "focus": focus},
                timeout=30,
            )
            if response.status_code not in (200, 202):
                st.error(f"Unexpected response: {response.status_code}")
                st.stop()
        except requests.Timeout:
            st.error("Could not reach n8n. Check your workflow is active.")
            st.stop()
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
            st.stop()

    st.success(f"Audit queued for **{company}**. The report will appear in Notion in ~2 minutes and you will receive a Slack notification.")
