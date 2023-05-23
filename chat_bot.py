import re
from datetime import datetime
from time import time

import openai
import tiktoken
from openai import OpenAIError
from slack_bolt import App
from slack_sdk import WebClient

from base import OpenAiCompletionInterface


def _clean_prompt(prompt):
    # Here we are matching and removing the @User string from the prompt
    return re.sub(r'\\s<@[^, ]*|^<@[^, ]*', '', prompt)


class Message:

    def __init__(self, role, content):
        self.role = role
        self.content = content

    def message(self):
        return {
            "role": self.role,
            "content": self.content
        }


class OpenAIChat(OpenAiCompletionInterface):
    def __init__(
            self,
            message: Message, model: str, max_tokens: int,
            max_response_tokens: int, api_key: str
    ):
        self.message = message
        self.model = model
        self.max_tokens = max_tokens
        self.max_response_tokens = max_response_tokens
        self.api_key = api_key

    def get_completion(self, prompt: str, history: list) -> str:
        openai.api_key = self.api_key

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[self.message.message()] + history,
            max_tokens=self.max_response_tokens,
            n=1,
            stop=None,
            temperature=0,
        )

        completion = response.choices[0].message["content"].strip()
        return completion

    def get_token_count(self, text: str):
        ...


class SlackClient:
    def __init__(self, bot_token: str):
        self.client = WebClient(token=bot_token)

    def get_message_history(self, channel_id, user_id, event_ts, limit, thread=False):
        if thread:
            return self._get_thread_history(channel_id, user_id, event_ts, limit)
        else:
            return self._get_conversation_history(channel_id, user_id, limit)

    def _get_thread_history(self, channel_id, user_id, event_ts, limit):
        result = self.client.conversations_replies(
            channel=channel_id, ts=event_ts, limit=limit, latest=str(datetime.now())
        )

        return self._extract_messages(result["messages"], user_id)

    def _get_conversation_history(self, channel_id, user_id, limit):
        result = self.client.conversations_history(channel=channel_id, limit=limit)

        return self._extract_messages(result["messages"], user_id)

    def _extract_messages(self, messages, user_id):
        history = []
        token_count = 0

        for message in messages:
            if self._is_user_message(message, user_id):
                role = "user"
                token_count += len(message["text"])
                if token_count > (MAX_TOKENS - MAX_RESPONSE_TOKENS):
                    break
                else:
                    history.append({"role": role, "content": message["text"]})

        history.reverse()
        return history

    def _is_user_message(self, message, user_id):
        return message.get("user") == user_id


class SlackBot:
    def __init__(
            self,
            app: App, slack_client: SlackClient, openai_chat: OpenAIChat
    ):
        self.app = app
        self.slack_client = slack_client
        self.openai_chat = openai_chat

    def handle_message(self, event: dict, thread: bool = False):
        channel_id = event["channel"]
        user_id = event["user"]
        event_ts = event["ts"]
        payload = {"channel": channel_id, "text": "Working a response... :robot_face:"}

        if thread:
            event_ts = event.get("thread_ts", event["ts"])
            payload["thread_ts"] = event_ts

        history = self.slack_client.get_message_history(
            channel_id, user_id, event_ts, limit=25, thread=thread
        )

        typing_message = self.slack_client.client.chat_postMessage(**payload)

        try:
            completion_message = self.openai_chat.get_completion(history=history)
        except OpenAIError as e:
            completion_message = (
                f'The call to OpenAI or another external service failed. Please try again later. \n{e}'
            )

        self.slack_client.client.chat_update(
            channel=channel_id, ts=typing_message["ts"], text=completion_message
        )
