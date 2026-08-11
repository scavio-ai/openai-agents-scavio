"""Run Scavio tools inside an OpenAI Agents SDK agent.

Prerequisites:
    pip install openai-agents-scavio
    export OPENAI_API_KEY=...
    export SCAVIO_API_KEY=sk_...   # from https://dashboard.scavio.dev
"""

from agents import Agent, Runner

from openai_agents_scavio import get_scavio_tools

# get_scavio_tools() registers all 188 tools across 31 platforms. That is more
# than any one agent should carry, so each example below enables only what it
# needs and leaves the rest off.
OFF = dict(
    enable_google=False, enable_amazon=False, enable_walmart=False,
    enable_youtube=False, enable_reddit=False, enable_tiktok=False,
    enable_tiktok_shop=False, enable_instagram=False, enable_x=False,
    enable_linkedin=False, enable_threads=False, enable_kuaishou=False,
    enable_ebay=False, enable_target=False, enable_home_depot=False,
    enable_zillow=False, enable_booking=False, enable_tripadvisor=False,
    enable_indeed=False, enable_airbnb=False, enable_glassdoor=False,
    enable_yelp=False, enable_app_store=False, enable_google_play=False,
    enable_sec=False, enable_redfin=False, enable_companies_house=False,
    enable_g2=False, enable_capterra=False, enable_google_ads=False,
    enable_meta_ads=False, enable_extract=False,
)


def research_agent() -> None:
    """Search the web and Reddit, then read the pages that look worth reading."""
    agent = Agent(
        name="Search Assistant",
        instructions="Search the web and Reddit before you answer, and cite your sources.",
        tools=get_scavio_tools(
            **{**OFF, "enable_google": True, "enable_reddit": True, "enable_extract": True}
        ),
    )
    result = Runner.run_sync(
        agent,
        "Is the OpenAI Agents SDK worth using in 2026? Summarize what the docs say "
        "and what developers on Reddit think.",
    )
    print(result.final_output)


def competitor_agent() -> None:
    """Software buyers: G2 and Capterra reviews plus whatever the vendor is advertising."""
    agent = Agent(
        name="Competitive Research",
        instructions=(
            "Research a software vendor. Read its G2 and Capterra reviews for what "
            "customers complain about, then check the Meta Ad Library for the claims "
            "it is making in its own ads."
        ),
        tools=get_scavio_tools(
            **{**OFF, "enable_g2": True, "enable_capterra": True, "enable_meta_ads": True}
        ),
    )
    result = Runner.run_sync(agent, "What do buyers dislike about Notion, and how does it advertise?")
    print(result.final_output)


def filings_agent() -> None:
    """SEC EDGAR is keyed by CIK, so the agent gets the lookup tool alongside the data."""
    agent = Agent(
        name="Filings Analyst",
        instructions=(
            "Resolve the ticker to a CIK with scavio_sec_lookup first, then pull filings. "
            "Never guess a CIK."
        ),
        tools=get_scavio_tools(**{**OFF, "enable_sec": True}),
    )
    result = Runner.run_sync(agent, "What did NVDA say about supply constraints in its latest 10-Q?")
    print(result.final_output)


if __name__ == "__main__":
    research_agent()
