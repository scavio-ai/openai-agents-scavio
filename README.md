# openai-agents-scavio

[Scavio](https://scavio.dev) real-time search tools for the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — Google, YouTube, Amazon, Walmart, Reddit, TikTok, and Instagram, with one API key. Scavio also covers TikTok Shop, X and LinkedIn; reach those through the [hosted MCP server](#use-every-endpoint-via-mcp).

> **Amazon changed (breaking).** The upstream provider moved in 2026-07:
> `domain` is replaced by `country`, a two-letter marketplace code (`us`, `gb`
> -- the UK is `gb`, not `uk` -- `de`, `jp`, ...), and `sort_by`, `pages`,
> `category_id`, `merchant_id`, `language`, `currency`, `device`, `zip_code`
> and `autoselect_variant` are gone. The marketplace ignores all of them
> (`sort_by` returns the identical unordered set for every value), so they are
> removed rather than kept as silent no-ops. Rank and filter results yourself.
> A third Amazon tool arrived with the move: `scavio_amazon_offers` lists every
> seller offering an ASIN -- price, condition, shipping, and which offer holds
> the buy box. 1 credit, same as the other two.

## Install

```bash
pip install openai-agents-scavio
```

## Setup

Get a Scavio API key from the [Scavio Dashboard](https://dashboard.scavio.dev) (new accounts get 50 free credits, no credit card). Set `SCAVIO_API_KEY` or pass `api_key=` to the factory.

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

The tools above cover seven platforms. For the full Scavio API — every endpoint across Google, YouTube, Amazon, Walmart, Reddit, TikTok, TikTok Shop, Instagram, X and LinkedIn, with no install — point the Agents SDK at the hosted MCP server:

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

Most calls cost 1 credit, Google and Reddit included. The exceptions:

| Tool | Credits |
|---|---|
| `scavio_youtube_search`, `scavio_youtube_shorts` | 2 |
| `scavio_youtube_streams` | 3 |
| `scavio_youtube_transcript` | 8 |
| `scavio_instagram_user_posts` | 2 |
| `scavio_instagram_post`, `scavio_instagram_comment_replies` | 8 |
| every other `scavio_instagram_*` | 10 |

See [scavio.dev/docs](https://scavio.dev/docs).

## Links

- Scavio: https://scavio.dev
- Docs: https://scavio.dev/docs/openai-agents
- Dashboard: https://dashboard.scavio.dev
