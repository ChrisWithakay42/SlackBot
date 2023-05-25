import logging

import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import OpenAiConfig
from config import SlackConfig
from draft.chat_bot import Message
from draft.chat_bot import OpenAiChat
from draft.chat_bot import SlackBot
from draft.chat_bot import SlackClient

logger = logging.getLogger(__name__)
openai.api_key = OpenAiConfig.OPENAI_API_KEY

app = App(token=SlackConfig.SLACK_BOT_TOKEN)


def generate_completion(prompt):
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'system', 'content': prompt}],
        temperature=0
    )
    completion = resp.choices[0].message['content'].strip()
    return completion


message = Message(**OpenAiConfig.MESSAGE_DATA)
openai_chat = OpenAiChat(
    message=message,
    model=OpenAiConfig.CHAT_MODEL,
    max_tokens=OpenAiConfig.MAX_TOKENS,
    max_response_tokens=OpenAiConfig.MAX_RESPONSE_TOKENS,
    api_key=OpenAiConfig.OPENAI_API_KEY
)
slack_client = SlackClient(
    bot_token=SlackConfig.SLACK_BOT_TOKEN,
    config={'MAX_TOKENS': OpenAiConfig.MAX_TOKENS, 'MAX_RESPONSE_TOKENS': OpenAiConfig.MAX_RESPONSE_TOKENS}
)
slack_bot = SlackBot(slack_client=slack_client, openai_chat=openai_chat)


@app.event('message')
def handle_direct_messages(event):
    if hasattr(event, 'bot_id'):
        return  # bot should not be triggered on its own messages
    slack_bot.handle_event(event=event)


@app.event('app_mention')
def handle_mention(event):
    slack_bot.handle_event(event=event, thread=True)


if __name__ == '__main__':
    handler = SocketModeHandler(app, SlackConfig.SLACK_APP_TOKEN)
    handler.start()
