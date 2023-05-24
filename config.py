from environs import Env

env = Env()
env.read_env()


class OpenAiConfig:
    OPENAI_API_KEY = env.str('OPENAI_API_KEY')
    CHAT_MODEL = env.str('CHAT_MODEL')
    DEFAULT_PROMPT = """
     
    """
    MAX_TOKENS = 4096
    MAX_RESPONSE_TOKENS = 1000
    MESSAGE_DATA = {
        'role': 'system',
        'content': """
        You are a friendly assistant for a company that can answer general questions
        about business, marketing, and programming. Your goal is to help the people in
        the company with any questions they might have. If you aren't sure about
        something or something seems inappropriate, you should say that you don't know.
    """
    }


class SlackConfig:
    SLACK_BOT_TOKEN = env.str('SLACK_BOT_TOKEN')
    SLACK_APP_TOKEN = env.str('SLACK_APP_TOKEN')
