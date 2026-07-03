from src.core.ai_agent import BugBountyAgent

class Summarizer:
    def __init__(self, agent: BugBountyAgent):
        self.agent = agent

    async def summarize(self, raw_report: str) -> str:
        """Summarize a raw security report into 5 bullet points."""
        if not raw_report or len(raw_report.strip()) < 10:
            return "❌ Report is too short or empty to summarize."

        prompt = f"""
        You are a security report summarizer. Summarize the following report into exactly 5 bullet points:
        1. Total number of vulnerabilities found.
        2. The single most critical vulnerability (if any).
        3. Any vulnerability that requires immediate manual verification.
        4. Fix recommendations for the top 3 issues.
        5. A one-line conclusion.

        Report:
        {raw_report[:8000]}
        """
        return await self.agent.send_prompt(prompt)
