"""Adapt LangChain tools for CrewAI 1.x compatibility."""

from langchain.tools import StructuredTool
from crewai.tools.base_tool import Tool as CrewTool


def adapt(tool: StructuredTool) -> CrewTool:
    """Convert a LangChain StructuredTool into a CrewAI Tool."""
    return CrewTool(
        name=tool.name,
        description=tool.description,
        func=tool.func,
    )
