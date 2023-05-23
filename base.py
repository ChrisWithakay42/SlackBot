from abc import ABC
from abc import abstractmethod


class OpenAiCompletionInterface(ABC):

    @abstractmethod
    def get_completion(self, prompt: str, history: list):
        pass

    @abstractmethod
    def get_token_count(self, text: str):
        pass
