import streamlit as st
from anthropic import Anthropic
from gigachat import GigaChat
from ollama import Client as OllamaClient
from openai import OpenAI


@st.cache_data(ttl=300, show_spinner=False)
def check_openai(api_key: str, timeout: int = 5) -> tuple[bool, str]:
    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        client.models.list(limit=1)
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=300, show_spinner=False)
def check_anthropic(api_key: str, timeout: int = 5) -> tuple[bool, str]:
    try:
        client = Anthropic(api_key=api_key, timeout=timeout)
        client.models.list(limit=1)
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=300, show_spinner=False)
def check_gigachat(credentials: str, scope: str, verify_ssl: bool, timeout: int = 5) -> tuple[bool, str]:
    try:
        client = GigaChat(
            credentials=credentials,
            scope=scope,
            verify_ssl_certs=verify_ssl,
            timeout=timeout,
        )
        client.get_models()
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=300, show_spinner=False)
def check_ollama(base_url: str, timeout: int = 5) -> tuple[bool, str]:
    try:
        client = OllamaClient(host=base_url, timeout=timeout)
        client.list()
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=30, show_spinner=False)
def list_ollama_models(base_url: str, timeout: int = 5) -> list[str]:
    try:
        client = OllamaClient(host=base_url, timeout=timeout)
        response = client.list()
        return [m.model.split(":")[0] for m in response.models]
    except Exception:
        return []


def pull_ollama_model(base_url: str, model_name: str) -> tuple[bool, str]:
    try:
        client = OllamaClient(host=base_url)
        client.pull(model_name)
        return True, ""
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
