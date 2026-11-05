import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from backend.agents.learning_agent import LearningAgent


class AssistantState(TypedDict):
    message: str
    requested_agent: str
    history: list[dict]
    agent: str
    answer: str


assistant = LearningAgent()


def detect_agent(text: str) -> str | None:
    text = text.lower()

    if re.search(
        r"\b(plan|schedule|roadmap|milestones)\b", text
    ):
        return "planner"

    if re.search(
        r"\b(interview|interviewer|mock|evaluate)\b", text
    ):
        return "interview"

    if re.search(
        r"\b(explain|teach|understand|example)\b", text
    ):
        return "learning"

    return None


def route_request(state: AssistantState) -> dict:
    requested = state["requested_agent"]

    if requested != "auto":
        return {"agent": requested}

    selected = detect_agent(state["message"])

    # For short follow-ups, reuse the most recent user intent.
    if selected is None:
        for message in reversed(state["history"]):
            if message["role"] == "user":
                selected = detect_agent(message["content"])
                if selected:
                    break

    return {"agent": selected or "learning"}


def make_coach_node(agent: str):
    def run(state: AssistantState) -> dict:
        answer = assistant.answer(
            state["message"],
            agent,
            state["history"],
        )
        return {"answer": answer}

    return run


builder = StateGraph(AssistantState)
builder.add_node("router", route_request)

for agent in ("learning", "interview", "planner"):
    builder.add_node(agent, make_coach_node(agent))
    builder.add_edge(agent, END)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    lambda state: state["agent"],
    {
        "learning": "learning",
        "interview": "interview",
        "planner": "planner",
    },
)

workflow = builder.compile()


def run_assistant(
    message: str,
    requested_agent: str,
    history: list[dict],
) -> dict:
    result = workflow.invoke({
        "message": message,
        "requested_agent": requested_agent,
        "history": history,
        "agent": "",
        "answer": "",
    })

    return {
        "agent": result["agent"],
        "answer": result["answer"],
    }
