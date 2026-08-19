from langgraph.graph import StateGraph, START, END

from state import HealthState

from stepcountnode import step_node
from screentimenode import screen_node
from foodorder import food_node

from database import dbsave

from finalanalyse import final_node
from pdfnode import pdf_node


# --------------------------------------------------
# Create graph
# --------------------------------------------------

builder = StateGraph(HealthState)


# --------------------------------------------------
# Add nodes
# --------------------------------------------------

builder.add_node("steps", step_node)

builder.add_node("screen", screen_node)

builder.add_node("food", food_node)

builder.add_node("dbsave", dbsave)

builder.add_node("final", final_node)

builder.add_node("pdf", pdf_node)


# --------------------------------------------------
# START → independent nodes
# --------------------------------------------------

builder.add_edge(
    START,
    "steps"
)

builder.add_edge(
    START,
    "screen"
)

builder.add_edge(
    START,
    "food"
)


# --------------------------------------------------
# Three nodes → database
# --------------------------------------------------

builder.add_edge(
    "steps",
    "dbsave"
)

builder.add_edge(
    "screen",
    "dbsave"
)

builder.add_edge(
    "food",
    "dbsave"
)


# --------------------------------------------------
# Database → final AI
# --------------------------------------------------

builder.add_edge(
    "dbsave",
    "final"
)


# --------------------------------------------------
# Final → PDF → END
# --------------------------------------------------

builder.add_edge(
    "final",
    "pdf"
)

builder.add_edge(
    "pdf",
    END
)


# --------------------------------------------------
# Compile graph
# --------------------------------------------------

graph = builder.compile()