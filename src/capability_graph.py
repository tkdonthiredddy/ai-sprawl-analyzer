import networkx as nx
import matplotlib.pyplot as plt


def build_capability_graph(df, overlap_records):
    """Build a graph with all AI tools as nodes and semantic overlaps as edges."""

    graph = nx.Graph()

    # Add every tool from the inventory as a node,
    # even if it does not have a detected semantic overlap.
    for _, row in df.iterrows():
        graph.add_node(
            row["tool"],
            team=row["team"],
            monthly_spend=row["monthly_spend"],
            data_risk=row["data_risk"],
            sso_enabled=row["sso_enabled"],
        )

    # Add edges only for tools that crossed the semantic similarity threshold.
    for overlap in overlap_records:
        tool_a = overlap["tool_a"]
        tool_b = overlap["tool_b"]
        similarity = overlap["similarity"]

        graph.add_edge(
            tool_a,
            tool_b,
            weight=similarity,
            label=str(similarity),
        )

    return graph


def render_graph(graph):
    """Render the AI capability overlap graph."""

    fig, ax = plt.subplots(figsize=(12, 9))

    pos = nx.spring_layout(graph, seed=42, k=0.8)

    edge_weights = [
        graph[u][v]["weight"] * 4
        for u, v in graph.edges()
    ]

    edge_labels = {
        (u, v): graph[u][v]["label"]
        for u, v in graph.edges()
    }

    # Highlight connected tools slightly larger than isolated tools.
    node_sizes = [
        3200 if graph.degree(node) > 0 else 2200
        for node in graph.nodes()
    ]

    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=node_sizes,
        ax=ax,
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        font_size=9,
        ax=ax,
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        width=edge_weights,
        ax=ax,
    )

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=8,
        ax=ax,
    )

    ax.set_title("AI Capability Overlap Graph")
    ax.axis("off")

    return fig