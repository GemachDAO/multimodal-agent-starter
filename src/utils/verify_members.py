from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv, find_dotenv
config = find_dotenv()
load_dotenv(config)
api_id =os.getenv('API_ID')
api_hash =os.getenv('API_HASH')
session_string = str(os.getenv('SESSION_STRING'))
async def fetch_telegram_data(member_id:int)->bool:
        # Initialize the Telegram client
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
    is_member= False
    if member_id in members_list:
        is_member=True
    return is_member