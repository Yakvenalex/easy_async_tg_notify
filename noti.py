import asyncio
import os
from decouple import config
from easy_async_tg_notify import Notifier

token = config('TELEGRAM_BOT_TOKEN')
user_id = int(config('TELEGRAM_CHAT_ID'))
users_ids = [int(user_id) for user_id in config('TELEGRAM_CHAT_IDS').split(',')]

# Получаем абсолютный путь к директории, в которой находится текущий скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
photo = os.path.join(script_dir, 'telegram-logo-27.png')


async def main():
    async with Notifier(token) as notifier:
        await notifier.send_text("Привет, <b>дружище!</b>!", user_id)
        await notifier.send_photo(photo, users_ids)
        await notifier.send_document(photo, user_id, caption='Подпись к документу')
        await notifier.send_contact('+76398836055', 'Алексей', user_id)


asyncio.run(main())
