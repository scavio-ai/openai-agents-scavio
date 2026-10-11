"""Tests for openai-agents-scavio. The Scavio SDK client is mocked; no key or network used."""

import asyncio
import inspect
import json

from agents.tool_context import ToolContext

import openai_agents_scavio.tools as tools_mod
from openai_agents_scavio import get_scavio_tools

TOTAL_TOOLS = 193

# Tool counts per enable_* flag. The sum is the whole surface, so a platform added
# without a count here (or a count left stale) fails test_all_tools_register.
PLATFORM_COUNTS = {
    "google": 14,
    "amazon": 3,
    "walmart": 7,
    "youtube": 15,
    "reddit": 12,
    "tiktok": 11,
    "tiktok_shop": 8,
    "instagram": 12,
    "x": 11,
    "linkedin": 9,
    "threads": 6,
    "kuaishou": 14,
    "ebay": 3,
    "target": 4,
    "home_depot": 3,
    "zillow": 3,
    "booking": 3,
    "tripadvisor": 4,
    "indeed": 4,
    "airbnb": 3,
    "glassdoor": 4,
    "yelp": 3,
    "app_store": 3,
    "google_play": 3,
    "sec": 6,
    "redfin": 3,
    "companies_house": 4,
    "g2": 3,
    "capterra": 3,
    "google_ads": 3,
    "meta_ads": 3,
    "extract": 1,
    "crawl": 5,
}


class _Recorder:
    """Stands in for one SDK namespace, recording (namespace, method, kwargs)."""

    def __init__(self, ns, calls):
        self._ns = ns
        self._calls = calls

    def __getattr__(self, method):
        def _call(**kwargs):
            self._calls.append((self._ns, method, kwargs))
            return {"ok": True, "namespace": self._ns, "method": method, "kwargs": kwargs}

        return _call


class _FakeExtract(_Recorder):
    def __call__(self, **kwargs):
        self._calls.append((None, "extract", kwargs))
        return {"ok": True, "namespace": None, "method": "extract", "kwargs": kwargs}


class _FakeClient:
    """Every namespace resolves lazily, so a new platform needs no test change."""

    def __init__(self, *args, **kwargs):
        self.calls = []

    @property
    def extract(self):
        # client.extract is a CALLABLE namespace (scavio>=0.23): calling it reads
        # one page (recorded with namespace None), and its attributes are the
        # website operations (map, crawl, crawl_status, batch, batch_status).
        return _FakeExtract("extract", self.calls)

    def __getattr__(self, ns):
        return _Recorder(ns, self.calls)


def _flags():
    return [
        name
        for name in inspect.signature(get_scavio_tools).parameters
        if name.startswith("enable_")
    ]


def _build(monkeypatch, **kwargs):
    monkeypatch.setattr(tools_mod, "ScavioClient", _FakeClient)
    return get_scavio_tools(api_key="test", **kwargs)


def _only(monkeypatch, *platforms):
    """Build with exactly these platforms enabled, whatever else exists."""
    wanted = {"enable_" + p for p in platforms}
    kwargs = {flag: flag in wanted for flag in _flags()}
    return _build(monkeypatch, **kwargs)


def _invoke(tool, args: dict):
    ctx = ToolContext(context=None, tool_name=tool.name, tool_call_id="1", tool_arguments=json.dumps(args))
    return asyncio.run(tool.on_invoke_tool(ctx, json.dumps(args)))


def _props(tool):
    return tool.params_json_schema.get("properties", {})


def _enum(prop):
    """Allowed values of a property. Optional ones arrive as anyOf[enum, null]."""
    if "enum" in prop:
        return prop["enum"]
    for branch in prop.get("anyOf", []):
        if "enum" in branch:
            return branch["enum"]
    return None


def test_all_tools_register(monkeypatch):
    tools = _build(monkeypatch, all=True)
    names = [t.name for t in tools]
    assert len(names) == TOTAL_TOOLS, len(names)
    assert len(set(names)) == len(names)
    assert all(n.startswith("scavio_") for n in names)
    # /youtube/metadata is a deprecated alias of /youtube/video; only /video ships.
    assert "scavio_youtube_video" in names
    assert "scavio_youtube_metadata" not in names
    # The five LinkedIn endpoints the provider withdrew return 410 and are not tools.
    for dead in ("scavio_linkedin_person_contact", "scavio_linkedin_company_people",
                 "scavio_linkedin_company_jobs", "scavio_linkedin_search_people",
                 "scavio_linkedin_search_posts"):
        assert dead not in names, dead


def test_every_flag_has_a_declared_count(monkeypatch):
    assert {f[len("enable_"):] for f in _flags()} == set(PLATFORM_COUNTS)
    assert sum(PLATFORM_COUNTS.values()) == TOTAL_TOOLS


