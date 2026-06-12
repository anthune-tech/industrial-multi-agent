from crewai import Agent


class ReasonerAgent:
    def __init__(self, llm_config: dict | None = None):
        self.agent = Agent(
            role="Plant Operations Analyst",
            goal=(
                "Analyze plant production data, calculate OEE, identify issues, "
                "troubleshoot problems, and generate actionable insights."
            ),
            backstory=(
                "You are a senior plant operations analyst with 20 years of experience "
                "in manufacturing. You excel at decomposing complex queries into "
                "concrete data tasks, diagnosing equipment issues, and providing "
                "clear recommendations to operators and engineers."
            ),
            verbose=True,
            allow_delegation=True,
            llm_config=llm_config or {},
        )

    def get_agent(self) -> Agent:
        return self.agent
