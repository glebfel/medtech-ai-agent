import streamlit as st
from anthropic import Anthropic
from gigachat import GigaChat
from ollama import Client as OllamaClient
from openai import OpenAI


@st.cache_data(ttl=300, show_spinner=False)
def check_openai(api_key: str, timeout: int = 5) -> tuple[bool, str]:
    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        client.models.list()
        return True, ""
    except Exception as e:
        return False, _short_error(e)


@st.cache_data(ttl=300, show_spinner=False)
def check_anthropic(api_key: str, timeout: int = 5) -> tuple[bool, str]:
    try:
        client = Anthropic(api_key=api_key, timeout=timeout)
        client.models.list()
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
def list_ollama_models(base_url: str, timeout: int = 5) -> list[dict]:
    try:
        client = OllamaClient(host=base_url, timeout=timeout)
        response = client.list()
        results = []
        for m in response.models:
            try:
                info = client.show(m.model)
                template = getattr(info, "template", "") or ""
                supports_tools = "tools" in template.lower()
            except Exception:
                supports_tools = False
            results.append({
                "name": m.model.split(":")[0],
                "size_gb": round(m.size / 1_073_741_824, 1),
                "params": m.details.parameter_size if m.details else "",
                "tools": supports_tools,
            })
        return results
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def list_openai_models(api_key: str, timeout: int = 5) -> list[str]:
    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        models = client.models.list()
        excluded = {"instruct", "realtime", "codex", "audio", "search", "embed", "image", "nano"}
        return sorted([
            m.id for m in models
            if m.id.startswith("gpt-")
            and not any(ex in m.id for ex in excluded)
        ], reverse=True)
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def list_anthropic_models(api_key: str, timeout: int = 5) -> list[str]:
    try:
        client = Anthropic(api_key=api_key, timeout=timeout)
        models = client.models.list(limit=20)
        return [m.id for m in models.data]
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def list_gigachat_models(credentials: str, scope: str, verify_ssl: bool, timeout: int = 5) -> list[str]:
    try:
        client = GigaChat(
            credentials=credentials,
            scope=scope,
            verify_ssl_certs=verify_ssl,
            timeout=timeout,
        )
        models = client.get_models()
        return [m.id for m in models.data]
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
    if "not_found" in msg.lower() or "404" in msg:
        return "Model not found"
    # Sanitize: don't leak API keys or internal details
    safe = msg.split("\n")[0][:80]
    if "sk-" in safe or "key" in safe.lower():
        return "Provider error"
    return safe