def test_each_platform_registers_its_own_tools_only(monkeypatch):
    for platform, count in PLATFORM_COUNTS.items():
        tools = _only(monkeypatch, platform)
        assert len(tools) == count, (platform, len(tools), count)


def test_provider_gating(monkeypatch):
    names = {t.name for t in _only(monkeypatch, "reddit")}
    assert names == {
        "scavio_reddit_search",
        "scavio_reddit_search_suggestions",
        "scavio_reddit_post",
        "scavio_reddit_post_comments",
        "scavio_reddit_comment_replies",
        "scavio_reddit_subreddit",
        "scavio_reddit_subreddit_posts",
        "scavio_reddit_user",
        "scavio_reddit_user_posts",
        "scavio_reddit_user_comments",
        "scavio_reddit_popular",
        "scavio_reddit_trending",
    }, sorted(names)


def test_api_key_not_in_schema(monkeypatch):
    g = next(t for t in _only(monkeypatch, "google") if t.name == "scavio_google_search")
    props = _props(g)
    assert "query" in props
    assert "api_key" not in props and "client" not in props


def test_google_maps_v2_params(monkeypatch):
    g = next(t for t in _only(monkeypatch, "google") if t.name == "scavio_google_search")
    # v2 params are exposed natively. The v1 names are gone rather than mapped:
    # start is a 0-based result offset, not a 1-based page, so a silent remap
    # would have fetched the wrong page.
    out = _invoke(g, {"query": "ai agents", "gl": "us", "hl": "en", "start": 20, "device": "mobile", "nfpr": True})
    assert out["ok"] is True
    assert out["method"] == "search"
    assert out["kwargs"] == {"query": "ai agents", "gl": "us", "hl": "en", "device": "mobile", "nfpr": True, "start": 20}


def test_google_ignores_dead_v1_page_param(monkeypatch):
    g = next(t for t in _only(monkeypatch, "google") if t.name == "scavio_google_search")
    # `page` is not in the schema any more; passing it must not reach the wire.
    out = _invoke(g, {"query": "ai agents", "page": 1})
    assert out["kwargs"] == {"query": "ai agents"}


def test_google_drops_v1_only_params(monkeypatch):
    g = next(t for t in _only(monkeypatch, "google") if t.name == "scavio_google_search")
    props = _props(g)
    # v1 vocabulary is absent entirely - /api/v1/google returns 410 as of 2026-08-04.
    for dead in ("search_type", "light_request", "country_code", "language", "page"):
        assert dead not in props, dead
    assert {"query", "gl", "hl", "start", "device", "nfpr"} <= set(props)


def test_reddit_search_has_no_phantom_filters(monkeypatch):
    s = next(t for t in _only(monkeypatch, "reddit") if t.name == "scavio_reddit_search")
    props = _props(s)
    # The API reads query and cursor only; type/sort were stripped on the wire.
    assert set(props) == {"query", "cursor"}
    out = _invoke(s, {"query": "serpapi alternative", "cursor": "abc"})
    assert out["kwargs"] == {"query": "serpapi alternative", "cursor": "abc"}


def test_amazon_product_uses_asin(monkeypatch):
    p = next(t for t in _only(monkeypatch, "amazon") if t.name == "scavio_amazon_product")
    out = _invoke(p, {"asin": "B000000000"})
    assert out["method"] == "product"
    assert out["kwargs"] == {"asin": "B000000000"}


def test_walmart_retired_params_are_gone(monkeypatch):
    tools = {t.name: t for t in _only(monkeypatch, "walmart")}
    assert set(tools) == {
        "scavio_walmart_search",
        "scavio_walmart_product",
        "scavio_walmart_reviews",
        "scavio_walmart_category",
        "scavio_walmart_offers",
        "scavio_walmart_seller",
        "scavio_walmart_seller_products",
    }
    search = _props(tools["scavio_walmart_search"])
    # device / delivery_zip / store_id were retired: the API answers 200 with a
    # warnings[] array rather than an error, so a stale schema fails silently.
    for dead in ("device", "delivery_zip", "store_id", "start_page"):
        assert dead not in search, dead
    # domain was NOT retired - it is the price-bearing param.
    assert _enum(search["domain"]) == ["com", "ca", "com.mx"]
    assert "page" in search
    # product is US-only; walmart.ca product pages cannot be fetched at all.
    assert set(_props(tools["scavio_walmart_product"])) == {"product_id"}
    # seller-products is ~40 server-rendered items: no page param exists.
    assert "page" not in _props(tools["scavio_walmart_seller_products"])


