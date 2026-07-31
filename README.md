# openai-agents-scavio

[Scavio](https://scavio.dev) real-time search tools for the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — Google, YouTube, Amazon, Walmart, Reddit, TikTok, and Instagram, with one API key.

> **Amazon changed (breaking).** The upstream provider moved in 2026-07:
> `domain` is replaced by `country`, a two-letter marketplace code (`us`, `gb`
> -- the UK is `gb`, not `uk` -- `de`, `jp`, ...), and `sort_by`, `pages`,
> `category_id`, `merchant_id`, `language`, `currency`, `device`, `zip_code`
> and `autoselect_variant` are gone. The marketplace ignores all of them
> (`sort_by` returns the identical unordered set for every value), so they are
> removed rather than kept as silent no-ops. Rank and filter results yourself.

## Install

```bash
pip install openai-agents-scavio
```

## Setup

Get a Scavio API key from the [Scavio Dashboard](https://dashboard.scavio.dev) (new accounts get free credits, no credit card). Set `SCAVIO_API_KEY` or pass `api_key=` to the factory.

## Usage

```python
from agents import Agent, Runner
from openai_agents_scavio import get_scavio_tools

agent = Agent(
    name="Search Assistant",
    instructions="Search the web, shopping sites, and social platforms with Scavio.",
    tools=get_scavio_tools(),  # reads SCAVIO_API_KEY
)

result = Runner.run_sync(agent, "Find the top budget laptops on Amazon")
print(result.final_output)
```

Expose only the providers you need:

```python
tools = get_scavio_tools(
    enable_google=True,
    enable_reddit=True,
    enable_amazon=False,
    enable_walmart=False,
    enable_youtube=False,
    enable_tiktok=False,
    enable_instagram=False,
)
```

Pass `all=True` to register every tool regardless of the individual flags.

## Tools

`get_scavio_tools()` returns one function tool per Scavio endpoint, named `scavio_<provider>_<action>` (e.g. `scavio_google_search`, `scavio_amazon_product`, `scavio_reddit_post`). Each returns the structured Scavio JSON response; errors come back as `{"error": "..."}` rather than raising, so a failed call never crashes the run.

## Use every endpoint via MCP

For the full Scavio API with no install, point the Agents SDK at the hosted MCP server:

```python
from agents import Agent
from agents.mcp.server import MCPServerStreamableHttp

server = MCPServerStreamableHttp(
    name="scavio",
    params={"url": "https://mcp.scavio.dev/mcp", "headers": {"x-api-key": "sk_live_..."}},
)
agent = Agent(name="Search Assistant", mcp_servers=[server])
```

## Credits

Most calls cost 1 credit (Google included). Instagram costs 8-10 credits per call, except user posts which costs 2. See [scavio.dev/docs](https://scavio.dev/docs).

## Links

- Scavio: https://scavio.dev
- Docs: https://scavio.dev/docs/openai-agents
- Dashboard: https://dashboard.scavio.dev
