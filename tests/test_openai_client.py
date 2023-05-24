from unittest.mock import MagicMock
from unittest.mock import patch

from draft.chat_bot import OpenAiChat


@patch("openai.ChatCompletion.create")
def test_get_completion(mock_create, chat_instance):
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message={"content": "I'm doing great!"})
    ]
    mock_create.return_value = mock_response

    history = ["History message 1", "History message 2"]
    completion = chat_instance.get_completion(history)

    assert completion == "I'm doing great!"
    mock_create.assert_called_once_with(
        model="gpt3",
        messages=["Hello, how are you?"] + history,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0
    )
