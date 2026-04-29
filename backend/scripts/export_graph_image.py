#!/usr/bin/env python3
"""
Export the Neo4j knowledge graph as a publication-quality image.

Produces three files next to this script:
  - graph_full.png   (PNG, 300 DPI, for inclusion in Word/LaTeX reports)
  - graph_full.svg   (SVG, vectorial, scales without pixelation)
  - graph_full.pdf   (PDF, for printed reports)

The layout is hierarchical (top = Modules, middle = Concepts, bottom = Resources).
Colors:
  - orange  = Module nodes
  - yellow  = Concept nodes
  - green   = Resource nodes
  - solid arrow   = COVERS
  - dashed arrow  = REQUIRES
  - dotted arrow  = REMEDIATES_TO

Usage:
  cd backend
  .\\venv\\Scripts\\activate
  pip install graphviz python-dotenv neo4j
  python scripts/export_graph_image.py
"""
import os
import sys

from dotenv import load_dotenv
from graphviz import Digraph
from neo4j import GraphDatabase

# Colors (accessible palette; print well in B&W too)
COLOR_MODULE = "#F4A261"    # warm orange
COLOR_CONCEPT = "#E9C46A"   # yellow
COLOR_RESOURCE = "#8AB17D"  # soft green


def fetch_graph(session):
    """Read all nodes and edges from Neo4j."""
    modules = session.run(
        "MATCH (m:Module) RETURN m.id AS id, m.name AS name ORDER BY m.id"
    ).data()
    concepts = session.run(
        "MATCH (c:Concept) RETURN c.id AS id, c.name AS name ORDER BY c.id"
    ).data()
    resources = session.run(
        "MATCH (r:Resource) "
        "RETURN r.id AS id, coalesce(r.title, r.name, r.id) AS name "
        "ORDER BY r.id"
    ).data()

    covers = session.run(
        "MATCH (m:Module)-[:COVERS]->(c:Concept) "
        "RETURN m.id AS src, c.id AS dst"
    ).data()
    requires = session.run(
        "MATCH (a:Concept)-[:REQUIRES]->(b:Concept) "
        "RETURN a.id AS src, b.id AS dst"
    ).data()
    remediates = session.run(
        "MATCH (c:Concept)-[:REMEDIATES_TO]->(r:Resource) "
        "RETURN c.id AS src, r.id AS dst"
    ).data()

    return modules, concepts, resources, covers, requires, remediates


def build_dot(modules, concepts, resources, covers, requires, remediates):
    """Build a Graphviz Digraph."""
    dot = Digraph("NumericalAnalysisKG", format="png")
    # Layout: top-down hierarchical with orthogonal (right-angle) edges
    dot.attr(
        rankdir="TB",        # Top to Bottom
        splines="ortho",     # clean right-angle edges
        nodesep="0.4",
        ranksep="1.0",
        bgcolor="white",
        fontname="Helvetica",
        fontsize="10",
    )
    dot.attr(
        "node",
        fontname="Helvetica",
        fontsize="10",
        style="filled,rounded",
        shape="box",
        margin="0.15,0.08",
    )
    dot.attr("edge", fontname="Helvetica", fontsize="8", arrowsize="0.7")

    # -- Modules (top rank) --
    with dot.subgraph(name="modules") as s:
        s.attr(rank="same")
        for m in modules:
            s.node(
                m["id"],
                label=m["name"],
                fillcolor=COLOR_MODULE,
                color="#D88C3F",
            )

    # -- Concepts (middle) --
    for c in concepts:
        dot.node(
            c["id"],
            label=c["name"],
            fillcolor=COLOR_CONCEPT,
            color="#C9A945",
        )

    # -- Resources (bottom rank) --
    with dot.subgraph(name="resources") as s:
        s.attr(rank="same")
        for r in resources:
            s.node(
                r["id"],
                label=r["name"],
                fillcolor=COLOR_RESOURCE,
                color="#6B9460",
            )

    # -- Edges --
    for e in covers:
        dot.edge(e["src"], e["dst"], label="COVERS",
                 color="#5A5A5A", style="solid")
    for e in requires:
        dot.edge(e["src"], e["dst"], label="REQUIRES",
                 color="#1F78B4", style="dashed", fontcolor="#1F78B4")
    for e in remediates:
        dot.edge(e["src"], e["dst"], label="REMEDIATES_TO",
                 color="#008856", style="dotted", fontcolor="#008856")

    return dot


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(here, "../../.env")
    load_dotenv(dotenv_path)

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        print("ERROR: NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD missing in .env")
        sys.exit(1)

    print(f"Connecting to {uri} as {user} ...")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        data = fetch_graph(session)
    driver.close()

    modules, concepts, resources, covers, requires, remediates = data
    print(
        f"Fetched {len(modules)} Modules, {len(concepts)} Concepts, "
        f"{len(resources)} Resources"
    )
    print(
        f"Fetched {len(covers)} COVERS, {len(requires)} REQUIRES, "
        f"{len(remediates)} REMEDIATES_TO"
    )

    dot = build_dot(modules, concepts, resources, covers, requires, remediates)

    out_base = os.path.join(here, "graph_full")
    # Render PNG (300 DPI for print quality)
    dot.attr(dpi="300")
    dot.render(out_base, format="png", cleanup=True)
    print(f"Wrote {out_base}.png")

    # Render SVG (vector — perfect for reports)
    dot.render(out_base, format="svg", cleanup=True)
    print(f"Wrote {out_base}.svg")

    # Render PDF
    dot.render(out_base, format="pdf", cleanup=True)
    print(f"Wrote {out_base}.pdf")


if __name__ == "__main__":
    main()
