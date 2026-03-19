import pandas as pd
import streamlit as st
from langchain_core.messages import ToolMessage

from src.services.chat_session import rename_session
from src.ui.charts import render_bmi_gauge
from src.ui.constants import TOOL_LABELS
from src.ui.parsers import parse_bmi, parse_icd10


def render_title_editor() -> None:
    current_title = st.session_state.get("_current_title", "")
    if not current_title:
        return

    new_title = st.text_input(
        "Chat title",
        value=current_title,
        key="_title_input",
        label_visibility="collapsed",
    )
    if new_title != current_title:
        st.session_state._current_title = new_title
        rename_session(thread_id=st.session_state.thread_id, title=new_title)


def render_chat_history() -> None:
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                _render_assistant_message(msg, idx=idx)
            else:
                st.markdown(msg["content"])


def _render_assistant_message(msg: dict, idx: int = 0) -> None:
    if msg.get("bmi_value"):
        render_bmi_gauge(msg["bmi_value"], key=f"bmi_history_{idx}")
    if msg.get("icd10_data"):
        st.dataframe(pd.DataFrame(msg["icd10_data"]), use_container_width=True, key=f"icd10_history_{idx}")
    if msg.get("tools_used"):
        labels = [TOOL_LABELS.get(t, t) for t in msg["tools_used"]]
        st.caption(f"Instruments: {', '.join(labels)}")
    st.markdown(msg["content"])


def process_response(result: dict) -> dict:
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
                render_bmi_gauge(bmi_value, key="bmi_current")

        elif tool_name == "icd10_search":
            icd10_data = parse_icd10(msg.content)
            if icd10_data:
                st.dataframe(pd.DataFrame(icd10_data), use_container_width=True, key="icd10_current")

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
