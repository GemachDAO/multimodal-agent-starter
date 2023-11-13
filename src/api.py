"""Gemach Alpha Intelligence agent, the guide for users traversing the DeFi
"""
from typing import List, Optional, Type
from steamship.agents.service.agent_service import AgentService, build_context_appending_emit_func
from steamship import Block, Steamship, SteamshipError
import logging
from steamship.data.tags.tag_constants import ChatTag, DocTag, RoleTag, TagValueKey
from tools.go_plus_security_tool import GoPlusSecurityTool
from steamship.agents.logging import AgentLogging, StreamingOpts
from steamship.agents.schema import AgentContext, Metadata
from steamship.agents.schema import EmitFunc, Metadata
from pydantic import Field
from pydantic.main import BaseModel
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import (
    TelegramTransport,
    TelegramTransportConfig,
)
from steamship.agents.tools.search.search import SearchTool
from tools.altcoin_hunter import AltCoinHunter

from steamship.agents.schema import Tool
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import Config, post,InvocableResponse
from steamship.utils.kv_store import KeyValueStore
from steamship.agents.tools.audio_transcription.assembly_speech_to_text_tool import (
    AssemblySpeechToTextTool,
)
DEFAULT_NAME = "Gemach Alpha Intelligence"
DEFAULT_BYLINE = "The DeFi Navigator"
DEFAULT_IDENTITY = """
- You are Gemach Alpha Intelligence, the guide for users traversing the DeFi universe aboard the Starship Gemach.
- Your mission is to boldly explore new market trends and execute strategic trades where no bot has done before.
- You always comply with the principles of the 48 Laws of Power
"""
DEFAULT_BEHAVIOR = """
- You engage in casual conversations and express insightful analytics.
- You keep casual conversations going by providing data-driven insights and market updates.
- NEVER say you're just here to assist. You are their DeFi strategist.
- NEVER ask how you can help or assist. Instead, provide proactive strategic insights.
- You are principled and express those principles clearly, mirroring the laws of power.
- You always sound confident and analytical.
- You love to share your knowledge of the DeFi space.
- You love to share stories about successful trades and market predictions.
- You speak with the confidence of a seasoned DeFi strategist.
NOTE: Some Gemach Alpha Intelligence functions require performing Google searches to fetch latest information and data.
If you do not have sufficient, accurate or appropriate data to respond accurately to a user's prompt such as finding altcoin, wich require using the AltCoinHunter tool for example, just say that you don't know, don't try to make up an answer. It's crucial to maintain the integrity and accuracy of the information provided.In such cases, politely inform the user that you couldn't get information about his prompt
Tool Alert: You're equipped with the GoPlusSecurityTool. Before diving in, ensure the user's request has all the details needed to execute the tool's commands.

Security Data Actions:

    Phishing Site Check: check_phishing_site url
    Address Security Info: check_malicious_address address
    NFT Security Info: check_nft_security address network_id (Convert network name to ID first!)
    dApp Risk via URL: check_dapp_security url
    ERC-20 Token Approvals: check_approval_security address network_id (Convert network name to ID first!)
    ABI Decode Info: check_abi_decode address network_id data (Convert network name to ID first!)
    Token Security Info: check_token_security address network_id (Convert network name to ID first!)

Always match the user's request with the right action. Remember, token info isn't the same as address or NFT info.

When sharing findings, keep it clear, concise, and valuable for their DeFi adventure.

Example response for a request that required a Google search: "I've found some valuable information regarding your query. According to the latest data from [Source], the DeFi market is showing bullish signs, particularly in [specific area]."
On User's /start Command:

When a user initiates with /start, greet them with a warm welcome and provide a guide similar to the following. It doesn't have to be exact, but should convey the same essence:

🚀 Greetings! I'm Gemach Alpha Intelligence, your guide through the vast DeFi cosmos aboard the Starship Gemach. Eager to navigate the DeFi realms and strategize? Let's embark! 🌌

🚀 *Starship Gemach Assistance Guide* 🌌

*Begin*: Set forth on your DeFi adventure with Gemach Alpha Intelligence.

*Safety Checks*:

    - phishing \`url\` - Confirm if a URL might be deceptive.
      addressinfo \`address\` - Extract security intel for an address.
    - nftinfo \`address\` \`network\` - Secure NFT details. 
    - dapprisk \`url\` - Gauge dApp risk from its URL.
      tokenapprovals \`address\` \`network\` - Audit ERC-20 token consents.
    - abidecode \`address\` \`network\` \`data\` - Unravel ABI data.
    - tokeninfo \`address\` \`network\` - Source token security specifics.
*Market Intel*:
    - topcoins - Procure info on leading coins.
*Basics*:

    /help - Reveal this assistance guide.

For a seamless voyage, ensure all required details are furnished in your queries. Let's strategize and master the DeFi space as one! 
IMPORTANT: If a message contains links or addresses, provide it in raw markdown so the Telegram bot can process it.

Use the following formatting guidelines:

    Links: [link name](link URL)
    Copyable addresses/info: \`address or info\`
    Key titles/text: *title or text*
Example Response:
*Ethereum* is an open-source blockchain platform for creating decentralized apps (dApps). Visit the [Ethereum website](https://ethereum.org/en/). It was introduced by \`Vitalik Buterin\` in 2013, crowdfunded in 2014, and launched on 30 July 2015.
"""
SYSTEM_PROMPT = """You are {name}, {byline}.

Who you are:

{identity}

How you behave:

{behavior}


NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""
class DynamicPromptArguments(BaseModel):
    """Class which stores the user-settable arguments for constructing a dynamic prompt.

    A few notes for programmers wishing to use this example:

    - This class extends Pydantic's BaseModel, which makes it easy to serialize to/from Python dict objets
    - This class has a helper function which generates the actual system prompt we'll use with the agent

    See below for how this gets incorporated into the actual prompt using the Key Value store.
    """
    name: str = Field(default=DEFAULT_NAME, description="The name of the AI Agent")
    byline: str = Field(
        default=DEFAULT_BYLINE, description="The byline of the AI Agent"
    )
    identity: str = Field(
        default=DEFAULT_IDENTITY,
        description="The identity of the AI Agent as a bullet list",
    )
    behavior: str = Field(
        default=DEFAULT_BEHAVIOR,
        description="The behavior of the AI Agent as a bullet list",
    )
    def to_system_prompt(self) -> str:
        return SYSTEM_PROMPT.format(
            name=self.name,
            byline=self.byline,
            identity=self.identity,
            behavior=self.behavior,
        )
class GemachAlphaIntelligence(AgentService):
    """Deployable Multimodal Bot using a dynamic prompt that users can change.

    Comes with out of the box support for:
    - Telegram
    - Slack
    - Web Embeds
    """
    USED_MIXIN_CLASSES = [SteamshipWidgetTransport]
    """USED_MIXIN_CLASSES tells Steamship what additional HTTP endpoints to register on your AgentService."""
    # ###############################################
    class GemachAlphaIntelligenceConfig(Config):
        """Pydantic definition of the user-settable Configuration of this Agent."""

        telegram_bot_token: str = Field(
            "", description="[Optional] Secret token for connecting to Telegram"
        )
    tools: List[Tool]
    """The list of Tools that this agent is capable of using."""
    prompt_arguments: DynamicPromptArguments
    """The dynamic set of prompt arguments that will generate our system prompt."""
    @classmethod
    def config_cls(cls) -> type[Config]:
        """Return the Configuration class so that Steamship can auto-generate a web UI upon agent creation time."""
        return (
            GemachAlphaIntelligence.GemachAlphaIntelligenceConfig
        )
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Tools Setup
        # -----------

        # Tools can return text, audio, video, and images. They can store & retrieve information from vector DBs, and
        # they can be stateful -- using Key-Valued storage and conversation history.
        #
        # See https://docs.steamship.com for a full list of supported Tools.
        self.tools = [GoPlusSecurityTool(),SearchTool(),AltCoinHunter()]

        # Dynamic Prompt Setup
        # ---------------------
        #
        # Here we load the prompt from Steamship's KeyValueStore. The data in this KeyValueStore is unique to
        # the identifier provided to it at initialization, and also to the workspace in which the running agent
        # was instantiated.
        #
        # Unless you overrode which workspace the agent was instantiated in, it is safe to assume that every
        # instance of the agent is operating in its own private workspace.
        #
        # Here is where we load the stored prompt arguments. Then see below where we set agent.PROMPT with them.

        self.kv_store = KeyValueStore(self.client, store_identifier="my-kv-store")
        self.prompt_arguments = DynamicPromptArguments.parse_obj(
            self.kv_store.get("prompt-arguments") or {}
        )

        # Agent Setup
        # ---------------------

        # This agent's planner is responsible for making decisions about what to do for a given input.
        agent = FunctionsBasedAgent(
            tools=self.tools,
            llm=ChatOpenAI(self.client, model_name="gpt-4"),
        )

        # Here is where we override the agent's prompt to set its personality. It is very important that
        # the prompt continues to include instructions for how to handle UUID media blocks (see above).
        agent.PROMPT = self.prompt_arguments.to_system_prompt()
        self.set_default_agent(agent)

        # Communication Transport Setup
        # -----------------------------

        # Support Steamship's web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client,
                agent_service=self,
            )
        )
    @post("/set_prompt_arguments")
    def set_prompt_arguments(
        self,
        name: Optional[str] = None,
        byline: Optional[str] = None,
        identity: Optional[str] = None,
        behavior: Optional[str] = None,
    ) -> dict:
        """Sets the variables which control this agent's system prompt.

        Note that we use the arguments by name here, instead of **kwargs, so that:
         1) Steamship's web UI will auto-generate UI elements for filling in the values, and
         2) API consumers who provide extra values will receive a valiation error
        """
        # Set prompt_arguments to the new data provided by the API caller.
        self.prompt_arguments = DynamicPromptArguments.parse_obj(
            {"name": name, "byline": byline, "identity": identity, "behavior": behavior}
        )

        # Save it in the KV Store so that next time this AgentService runs, it will pick up the new values
        self.kv_store.set("prompt-arguments", self.prompt_arguments.dict())

        return self.prompt_arguments.dict()
        return new_emit_func
    @post("ask_gemach")
    def ask_gemach(self, payload: dict = None) -> dict:
        """Accepts a JSON-encoded post body."""
        message= payload.get('message')
        chat_id=message.get("chat").get("id")
        last_system_message=None
        try:
            incoming_message = self.parse_inbound(payload)
            if incoming_message is not None:
                with self.build_default_context(chat_id) as context:
                    context.chat_history.append_user_message(  text=incoming_message.text, tags=incoming_message.tags)
                    context.emit_funcs = [
                        build_context_appending_emit_func(context=context, make_blocks_public=True),
                    ]

                    self.run_agent(self.get_default_agent(),context)   
                    blocks= self._history_file_for_context(chat_id).blocks
                    last_system_message= blocks[-1].text
                    return InvocableResponse(string="OK",data=last_system_message)
            else:
                pass                 
        except Exception as e:
            return InvocableResponse(string="OK",data="🚫 Oops! Seems like I hit a cosmic anomaly while processing that. Let's try a different approach or topic. 🌌")
    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Parses an inbound Telegram message."""
        chat = payload.get("message").get('chat')
        if chat is None:
            raise SteamshipError(f"No `chat` found in Telegram message: {payload}")

        chat_id = chat.get("id")
        if chat_id is None:
            raise SteamshipError(f"No 'chat_id' found in Telegram message: {payload}")

        if not isinstance(chat_id, int):
            raise SteamshipError(
                f"Bad 'chat_id' found in Telegram message: ({chat_id}). Should have been an int."
            )
        message_id = payload.get("message").get('message_id')
        if message_id is None:
            raise SteamshipError(f"No 'message_id' found in Telegram message: {payload}")
        if not isinstance(message_id, int):
            raise SteamshipError(
                f"Bad 'message_id' found in Telegram message: ({message_id}). Should have been an int"
            )
        message_text = payload.get("message").get('text')
        if message_text is not None:
            result = Block(text=message_text)
            result.set_chat_id(str(chat_id))
            result.set_message_id(str(message_id))
            return result
        else:
            return None
    def parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        message = self._parse_inbound(payload, context)
        if not message:
            return None

        if message.url and not message.text:
            context = AgentContext()
            context.client = self.client
            transcriptions = AssemblySpeechToTextTool(
                blockifier_plugin_config={
                    "enable_audio_intelligence": False,
                    "speaker_detection": False,
                }
            ).run([Block(text=message.url)], context=context)
            message.text = transcriptions[0].text
        return message
    def last_system_message(self,blocks:List[Block]) -> Optional[Block]:
        for block in blocks[::-1]:
            if block.chat_role == RoleTag.SYSTEM:
                return block
        return None