# Core app libraries
import streamlit as st
import pandas as pd
import plotly.express as px

# Project modules
from src.ai_classifier import classify_tool
from src.insights_generator import generate_executive_insights
from src.risk_scoring import calculate_scores
from src.semantic_overlap import detect_semantic_overlap, explain_overlap
from src.capability_graph import build_capability_graph, render_graph


# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="AI Sprawl Analyzer",
    page_icon="🤖",
    layout="wide",
)

st.title("AI Sprawl Analyzer")
st.caption("Enterprise AI governance and tool overlap analysis")


# --------------------------------------------------
# Load data
# --------------------------------------------------

uploaded_file = st.file_uploader("Upload AI tool inventory CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Uploaded CSV loaded successfully.")
else:
    df = pd.read_csv("data/sample_ai_tools.csv")
    st.info("Using sample AI tool inventory. Upload a CSV to analyze your own data.")


# --------------------------------------------------
# Inventory overview
# --------------------------------------------------

st.subheader("AI Tool Inventory")
st.dataframe(df, use_container_width=True)

total_spend = df["monthly_spend"].sum()
tool_count = len(df)
high_risk_count = len(df[df["data_risk"] == "High"])

col1, col2, col3 = st.columns(3)

col1.metric("Total Monthly Spend", f"${total_spend:,}")
col2.metric("Total AI Tools", tool_count)
col3.metric("High Risk Tools", high_risk_count)


# --------------------------------------------------
# Executive risk scorecard
# --------------------------------------------------

scores = calculate_scores(df)

st.subheader("Executive Risk Scorecard")

score_col1, score_col2, score_col3, score_col4 = st.columns(4)

score_col1.metric("Governance Risk Score", f"{scores['governance_risk_score']} / 100")
score_col2.metric("SSO Coverage", f"{scores['sso_coverage']}%")
score_col3.metric("High-Risk Tools", scores["high_risk_tools"])
score_col4.metric(
    "Est. Consolidation Opportunity",
    f"${scores['estimated_consolidation_opportunity']:,}/mo",
)


# --------------------------------------------------
# Governance review table
# --------------------------------------------------

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


# --------------------------------------------------
# Spend visualization
# --------------------------------------------------

st.subheader("Spend by Team")

team_spend = df.groupby("team")["monthly_spend"].sum().reset_index()

fig = px.bar(
    team_spend,
    x="team",
    y="monthly_spend",
    title="Monthly AI Spend by Team",
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Rule-based overlap examples
# --------------------------------------------------

st.subheader("Potential Capability Overlap")

overlap_categories = {
    "Content Generation": ["ChatGPT", "Jasper", "Gemini"],
    "Meeting Intelligence": ["Otter.ai", "Fireflies.ai"],
    "Research Assistants": ["Claude", "Perplexity", "ChatGPT"],
}

for category, tools in overlap_categories.items():
    st.markdown(f"### {category}")
    st.write(", ".join(tools))


# --------------------------------------------------
# Baseline governance recommendations
# --------------------------------------------------

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


# --------------------------------------------------
# AI-powered classification and executive insights
# --------------------------------------------------

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

            results.append(
                {
                    "tool": row["tool"],
                    "team": row["team"],
                    "monthly_spend": row["monthly_spend"],
                    **classification,
                }
            )

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
        title="Monthly Spend by AI Capability",
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


# --------------------------------------------------
# Semantic overlap detection using embeddings
# --------------------------------------------------

st.subheader("Semantic Overlap Detection")

similarity_threshold = st.slider(
    "Similarity threshold",
    min_value=0.50,
    max_value=0.95,
    value=0.60,
    step=0.01,
)

if st.button("Detect Semantic Overlap"):
    with st.spinner("Generating embeddings and comparing tool capabilities..."):
        overlap_records = detect_semantic_overlap(df, threshold=similarity_threshold)

    if overlap_records:
        overlap_df = pd.DataFrame(overlap_records)

        st.dataframe(overlap_df, use_container_width=True)

        st.subheader("Capability Relationship Graph")

        graph = build_capability_graph(df, overlap_records)
        fig_graph = render_graph(graph)

        st.pyplot(fig_graph)

        st.subheader("AI Overlap Explanations")

        for overlap in overlap_records:
            with st.expander(f"{overlap['tool_a']} ↔ {overlap['tool_b']}"):
                with st.spinner("Generating governance explanation..."):
                    explanation = explain_overlap(
                        overlap["tool_a"],
                        overlap["tool_b"],
                        overlap["purpose_a"],
                        overlap["purpose_b"],
                    )

                st.markdown(explanation)

    else:
        st.info("No semantic overlaps found at the selected threshold.")