def test_body_priced_surfaces_never_claim_a_flat_cost(monkeypatch):
    tools = {t.name: t for t in _build(monkeypatch, all=True)}
    # walmart search/category are 1 credit on com/ca and 2 on com.mx.
    for name in ("scavio_walmart_search", "scavio_walmart_category"):
        d = tools[name].description
        assert "com.mx" in d and "2 credit" in d, d
    # threads is 2 credits by user_id and 4 by username.
    d = tools["scavio_threads_profile"].description
    assert "user_id" in d and "4" in d, d
    # extract is tier-priced by mode.
    d = tools["scavio_extract"].description
    assert "ultra" in d and "mode" in d, d


def test_extract_is_a_top_level_method(monkeypatch):
    tools = _only(monkeypatch, "extract")
    assert [t.name for t in tools] == ["scavio_extract"]
    out = _invoke(tools[0], {"url": "https://example.com/pricing", "format": "text", "mode": "ultra"})
    # namespace None proves client.extract(...) was called, not client.extract.extract(...).
    assert out["namespace"] is None
    assert out["method"] == "extract"
    assert out["kwargs"] == {"url": "https://example.com/pricing", "format": "text", "mode": "ultra"}


def test_meta_ads_uses_the_meta_ads_namespace(monkeypatch):
    tools = {t.name: t for t in _only(monkeypatch, "meta_ads")}
    assert set(tools) == {"scavio_meta_ads_search", "scavio_meta_ads_advertiser", "scavio_meta_ads_ad"}
    # The route key is metaads and the path is /api/v1/meta-ads/* - the SDK owns
    # that mapping, and the tool must go through the meta_ads namespace to get it.
    out = _invoke(tools["scavio_meta_ads_search"], {"query": "crm software"})
    assert (out["namespace"], out["method"]) == ("meta_ads", "search")


def test_kuaishou_states_its_per_endpoint_price(monkeypatch):
    tools = {t.name: t for t in _only(monkeypatch, "kuaishou")}
    assert len(tools) == 14
    # Kuaishou is priced per endpoint (1, 2, 10 or 40), never per platform.
    assert "10 credits" in tools["scavio_kuaishou_profile"].description
    assert "credit" in tools["scavio_kuaishou_search"].description


def test_lookup_first_platforms_ship_their_resolver(monkeypatch):
    names = {t.name for t in _build(monkeypatch, all=True)}
    for resolver in ("scavio_sec_lookup", "scavio_tripadvisor_locations",
                     "scavio_glassdoor_companies", "scavio_google_ads_advertisers",
                     "scavio_companies_house_search"):
        assert resolver in names, resolver


def test_enum_params_expose_their_values(monkeypatch):
    e = next(t for t in _only(monkeypatch, "extract") if t.name == "scavio_extract")
    props = _props(e)
    assert _enum(props["mode"]) == ["normal", "advanced", "ultra"]
    assert _enum(props["format"]) == ["html", "markdown", "text"]


# --------------------------------------------------------------------------- #
# Map, crawl and batch (enable_crawl, opt-in)
# --------------------------------------------------------------------------- #

JOB_ID = "crawl_01a12d21-fb42-7000-88cf-6887f653ee5d"


class _JobClient(_FakeClient):
    """Crawl/batch jobs that move through scripted statuses."""

    def __init__(self, statuses=("running", "completed")):
        super().__init__()
        self._script = iter(statuses)
        calls = self.calls
        script = self._script

        class _Ext(_FakeExtract):
            def crawl(self, **kwargs):
                calls.append(("extract", "crawl", kwargs))
                return {"data": {"id": JOB_ID, "status": "queued"}, "credits_used": 0}

            def batch(self, **kwargs):
                calls.append(("extract", "batch", kwargs))
                return {"data": {"id": JOB_ID, "status": "queued"}, "credits_used": 0}

            def crawl_status(self, **kwargs):
                calls.append(("extract", "crawl_status", kwargs))
                return {"data": {"id": kwargs["job_id"], "status": next(script, "completed"), "results": []}}

            def batch_status(self, **kwargs):
                calls.append(("extract", "batch_status", kwargs))
                return {"data": {"id": kwargs["job_id"], "status": next(script, "completed"), "results": []}}

        self._ext = _Ext("extract", calls)

    @property
    def extract(self):
        return self._ext


def _crawl_tools(monkeypatch, client):
    monkeypatch.setattr(tools_mod, "ScavioClient", lambda *a, **k: client)
    monkeypatch.setattr(tools_mod, "WEB_JOB_POLL_INTERVAL", 0.0)
    wanted = {"enable_crawl"}
    tools = get_scavio_tools(api_key="test", **{f: f in wanted for f in _flags()})
    return {t.name: t for t in tools}


def test_crawl_tools_are_opt_in(monkeypatch):
    names = {t.name for t in _build(monkeypatch)}
    assert "scavio_crawl_website" not in names
    assert "scavio_extract" in names


