import requests
import streamlit as st
from anthropic import Anthropic
from gigachat import GigaChat
from openai import OpenAI


@st.cache_data(ttl=300, show_spinner=False)
def check_openai(api_key: str) -> tuple[bool, str]:
    try:
        client = OpenAI(api_key=api_key, timeout=5)
        client.models.list(limit=1)
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=300, show_spinner=False)
def check_anthropic(api_key: str) -> tuple[bool, str]:
    try:
        client = Anthropic(api_key=api_key, timeout=5)
        client.models.list(limit=1)
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=300, show_spinner=False)
def check_gigachat(credentials: str, scope: str, verify_ssl: bool) -> tuple[bool, str]:
    try:
        client = GigaChat(
            credentials=credentials,
            scope=scope,
            verify_ssl_certs=verify_ssl,
            timeout=5,
        )
        client.get_models()
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=300, show_spinner=False)
def check_ollama(base_url: str) -> tuple[bool, str]:
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            return True, ""
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, _short_error(e)


def _short_error(e: Exception) -> str:
    msg = str(e)
    if "authentication" in msg.lower() or "401" in msg:
        return "Invalid API key"
    if "permission" in msg.lower() or "403" in msg:
        return "Access denied"
    if "timeout" in msg.lower() or "timed out" in msg.lower():
        return "Connection timeout"
    if "connect" in msg.lower():
        return "Connection failed"
    return msg[:80]
