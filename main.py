from slack_bolt import App

from chat_bot import OpenAIChat
from chat_bot import SlackBot
from chat_bot import SlackClient
from config import OpenAiConfig
from config import SlackConfig

if __name__ == '__main__':
    app = App()
    openai_chat = OpenAIChat(
        model=OpenAiConfig.CHAT_MODEL,
        max_tokens=OpenAiConfig.MAX_TOKENS,
        max_response_tokens=OpenAiConfig.MAX_RESPONSE_TOKENS,
        api_key=OpenAiConfig.OPENAI_API_KEY
    )
    slack_client = SlackClient(bot_token=SlackConfig.SLACK_BOT_TOKEN)
    slack_bot = SlackBot(
        app=app,
        slack_client=slack_client,
        openai_chat=openai_chat
    )
