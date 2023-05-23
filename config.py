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


class SlackConfig:
    SLACK_BOT_TOKEN = env.str('SLACK_BOT_TOKEN')
    SLACK_APP_TOKEN = env.str('SLACK_APP_TOKEN')
