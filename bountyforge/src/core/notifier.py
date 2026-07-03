import httpx

class Notifier:
    def __init__(self, config):
        a = config.get('alerting', {})
        self.slack = a.get('slack_webhook')
        self.telegram_token = a.get('telegram_bot_token')
        self.telegram_chat = a.get('telegram_chat_id')
        self.discord = a.get('discord_webhook')
        self.enabled = a.get('enabled', False)

    async def send(self, title, message, severity="HIGH"):
        if not self.enabled:
            return
        msg = f"🚨 *{severity}*: {title}\n\n{message[:3000]}"
        async with httpx.AsyncClient() as client:
            if self.slack:
                await client.post(self.slack, json={"text": msg})
            if self.telegram_token and self.telegram_chat:
                await client.post(
                    f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                    data={"chat_id": self.telegram_chat, "text": msg, "parse_mode": "Markdown"}
                )
            if self.discord:
                await client.post(self.discord, json={"content": msg})
