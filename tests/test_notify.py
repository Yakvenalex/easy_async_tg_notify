import os
import pytest
from decouple import config
from easy_async_tg_notify import Notifier


@pytest.fixture
def get_config():
    return {
        'TELEGRAM_BOT_TOKEN': config('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': int(config('TELEGRAM_CHAT_ID')),
        'TELEGRAM_CHAT_IDS': [int(user_id) for user_id in config('TELEGRAM_CHAT_IDS').split(',')],
        'PHOTO': os.path.join(os.path.dirname(__file__), 'telegram-logo-27.png'),
        'INVALID_CHAT_ID': -1,  # Пример несуществующего чата
        'INVALID_TOKEN': 'INVALID_TOKEN'  # Пример невалидного токена
    }


@pytest.mark.asyncio
async def test_send_text(get_config):
    token = get_config['TELEGRAM_BOT_TOKEN']
    user_id = get_config['TELEGRAM_CHAT_ID']

    async with Notifier(token) as notifier:
        response = await notifier.send_text("Привет, <b>дружище!</b>!", user_id)
        assert response[0].status_code == 200


@pytest.mark.asyncio
async def test_send_photo(get_config):
    token = get_config['TELEGRAM_BOT_TOKEN']
    user_ids = get_config['TELEGRAM_CHAT_IDS']
    photo_path = get_config['PHOTO']
    user_id = get_config['TELEGRAM_CHAT_ID']

    async with Notifier(token) as notifier:
        response_user = await notifier.send_photo(photo_path, user_id)
        response_users = await notifier.send_photo(photo_path, user_ids)

        assert response_user[0].status_code == 200
        assert all(resp.status_code == 200 for resp in response_users)


@pytest.mark.asyncio
async def test_send_document(get_config):
    token = get_config['TELEGRAM_BOT_TOKEN']
    user_id = get_config['TELEGRAM_CHAT_ID']
    photo_path = get_config['PHOTO']

    async with Notifier(token) as notifier:
        response = await notifier.send_document(photo_path, user_id, caption='Подпись к документу')
        assert response[0].status_code == 200


@pytest.mark.asyncio
async def test_send_contact(get_config):
    token = get_config['TELEGRAM_BOT_TOKEN']
    user_id = get_config['TELEGRAM_CHAT_ID']

    async with Notifier(token) as notifier:
        response = await notifier.send_contact('+76398836055', 'Алексей', to_chat_ids=user_id)
        assert response[0].status_code == 200


@pytest.mark.asyncio
async def test_send_text_invalid_token(get_config):
    invalid_token = get_config['INVALID_TOKEN']
    user_id = get_config['TELEGRAM_CHAT_ID']

    async with Notifier(invalid_token) as notifier:
        with pytest.raises(Exception):
            await notifier.send_text("Привет, <b>дружище!</b>!", user_id)


@pytest.mark.asyncio
async def test_send_text_invalid_chat_id(get_config):
    token = get_config['TELEGRAM_BOT_TOKEN']
    invalid_chat_id = get_config['INVALID_CHAT_ID']

    async with Notifier(token) as notifier:
        response = await notifier.send_text("Привет, <b>дружище!</b>!", invalid_chat_id)
        assert response[0].status_code != 200


@pytest.mark.asyncio
async def test_send_photo_invalid_path(get_config):
    token = get_config['TELEGRAM_BOT_TOKEN']
    user_id = get_config['TELEGRAM_CHAT_ID']
    invalid_photo_path = 'invalid/path/to/photo.png'

    async with Notifier(token) as notifier:
        with pytest.raises(FileNotFoundError):  # Замените на конкретное исключение, если оно другое
            await notifier.send_photo(invalid_photo_path, user_id)


@pytest.mark.asyncio
async def test_send_text_markdown(get_config):
    token = get_config['TELEGRAM_BOT_TOKEN']
    user_id = get_config['TELEGRAM_CHAT_ID']

    async with Notifier(token) as notifier:
        response = await notifier.send_text("Привет, *дружище!*", user_id, parse_mode='Markdown')
        assert response[0].status_code == 200
