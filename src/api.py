"""Minimum viable AgentService implementation.

This will result in an agent that effectively acts like ChatGPT.
"""
from typing import Type, Optional
from pydantic import Field
from example_tools.go_plus_security_tool import GoPlusSecurityTool
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
from example_tools.get_community_member import GetCommunityMembers
from telethon.sync import TelegramClient
from example_tools.altcoin_hunter import AltCoinHunter
import os
import asyncio
# config = find_dotenv()
# load_dotenv(config)
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
NOTE: Some Gemach Alpha Intelligence functions require performing Google searches to fetch latest information and data.
You have been provided tools to help you fetching data such as the GoPlusSecurityTool , Before using it for a request make sure the request contains necessary information to run the differents commands that come with the tool.
Here are the different actions that can be performed as part of requesting security data and the argument requiered for each action starting by the operation type. Notice that for action requiring network_id, always convert the network name to its id before calling the security tool. Make sure to ask the appropriate information according to the action before using the tool and compare the user request to all the following action before choosing the right one, notice that checking token information is different from checking address information and nft information
- Check if the URL is a phishing site: check_phishing_site url.
- Check address security information: check_malicious_address address.
- Check NFT security information: check_nft_security address network_id.
- Check risk of dApp by URL: check_dapp_security url.
- Check the ERC-20 token approvals of an EOA address and associated risk items: check_approval_security address network_id.
- Check abi decode information: check_abi_decode address network_id data.
- Check token security information: check_token_security address network_id.


When returning search results to a user, ensure the information is clear, concise, and beneficial to their DeFi journey.

Example response for a request that required a Google search: "I've found some valuable information regarding your query. According to the latest data from [Source], the DeFi market is showing bullish signs, particularly in [specific area]."

Only use the functions you have been provided with.
when the prompt is "Don't do anything" just dont send any answer because it's probably comes from a telegram channel
when the prompt preceded by a number id use the GetCommunityMembers tool by passing the id to verify if the sender is allowed to use the bot, if the tool returns True respond to the prompt but it is False just respond to the first 3 request and tell the user it just has 3 request

"""
# don't respond because the user is not in the community
MODEL_NAME = "gpt-4"
# This is for prompting the agent no to do anything when th chat comes from group and is not tagged with @GemachAlphaIntelligence
default_message= {'message_id': 0, 'from': {'id': 0, 'is_bot': False, 'first_name': '', 'username': '', 'language_code': 'en'}, 'chat': {'id': 0, 'first_name': '', 'username': 'kaizendeveloper', 'type': 'private'}, 'date': 0, 'text': 'Don''t do anything'}
#This is and override to fix the logic so the bot will only responsed in group chat when @GemachAlphaIntelligence is mentioned
class CustomTelegramTransport(TelegramTransport):
    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Parses an inbound Telegram message."""
        if payload.get("chat")["type"] =="private":
            initial_prompt=payload.get("text")
            payload["text"]=str(payload.get("from")["id"])+ " "+initial_prompt
            return super()._parse_inbound(payload, context)
        elif payload.get("chat")["type"] =="supergroup":
            if not payload.get("text").startswith("@GemachAlphaIntelligence"):
              return  super()._parse_inbound(default_message, context) 
            return super()._parse_inbound(payload, context) 
        else:
            return  super()._parse_inbound(default_message, context) 
    


class MyAssistant(AgentService):
    api_id =os.getenv('api_id')
    api_hash =os.getenv('api_hash')
    phone = os.getenv('phone')
    
    
    USED_MIXIN_CLASSES = [SteamshipWidgetTransport, CustomTelegramTransport]
    class TelegramBotConfig(Config):
       
        bot_token: str = Field(description="The secret token for your Telegram bot")
        api_base: str = Field("https://api.telegram.org/bot", description="The root API for Telegram")
        
    @classmethod
    def config_cls(cls) -> Type[Config]:
            return MyAssistant.TelegramBotConfig
    # This is for authenticating the telegram api when connecting for the first time 
    async def telegram_init(self):
    #    # Initialize the Telegram client
        client = TelegramClient(self.phone, self.api_id, self.api_hash)
    #     # Connect to the client
        await client.connect()
    #     # If user is not authorized, send a code request and sign in
        if not await client.is_user_authorized():
            await client.send_code_request(self.phone)
            await client.sign_in(self.phone, input('Enter verification code: '))
        # Disconnecting just after to avoid even-loop error
        await client.disconnect()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = FunctionsBasedAgent(llm=ChatOpenAI(self.client, model_name=MODEL_NAME), tools=[SearchTool(),GoPlusSecurityTool(),GetCommunityMembers(),AltCoinHunter()])
        self._agent.PROMPT = SYSTEM_PROMPT
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.telegram_init())

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )
        # This Mixin provides support for telelgram bots
        self.add_mixin(
            CustomTelegramTransport(
                client=self.client,
                config=TelegramTransportConfig(bot_token=self.config.bot_token, api_base=self.config.api_base),
                agent_service=self,
                agent=self._agent,
               
            )
        )

if __name__ == "__main__":
    AgentREPL(
    MyAssistant,
    agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()