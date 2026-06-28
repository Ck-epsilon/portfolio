# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""CrewAI agent and task definitions for the AI Workbench.

Two-agent crew:
  - researcher: gathers information using web search + scraping tools
  - analyst: synthesizes findings into structured reports

All agents instrumented via LangFuse for trace/span/cost observability.
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FileReadTool

# ── LangFuse callback (automatic tracing) ────────────────────
def _setup_langfuse():
    """Configure LangFuse tracing if credentials are available."""
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        from langfuse.callback import CallbackHandler
        return CallbackHandler()
    return None


# ── Tools ────────────────────────────────────────────────────
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
file_tool = FileReadTool()


# ── Agents ───────────────────────────────────────────────────
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find accurate, up-to-date information on the given topic using web search and source verification",
    backstory=(
        "You are a veteran researcher with 15 years of experience at a top-tier consulting firm. "
        "You cross-reference multiple sources, verify claims, and never present speculation as fact. "
        "When information is uncertain, you clearly state the confidence level."
    ),
    tools=[search_tool, scrape_tool],
    verbose=True,
    allow_delegation=False,
    llm=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    max_iter=5,
)

analyst = Agent(
    role="Principal Data Analyst",
    goal="Synthesize raw research findings into clear, actionable reports with key insights and recommendations",
    backstory=(
        "You are a principal analyst known for turning complex data into clear narratives. "
        "Executives rely on your reports to make multi-million dollar decisions. "
        "You structure information logically, highlight the 3-5 most important takeaways, "
        "and include concrete data points to support every claim."
    ),
    tools=[file_tool],
    verbose=True,
    allow_delegation=False,
    llm=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    max_iter=3,
)


# ── Task factory ─────────────────────────────────────────────
def create_research_task(topic: str) -> Task:
    """Create a research task for the given topic."""
    return Task(
        description=(
            f"Research the following topic thoroughly: '{topic}'. "
            "Use web search to find recent, credible sources. "
            "Extract key facts, statistics, expert opinions, and competing viewpoints. "
            "Organize findings by: (1) Current state, (2) Key trends, (3) Major players, "
            "(4) Risks and opportunities, (5) Sources cited. "
            "Aim for at least 5 distinct sources."
        ),
        expected_output=(
            "A structured research brief with sections: Summary, Key Findings (bullet points), "
            "Detailed Analysis (by subtopic), Sources (URLs with brief descriptions), "
            "Confidence Assessment (high/medium/low per finding). "
            "Minimum 500 words."
        ),
        agent=researcher,
    )


def create_analysis_task(topic: str) -> Task:
    """Create an analysis task that processes research output."""
    return Task(
        description=(
            f"Take the research findings on '{topic}' and synthesize them into an executive-ready report. "
            "Structure: (1) Executive Summary (3 sentences max), "
            "(2) Top 5 Insights (ranked by importance), "
            "(3) Supporting Evidence (data points from research), "
            "(4) Recommendations (3-5 actionable next steps), "
            "(5) Limitations and Unknowns. "
            "Use concrete numbers, percentages, and comparisons where available."
        ),
        expected_output=(
            "An executive report with Title, Executive Summary, Top 5 Insights, "
            "Supporting Evidence, Recommendations, and Limitations. "
            "Ready for C-suite presentation. Minimum 400 words."
        ),
        agent=analyst,
        context=[],  # Will be populated with research output at runtime
    )


# ── Crew ─────────────────────────────────────────────────────
def build_crew(topic: str) -> Crew:
    """Build a two-agent research crew for the given topic."""
    research_task = create_research_task(topic)
    analysis_task = create_analysis_task(topic)
    # Analyst receives researcher's output as context
    analysis_task.context = [research_task]

    langfuse_handler = _setup_langfuse()

    return Crew(
        agents=[researcher, analyst],
        tasks=[research_task, analysis_task],
        process=Process.sequential,
        verbose=True,
        memory=True,
        planning=True,
        output_log_file="crew_output.log",
        **(  # type: ignore
            {"callbacks": [langfuse_handler]} if langfuse_handler else {}
        ),
    )
