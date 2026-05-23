
from src.ai_classifier import classify_tool
from src.insights_generator import generate_executive_insights
from src.risk_scoring import calculate_scores

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Sprawl Analyzer",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Sprawl Analyzer")
st.caption("Enterprise AI governance and tool overlap analysis")

uploaded_file = st.file_uploader("Upload AI tool inventory CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Uploaded CSV loaded successfully.")
else:
    df = pd.read_csv("data/sample_ai_tools.csv")
    st.info("Using sample AI tool inventory. Upload a CSV to analyze your own data.")

st.subheader("AI Tool Inventory")

st.dataframe(df, use_container_width=True)

total_spend = df["monthly_spend"].sum()
tool_count = len(df)
high_risk_count = len(df[df["data_risk"] == "High"])

col1, col2, col3 = st.columns(3)

col1.metric("Total Monthly Spend", f"${total_spend:,}")
col2.metric("Total AI Tools", tool_count)
col3.metric("High Risk Tools", high_risk_count)
scores = calculate_scores(df)

st.subheader("Executive Risk Scorecard")

score_col1, score_col2, score_col3, score_col4 = st.columns(4)

score_col1.metric(
    "Governance Risk Score",
    f"{scores['governance_risk_score']} / 100"
)

score_col2.metric(
    "SSO Coverage",
    f"{scores['sso_coverage']}%"
)

score_col3.metric(
    "High-Risk Tools",
    scores["high_risk_tools"]
)

score_col4.metric(
    "Est. Consolidation Opportunity",
    f"${scores['estimated_consolidation_opportunity']:,}/mo"
)

st.subheader("Tools Requiring Governance Review")

risk_df = df[
    (df["data_risk"] == "High") | (df["sso_enabled"] == "No")
].copy()

risk_df["review_reason"] = risk_df.apply(
    lambda row: ", ".join(
        [
            reason
            for reason in [
                "High data risk" if row["data_risk"] == "High" else None,
                "SSO not enabled" if row["sso_enabled"] == "No" else None,
            ]
            if reason
        ]
    ),
    axis=1,
)

st.dataframe(
    risk_df[
        ["tool", "team", "monthly_spend", "data_risk", "sso_enabled", "review_reason"]
    ],
    use_container_width=True,
)


st.subheader("Spend by Team")

team_spend = (
    df.groupby("team")["monthly_spend"]
    .sum()
    .reset_index()
)

fig = px.bar(
    team_spend,
    x="team",
    y="monthly_spend",
    title="Monthly AI Spend by Team"
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Potential Capability Overlap")

overlap_categories = {
    "Content Generation": ["ChatGPT", "Jasper", "Gemini"],
    "Meeting Intelligence": ["Otter.ai", "Fireflies.ai"],
    "Research Assistants": ["Claude", "Perplexity", "ChatGPT"],
}

for category, tools in overlap_categories.items():
    st.markdown(f"### {category}")
    st.write(", ".join(tools))

st.subheader("Governance Recommendations")

recommendations = [
    "Consolidate overlapping AI writing assistants",
    "Review non-SSO-enabled tools",
    "Implement centralized AI governance policy",
    "Establish approved AI vendor catalog",
    "Monitor high-risk tools handling sensitive data",
]

for rec in recommendations:
    st.write(f"- {rec}")


st.subheader("AI-Powered Tool Classification")

if st.button("Run AI Classification"):
    results = []
    with st.spinner("Classifying AI tools..."):
        for _, row in df.iterrows():
            classification = classify_tool(
                row["tool"],
                row["team"],
                row["purpose"],
                row["data_risk"],
                row["sso_enabled"],
            )

            results.append({
                "tool": row["tool"],
                "team": row["team"],
                "monthly_spend": row["monthly_spend"],
                **classification,
            })

    classified_df = pd.DataFrame(results)

    st.dataframe(classified_df, use_container_width=True)

    st.subheader("Capability Categories")
    category_spend = (
        classified_df.groupby("capability_category")["monthly_spend"]
        .sum()
        .reset_index()
    )

    fig2 = px.bar(
        category_spend,
        x="capability_category",
        y="monthly_spend",
        title="Monthly Spend by AI Capability"
    )

    st.plotly_chart(fig2, use_container_width=True)
    st.subheader("AI Executive Insights")
    with st.spinner("Generating executive insights..."):
   	 insights = generate_executive_insights(classified_df)
    st.markdown(insights)
    st.download_button(
    label="Download Executive Report",
    data=insights,
    file_name="ai_governance_report.md",
    mime="text/markdown",
    )