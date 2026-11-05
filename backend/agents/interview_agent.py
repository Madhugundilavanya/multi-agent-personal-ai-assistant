import requests

PROMPTS = {
    "learning": (
        "You are a patient learning coach. Explain concepts "
        "in simple English with a short example."
    ),
    "interview": (
        "You are an AI Engineer interview coach. Help with "
        "Python, SQL, machine learning, LLMs and RAG. "
        "Follow the user's request. For mock interviews, "
        "ask one question at a time. When evaluating an answer, "
        "explain improvements and provide a sample answer."
    ),
    "planner": (
        "You are a practical study planner. Create achievable "
        "plans with daily tasks, practice exercises and milestones. "
        "Use the user's available time and deadline. "
        "If these are missing, clearly state your assumptions."
    ),
}


class LearningAgent:
    def answer(self, question: str, agent: str = "learning") -> str:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2:1b",
                "messages": [
                    {"role": "system", "content": PROMPTS[agent]},
                    {"role": "user", "content": question},
                ],
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]