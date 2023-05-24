from unittest.mock import MagicMock

import pytest

from draft.chat_bot import OpenAiChat


@pytest.fixture
def chat_instance():
    message = MagicMock()
    message.message.return_value = "Hello, how are you?"
    return OpenAiChat(message, "gpt3", 100, 50, "api_key")

