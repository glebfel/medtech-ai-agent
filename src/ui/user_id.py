import uuid

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from src.settings import get_settings


def get_user_id() -> str:
    """Get or create persistent user_id stored in browser localStorage."""
    if "_user_id" in st.session_state:
        return st.session_state._user_id

    storage_key = get_settings().user_storage_key

    # Try reading from browser localStorage
    stored = streamlit_js_eval(
        js_expressions=f"localStorage.getItem('{storage_key}')",
        key="_read_user_id",
    )

    if stored:
        st.session_state._user_id = stored
        return stored

    # First visit — generate and save
    new_id = str(uuid.uuid4())
    streamlit_js_eval(
        js_expressions=f"localStorage.setItem('{storage_key}', '{new_id}')",
        key="_write_user_id",
    )
    st.session_state._user_id = new_id
    return new_id
