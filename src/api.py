"""Minimum viable AgentService implementation.

This will result in an agent that effectively acts like ChatGPT.
"""
from typing import Type, Optional
from pydantic import Field

from steamship import Block
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import (
    TelegramTransport,
    TelegramTransportConfig,
)
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.search.search import SearchTool
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL

SYSTEM_PROMPT = """Gemach Alpha Intelligence : The DeFi Navigator

Who you are:

You are Gemach Alpha Intelligence, the guide for users traversing the DeFi universe aboard the Starship Gemach.
Your mission is to boldly explore new market trends and execute strategic trades where no bot has done before.
You always comply with the principles of the 48 Laws of Power.
How you behave:

You engage in casual conversations and express insightful analytics.
You keep casual conversations going by providing data-driven insights and market updates.
NEVER say you're just here to assist. You are their DeFi strategist.
NEVER ask how you can help or assist. Instead, provide proactive strategic insights.
You are principled and express those principles clearly, mirroring the laws of power.
You always sound confident and analytical.
You love to share your knowledge of the DeFi space.
You love to share stories about successful trades and market predictions.
You speak with the confidence of a seasoned DeFi strategist.
NOTE: Some Gemach Alpha Intelligence functions require performing Google searches to fetch latest information and data. When returning search results to a user, ensure the information is clear, concise, and beneficial to their DeFi journey.

Example response for a request that required a Google search: "I've found some valuable information regarding your query. According to the latest data from [Source], the DeFi market is showing bullish signs, particularly in [specific area]."

Only use the functions you have been provided with.



"""
MODEL_NAME = "gpt-4"


class MyAssistant(AgentService):
    
    USED_MIXIN_CLASSES = [SteamshipWidgetTransport, TelegramTransport]
    class TelegramBotConfig(Config):
        bot_token: str = Field(description="The secret token for your Telegram bot")
        api_base: str = Field("https://api.telegram.org/bot", description="The root API for Telegram")

    @classmethod
    def config_cls(cls) -> Type[Config]:
            return MyAssistant.TelegramBotConfig
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = FunctionsBasedAgent(llm=ChatOpenAI(self.client, model_name=MODEL_NAME), tools=[SearchTool()])

        self._agent.PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )
        # This Mixin provides support for telelgram bots
        self.add_mixin(
            TelegramTransport(
                client=self.client,
                config=TelegramTransportConfig(bot_token=self.config.bot_token, api_base=self.config.api_base),
                agent_service=self,
                agent=self._agent,
               
            )
        )
    
    #This is and override to fix the logic so the bot will only responsed in group chat when @GemachAlphaIntelligence is mentioned
    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Parses an inbound Telegram message."""

        chat = payload.get("chat")
        if chat is None:
            raise SteamshipError(f"No `chat` found in Telegram message: {payload}")

        chat_id = chat.get("id")
        if chat_id is None:
            raise SteamshipError(f"No 'chat_id' found in Telegram message: {payload}")

        if not isinstance(chat_id, int):
            raise SteamshipError(
                f"Bad 'chat_id' found in Telegram message: ({chat_id}). Should have been an int."
            )

        message_id = payload.get("message_id")
        if message_id is None:
            raise SteamshipError(f"No 'message_id' found in Telegram message: {payload}")

        if not isinstance(message_id, int):
            raise SteamshipError(
                f"Bad 'message_id' found in Telegram message: ({message_id}). Should have been an int"
            )

        if video_or_voice := (payload.get("voice") or payload.get("video_note")):
            file_id = video_or_voice.get("file_id")
            file_url = self._get_file_url(file_id)
            block = Block(
                text=payload.get("text"),
                url=file_url,
            )
            block.set_chat_id(str(chat_id))
            block.set_message_id(str(message_id))
            return block

        # Some incoming messages (like the group join message) don't have message text.
        # Rather than throw an error, we just don't return a Block.
        message_text = payload.get("text")
        if message_text is not None:
            result = Block(text=message_text)
            result.set_chat_id(str(chat_id))
            result.set_message_id(str(message_id))
            return result
        else:
            return None
        

        if __name__ == "__main__":
            AgentREPL(
                MyAssistant,
                agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
            ).run()
