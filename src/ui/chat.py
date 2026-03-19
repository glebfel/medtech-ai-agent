import pandas as pd
import streamlit as st
from langchain_core.messages import ToolMessage

from src.ui.charts import render_bmi_gauge
from src.ui.constants import TOOL_LABELS
from src.ui.parsers import parse_bmi, parse_icd10


def render_chat_history() -> None:
    """Render all stored messages with their visualizations."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                _render_assistant_message(msg)
            else:
                st.markdown(msg["content"])


def _render_assistant_message(msg: dict) -> None:
    """Render a single assistant message with optional charts/tables."""
    if msg.get("bmi_value"):
        render_bmi_gauge(msg["bmi_value"])
    if msg.get("icd10_data"):
        st.dataframe(pd.DataFrame(msg["icd10_data"]), use_container_width=True)
    if msg.get("tools_used"):
        labels = [TOOL_LABELS.get(t, t) for t in msg["tools_used"]]
        st.caption(f"Instruments: {', '.join(labels)}")
    st.markdown(msg["content"])


def process_response(result: dict) -> dict:
    """Parse agent result: render visualizations inline and return storable message dict."""
    tools_used = []
    bmi_value = None
    icd10_data = []

    for msg in result["messages"]:
        if not isinstance(msg, ToolMessage):
            continue

        tool_name = msg.name
        tools_used.append(tool_name)
        st.session_state.tool_usage[tool_name] = (
            st.session_state.tool_usage.get(tool_name, 0) + 1
        )

        if tool_name == "bmi_calculator":
            bmi_value = parse_bmi(msg.content)
            if bmi_value:
                render_bmi_gauge(bmi_value)

        elif tool_name == "icd10_search":
            icd10_data = parse_icd10(msg.content)
            if icd10_data:
                st.dataframe(pd.DataFrame(icd10_data), use_container_width=True)

    if tools_used:
        labels = [TOOL_LABELS.get(t, t) for t in tools_used]
        st.caption(f"Instruments: {', '.join(labels)}")

    ai_content = result["messages"][-1].content
    st.markdown(ai_content)

    return {
        "role": "assistant",
        "content": ai_content,
        "tools_used": tools_used,
        "bmi_value": bmi_value,
        "icd10_data": icd10_data,
    }
