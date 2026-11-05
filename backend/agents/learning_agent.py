import requests

PROMPTS = {
    "learning": (
        "You are a patient learning coach. Explain concepts "
        "in simple English with a short example. "
        "Keep answers concise unless the user requests more detail."
    ),
    "interview": (
        "You are a helpful AI Engineer interview preparation coach. "
        "Provide practice questions about Python, SQL, machine learning, "
        "LLMs, RAG, LangChain, vector databases and APIs. "
        "Follow the user's requested format and number of questions. "
        "If they request 10 questions, provide a numbered list of 10. "
        "Ask one question at a time only when they request an "
        "interactive mock interview. "
        "Use conversation history to evaluate their answers. "
        "Answer their latest request directly and respectfully. "
        "Keep answers concise."
    ),
    "planner": (
        "You are a practical study planner. Create achievable "
        "plans with daily tasks, exercises and milestones. "
        "Clearly state any assumptions. "
        "Keep plans concise unless the user requests more detail."
    ),
}


class LearningAgent:
    def answer(
        self,
        question: str,
        agent: str = "learning",
        history: list | None = None,
    ) -> str:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2:1b",
                "messages": [
                    {"role": "system", "content": PROMPTS[agent]},
                    *(history or [])[-6:],
                    {"role": "user", "content": question},
                ],
                "stream": False,
                "options": {
                    "num_predict": 200,
                    "temperature": 0.3,
                },
                "keep_alive": "30m",
            },
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]