def test_crawl_tools_register(monkeypatch):
    tools = _crawl_tools(monkeypatch, _JobClient())
    assert set(tools) == {
        "scavio_map_website", "scavio_crawl_website", "scavio_crawl_status",
        "scavio_batch_extract", "scavio_batch_status",
    }


def test_map_calls_extract_map(monkeypatch):
    tools = _crawl_tools(monkeypatch, _FakeClient())
    out = _invoke(tools["scavio_map_website"], {"url": "scavio.dev", "limit": 5, "include_paths": ["/blog/**"]})
    assert (out["namespace"], out["method"]) == ("extract", "map")
    assert out["kwargs"] == {"url": "scavio.dev", "limit": 5, "include_paths": ["/blog/**"]}


def test_crawl_waits_until_completed_then_reads_results(monkeypatch):
    client = _JobClient()
    tools = _crawl_tools(monkeypatch, client)
    out = _invoke(tools["scavio_crawl_website"], {"url": "https://hono.dev/docs", "max_pages": 3, "limit": 5})
    assert out["data"]["status"] == "completed"
    assert client.calls[0] == ("extract", "crawl", {"url": "https://hono.dev/docs", "max_pages": 3})
    assert client.calls[1] == ("extract", "crawl_status", {"job_id": JOB_ID, "limit": 1, "include_content": False})
    assert client.calls[-1] == ("extract", "crawl_status", {"job_id": JOB_ID, "limit": 5})


def test_crawl_wait_zero_returns_the_queued_job(monkeypatch):
    client = _JobClient()
    tools = _crawl_tools(monkeypatch, client)
    out = _invoke(tools["scavio_crawl_website"], {"url": "https://hono.dev/docs", "wait_seconds": 0})
    assert out["data"]["status"] == "queued"
    assert len(client.calls) == 1


def test_crawl_still_running_when_the_wait_ends(monkeypatch):
    client = _JobClient(statuses=["running"] * 100)
    tools = _crawl_tools(monkeypatch, client)
    ticks = iter(range(0, 10_000, 10))
    monkeypatch.setattr(tools_mod.time, "monotonic", lambda: float(next(ticks)))
    out = _invoke(tools["scavio_crawl_website"], {"url": "https://hono.dev/docs", "wait_seconds": 5})
    assert out["data"]["status"] == "running"
    assert out["data"]["id"] == JOB_ID


def test_batch_and_status_tools(monkeypatch):
    client = _JobClient()
    tools = _crawl_tools(monkeypatch, client)
    out = _invoke(tools["scavio_batch_extract"], {"urls": ["https://example.com/"], "mode": "normal"})
    assert out["data"]["status"] == "completed"
    assert client.calls[0] == ("extract", "batch", {"urls": ["https://example.com/"], "mode": "normal"})
    _invoke(tools["scavio_crawl_status"], {"id": "crawl_1", "cursor": "25", "include_content": False})
    assert client.calls[-1] == ("extract", "crawl_status", {"job_id": "crawl_1", "cursor": "25", "limit": 10, "include_content": False})
    _invoke(tools["scavio_batch_status"], {"id": "batch_1"})
    assert client.calls[-1] == ("extract", "batch_status", {"job_id": "batch_1", "limit": 10})


def test_crawl_tools_match_the_real_sdk_signatures():
    """Every SDK method the website tools call exists on scavio and accepts the kwargs."""
    from scavio import ScavioClient

    ext = ScavioClient(api_key="test").extract
    expected = {
        "map": {"url", "search", "limit", "sitemap", "include_subdomains", "include_paths", "exclude_paths", "ignore_query_parameters", "mode"},
        "crawl": {"url", "max_pages", "max_depth", "include_paths", "exclude_paths", "allow_subdomains", "ignore_query_parameters", "sitemap", "format", "mode"},
        "crawl_status": {"job_id", "cursor", "limit", "status", "include_content"},
        "batch": {"urls", "format", "mode"},
        "batch_status": {"job_id", "cursor", "limit", "status", "include_content"},
    }
    for method, params in expected.items():
        accepted = set(inspect.signature(getattr(ext, method)).parameters)
        assert params <= accepted, (method, params - accepted)


def test_website_tools_never_describe_the_fetch_method(monkeypatch):
    tools = _crawl_tools(monkeypatch, _JobClient())
    tools.update({t.name: t for t in _only(monkeypatch, "extract")})
    for tool in tools.values():
        text = (tool.description + json.dumps(tool.params_json_schema)).lower()
        assert "credit" in tool.description.lower(), tool.name
        for word in ("proxy", "residential", "datacenter", "headless", "browser"):
            assert word not in text, (tool.name, word)
