"""Tests for openai-agents-scavio. The Scavio SDK client is mocked; no key or network used."""

import asyncio
import json

from agents.tool_context import ToolContext

import openai_agents_scavio.tools as tools_mod
from openai_agents_scavio import get_scavio_tools


class _Recorder:
    def __init__(self, calls):
        self._calls = calls

    def __getattr__(self, method):
        def _call(**kwargs):
            self._calls.append((method, kwargs))
            return {"ok": True, "method": method, "kwargs": kwargs}

        return _call


class _FakeClient:
    def __init__(self, *args, **kwargs):
        self.calls = []
        for ns in ("google", "amazon", "walmart", "youtube", "reddit", "tiktok", "instagram"):
            setattr(self, ns, _Recorder(self.calls))


def _build(monkeypatch, **kwargs):
    monkeypatch.setattr(tools_mod, "ScavioClient", _FakeClient)
    return get_scavio_tools(api_key="test", **kwargs)


def _invoke(tool, args: dict):
    ctx = ToolContext(context=None, tool_name=tool.name, tool_call_id="1", tool_arguments=json.dumps(args))
    return asyncio.run(tool.on_invoke_tool(ctx, json.dumps(args)))


def test_all_tools_register(monkeypatch):
    tools = _build(monkeypatch, all=True)
    names = [t.name for t in tools]
    assert len(names) == 47, names
    assert len(set(names)) == len(names)
    assert all(n.startswith("scavio_") for n in names)


def test_provider_gating(monkeypatch):
    tools = _build(
        monkeypatch,
        enable_google=False,
        enable_amazon=False,
        enable_walmart=False,
        enable_youtube=False,
        enable_reddit=True,
        enable_tiktok=False,
        enable_instagram=False,
    )
    assert {t.name for t in tools} == {"scavio_reddit_search", "scavio_reddit_post"}


def test_api_key_not_in_schema(monkeypatch):
    tools = _build(monkeypatch, enable_google=True, enable_amazon=False, enable_walmart=False,
                   enable_youtube=False, enable_reddit=False, enable_tiktok=False, enable_instagram=False)
    g = next(t for t in tools if t.name == "scavio_google_search")
    props = g.params_json_schema.get("properties", {})
    assert "query" in props
    assert "api_key" not in props and "client" not in props


def test_google_maps_v2_params(monkeypatch):
    tools = _build(monkeypatch, enable_google=True, enable_amazon=False, enable_walmart=False,
                   enable_youtube=False, enable_reddit=False, enable_tiktok=False, enable_instagram=False)
    g = next(t for t in tools if t.name == "scavio_google_search")
    # v1 params (country_code/language/page) are mapped to v2 (gl/hl/start); none dropped.
    out = _invoke(g, {"query": "ai agents", "country_code": "us", "language": "en", "page": 3, "device": "mobile", "nfpr": True})
    assert out["ok"] is True
    assert out["method"] == "search"
    assert out["kwargs"] == {"query": "ai agents", "gl": "us", "hl": "en", "device": "mobile", "nfpr": True, "start": 20}


def test_google_page_one_omits_start(monkeypatch):
    tools = _build(monkeypatch, enable_google=True, enable_amazon=False, enable_walmart=False,
                   enable_youtube=False, enable_reddit=False, enable_tiktok=False, enable_instagram=False)
    g = next(t for t in tools if t.name == "scavio_google_search")
    out = _invoke(g, {"query": "ai agents", "page": 1})
    assert out["kwargs"] == {"query": "ai agents"}


def test_google_drops_v1_only_params(monkeypatch):
    tools = _build(monkeypatch, enable_google=True, enable_amazon=False, enable_walmart=False,
                   enable_youtube=False, enable_reddit=False, enable_tiktok=False, enable_instagram=False)
    g = next(t for t in tools if t.name == "scavio_google_search")
    props = g.params_json_schema.get("properties", {})
    assert "search_type" not in props and "light_request" not in props
    assert {"query", "country_code", "language", "page", "device", "nfpr"} <= set(props)


def test_amazon_product_uses_asin(monkeypatch):
    tools = _build(monkeypatch, enable_amazon=True, enable_google=False, enable_walmart=False,
                   enable_youtube=False, enable_reddit=False, enable_tiktok=False, enable_instagram=False)
    p = next(t for t in tools if t.name == "scavio_amazon_product")
    out = _invoke(p, {"asin": "B000000000"})
    assert out["method"] == "product"
    assert out["kwargs"] == {"asin": "B000000000"}
