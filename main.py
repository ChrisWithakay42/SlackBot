import logging

import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import OpenAiConfig
from config import SlackConfig
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


slack_client = SlackClient(SlackConfig.SLACK_BOT_TOKEN, config={'MAX_TOKENS': 4096, 'MAX_RESPONSE_TOKENS': 1000})


@app.event('message')
def handle_direct_messages(event, say):
    if hasattr(event, 'bot_id'):
        return  # bot should not be triggered on its own messages
    completion = generate_completion(prompt=event['text'])
    say(text=completion)


if __name__ == '__main__':
    handler = SocketModeHandler(app, SlackConfig.SLACK_APP_TOKEN)
    handler.start()
