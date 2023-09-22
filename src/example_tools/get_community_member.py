from typing import Any, List, Union
from steamship.agents.schema import AgentContext, Tool
from steamship import Block
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from steamship.utils.repl import ToolREPL
from telethon.sessions import StringSession
import os
import asyncio

class GetCommunityMembers(Tool):
    """
    Custom tool for getting a list of GemachDao community .
    """
    name: str = "GetCommunityMembers"
    human_description: str = "Retrieve GemachDao community member list"
    agent_description: str = """
        Used to Retrieve GemachDao community member list 
    """
    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Any]:
        """
        Retrieve GemachDao community member list
        """
        # Create a new asyncio event loop and set it as the default loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Fetch telegram data asynchronously
        members_list = loop.run_until_complete(self.fetch_telegram_data())
        # Initialize output list and is_member flag
        output = []
        is_member= False
        for block in tool_input:
            if block.is_text():
                    if int(block.text) in members_list:
                        is_member=True
        output.append(Block(text=str(is_member)))
        return output
    # Define an asynchronous method to fetch data from Telegram
    async def fetch_telegram_data(self):
        # Telegram API credentials
        api_id =os.getenv('api_id')
        api_hash =os.getenv('api_hash')
        session_string = os.getenv('SESSION_STRING')
        # Initialize the Telegram client
        # client = TelegramClient(phone, api_id, api_hash)
        client= TelegramClient(StringSession(session_string), api_id, api_hash)
        # Connect to the client
        await client.connect()
        # Initialize variables to store chat data
        chats = []
        target_chat = None
        last_date = None
        chunk_size = 200
        # Fetch the list of chats
        result = await client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)
        # Find the target chat with the specified ID
        for chat in chats:
            try:
                if chat.megagroup == True and chat.id == 1531445636:
                    target_chat = chat
            except:
                continue
        # Fetch all participants of the target chat
        all_participants = await client.get_participants(target_chat, aggressive=True)
        members_list = []
        # for user in all_participants:
        #     members_list.append(user.id)
        members_list = [user.id for user in all_participants]
        # Disconnect the client
        await client.disconnect()
        return members_list

if __name__ == "__main__":
    tool = GetCommunityMembers()
    ToolREPL(tool).run()
