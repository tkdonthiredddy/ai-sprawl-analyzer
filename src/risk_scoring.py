def calculate_scores(df):
    total_tools = len(df)
    total_spend = df["monthly_spend"].sum()

    high_risk_tools = len(df[df["data_risk"] == "High"])
    non_sso_tools = len(df[df["sso_enabled"] == "No"])

    high_risk_score = (high_risk_tools / total_tools) * 40 if total_tools else 0
    non_sso_score = (non_sso_tools / total_tools) * 35 if total_tools else 0

    concentration_score = 0
    if total_spend > 0:
        top_tool_spend = df["monthly_spend"].max()
        concentration_score = (top_tool_spend / total_spend) * 25

    governance_risk_score = round(high_risk_score + non_sso_score + concentration_score)

    sso_coverage = round(
        (len(df[df["sso_enabled"] == "Yes"]) / total_tools) * 100
    ) if total_tools else 0

    estimated_consolidation_opportunity = round(total_spend * 0.15)

    return {
        "governance_risk_score": governance_risk_score,
        "sso_coverage": sso_coverage,
        "high_risk_tools": high_risk_tools,
        "non_sso_tools": non_sso_tools,
        "estimated_consolidation_opportunity": estimated_consolidation_opportunity,
    }