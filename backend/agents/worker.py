from crewai import Agent


class WorkerAgent:
    def __init__(self, llm_config: dict | None = None, tools: list | None = None):
        self.agent = Agent(
            role="Data Processing Engineer",
            goal=(
                "Execute data analysis tasks accurately using available tools — "
                "reading plant data, calculating KPIs, querying databases, "
                "and saving results."
            ),
            backstory=(
                "You are a data processing engineer specializing in manufacturing "
                "telemetry. You work efficiently with structured data, follow "
                "instructions precisely, and return clean, verified results."
            ),
            verbose=True,
            allow_delegation=False,
            tools=tools or [],
            llm_config=llm_config or {},
        )

    def get_agent(self) -> Agent:
        return self.agent
