from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_core.tools import BaseTool
from pydantic import Field


@dataclass
class RouteDecision:
    task: str
    tool_name: str


class _MetadataTool(BaseTool):
    name: str = "metadata_tool"
    description: str = "Use for questions asking about image metadata, dimensions, CRS, or coverage."

    def _run(self, query: str) -> str:
        return "metadata"


class _VQATool(BaseTool):
    name: str = "vqa_tool"
    description: str = "Use for natural-language questions about a single remote-sensing image."

    def _run(self, query: str) -> str:
        return "vqa"


class _GroundingTool(BaseTool):
    name: str = "grounding_tool"
    description: str = "Use when the user asks to locate, highlight, or count an object/region."

    def _run(self, query: str) -> str:
        return "grounding"


class _ChangeTool(BaseTool):
    name: str = "change_detection_tool"
    description: str = "Use for two images representing different dates or explicit change questions."

    def _run(self, query: str) -> str:
        return "change_detection"


class _OpticalSarTool(BaseTool):
    name: str = "optical_sar_tool"
    description: str = "Use for complementary optical and SAR analysis."

    def _run(self, query: str) -> str:
        return "optical_sar"


class SatQueryAgent:
    """Deterministic first-stage LangChain tool router.

    The current build intentionally has no LLM. The routing rules are explicit,
    testable, and replaceable with a LangChain LLM agent when the EarthDial
    inference service is connected.
    """

    def __init__(self) -> None:
        self.tools = [
            _MetadataTool(),
            _VQATool(),
            _GroundingTool(),
            _ChangeTool(),
            _OpticalSarTool(),
        ]
        self._by_name = {tool.name: tool for tool in self.tools}

    def route(
        self,
        query: str,
        num_images: int,
        modalities: list[str],
        task_hint: str = "auto",
    ) -> RouteDecision:
        if task_hint and task_hint != "auto":
            mapping = {
                "vqa": ("vqa", "vqa_tool"),
                "grounding": ("grounding", "grounding_tool"),
                "change": ("change_detection", "change_detection_tool"),
                "optical_sar": ("optical_sar", "optical_sar_tool"),
            }
            if task_hint in mapping:
                task, tool = mapping[task_hint]
                return RouteDecision(task, tool)

        text = query.lower()
        metadata_words = ("crs", "coordinate system", "bounds", "metadata", "resolution", "dimensions")
        grounding_words = ("where", "highlight", "locate", "show me", "count", "find")
        change_words = ("change", "changed", "difference", "before and after", "between the two")

        if any(word in text for word in metadata_words):
            return RouteDecision("metadata", "metadata_tool")
        if num_images == 2 and ("sar" in modalities or "radar" in text or "optical + sar" in text):
            return RouteDecision("optical_sar", "optical_sar_tool")
        if num_images == 2 or any(word in text for word in change_words):
            return RouteDecision("change_detection", "change_detection_tool")
        if any(word in text for word in grounding_words):
            return RouteDecision("grounding", "grounding_tool")
        return RouteDecision("vqa", "vqa_tool")


agent = SatQueryAgent()
