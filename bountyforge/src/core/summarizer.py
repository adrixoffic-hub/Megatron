
from src.core.ai_agent import BugBountyAgent

class Summarizer:
    def __init__(self, agent: BugBountyAgent):
        self.agent = agent

    async def summarize(self, raw_report: str) -> str:
        prompt = f"""
        You are a security report summarizer. I have a raw scan report.
        Summarize the following into 5 bullet points:
        1. Total number of vulnerabilities.
        2. The single most critical vulnerability.
        3. Any vulnerability that requires immediate manual verification.
        4. Fix recommendations for the top 3 issues.
        5. A one-line conclusion.

        Report:
        {raw_report[:8000]}
        """
        return await self.agent.send_prompt(prompt)
