import uuid

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from src.settings import get_settings


def get_user_id() -> str:
    """Get or create persistent user_id stored in browser cookie."""
    if "_user_id" in st.session_state:
        return st.session_state._user_id

    settings = get_settings()
    storage_key = settings.user_storage_key

    # Read from cookie (survives page refresh, unlike streamlit_js_eval)
    user_id = st.context.cookies.get(storage_key)

    if user_id:
        st.session_state._user_id = user_id
        return user_id

    # New user — generate ID and set cookie via JS
    new_id = str(uuid.uuid4())
    max_age = settings.user_cookie_max_age_days * 86400
    streamlit_js_eval(
        js_expressions=f"document.cookie = '{storage_key}={new_id}; path=/; max-age={max_age}; SameSite=Lax'",
        key="_set_user_cookie",
    )
    st.session_state._user_id = new_id
    return new_id
