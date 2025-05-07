import asyncio
import re
from telethon import TelegramClient, errors
from telethon.tl.custom import Message

API_ID = 24641445
API_HASH = "cbd16f1ca6464bf64338e45abd85ccdf"
SESSION_NAME = "session"
DEFAULT_BOT_USERNAME = 'username_to_id_bot'
DEFAULT_WAIT_TIME = 5

class TelegramIdFinder:
    def __init__(self, session_name: str, api_id: int, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = TelegramClient(session_name, api_id, api_hash)
        self._is_connected = False

    async def connect(self):
        if not self._is_connected and not self.client.is_connected():
            try:
                await self.client.start()
                self._is_connected = True
            except errors.SessionPasswordNeededError:
                raise
            except Exception as e:
                self._is_connected = False
                raise

    async def disconnect(self):
        if self._is_connected and self.client.is_connected():
            await self.client.disconnect()
            self._is_connected = False

    async def get_id_via_bot(
        self,
        username_to_find: str,
        bot_username: str = DEFAULT_BOT_USERNAME,
        wait_time: int = DEFAULT_WAIT_TIME
    ) -> str:
        if not self._is_connected:
            return None
        extracted_id = None
        try:
            try: bot_entity = await self.client.get_entity(bot_username)
            except (ValueError, errors.FloodWaitError, Exception): return None

            await self.client.send_message(bot_entity, username_to_find)
            #await asyncio.sleep(wait_time)
            await asyncio.sleep(1)
            messages = await self.client.get_messages(bot_entity, limit=5)
            if not messages: return None

            for msg in messages:
                if msg.text and not msg.out:
                    match = re.search(r"^id:\s*`?(\d+)`?", msg.text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_id = match.group(1)
                        break
        except errors.FloodWaitError as e:
            await asyncio.sleep(e.seconds + 1)
        except Exception: pass
        return extracted_id

    @property
    def is_ready(self) -> bool:
        return self._is_connected and self.client.is_connected()