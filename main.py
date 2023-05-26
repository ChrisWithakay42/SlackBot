import openai
from environs import Env
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

env = Env()
env.read_env()
app = App()
slack_client = WebClient(token=env.str('SLACK_BOT_TOKEN'))
openai.api_key = env.str('OPENAI_API_KEY')


def get_completion(prompt, history) -> str:
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'system', 'content': prompt}] + history,
        temperature=0
    )
    completion = response.choices[0].message['content'].strip()
    return completion


def get_message_history(
        channel_id: str, user_id: str, event_ts: str,
        limit: int, is_thread: bool = False
):
    conversation_history = []

    if is_thread:
        res = slack_client.conversations_replies(
            channel=channel_id, ts=event_ts, limit=limit,
        )
    else:
        res = slack_client.conversations_history(
            channel=channel_id, limit=limit
        )

    for message in res['messages']:
        if message.get('user') == user_id:
            role = 'user'
        elif message.get('subtype') == 'bot_message' or message.get('bot_id'):
            role = 'assistant'
        else:
            role = 'user'  # Assign the role as 'user' for non-bot messages

        conversation_history.append({'role': role, 'content': message['text']})

    if not is_thread:
        conversation_history.reverse()

    return conversation_history


def handle_event(event: dict, is_thread: bool = False):
    channel_id = event['channel']
    user_id = event['user']
    event_ts = event['event_ts']

    payload = {'channel': channel_id, 'text': 'Working on a response... :robot_face:'}

    if is_thread:
        event_ts = event.get('thread_ts', event['ts'])
        payload['thread_ts'] = event_ts

    message_history = get_message_history(
        channel_id=channel_id, user_id=user_id, event_ts=event_ts, limit=50, is_thread=is_thread
    )

    first_message = slack_client.chat_postMessage(
        **payload
    )
    prompt = event['text']

    try:
        chat_completion = get_completion(prompt, message_history)
    except Exception as e:
        chat_completion = f'Call to an external service failed {e}'

    slack_client.chat_update(
        channel=channel_id, ts=first_message['ts'], text=chat_completion
    )


@app.event('app_mention')
def handle_mention(event):
    handle_event(event, is_thread=True)


@app.event('message')
def handle_direct_message(event):
    handle_event(event)


if __name__ == '__main__':
    slack_app_token = env.str('SLACK_APP_TOKEN')
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()
