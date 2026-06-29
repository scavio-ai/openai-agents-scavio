"""Run Scavio tools inside an OpenAI Agents SDK agent.

Prerequisites:
    pip install openai-agents-scavio
    export OPENAI_API_KEY=...
    export SCAVIO_API_KEY=sk_...   # from https://dashboard.scavio.dev
"""

from agents import Agent, Runner

from openai_agents_scavio import get_scavio_tools


def main() -> None:
    agent = Agent(
        name="Search Assistant",
        instructions="Search the web and Reddit before you answer, and cite your sources.",
        tools=get_scavio_tools(enable_google=True, enable_reddit=True),
    )
    result = Runner.run_sync(
        agent,
        "Is the OpenAI Agents SDK worth using in 2026? Summarize what the docs say and what developers on Reddit think.",
    )
    print(result.final_output)


if __name__ == "__main__":
    main()
