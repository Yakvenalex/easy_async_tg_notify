# easy_async_tg_notify

```markdown
`easy_async_tg_notify` простая асинхронная библиотека, которая позволит вам без заморочек настроить отправку текстовых,
фото, видео, аудио и прочих уведомлений в телеграмм под свои задачи и проекты. Библиотека работает на чистом API 
телеграмм. Для асинхронности используется httpx.

```

## Особенности

- **Асинхронная работа**: Благодаря этому вы сможете легко интегрировать библиотеку в любой свой проект без блокировок.
- **Отправка любых форматов сообщений**: Библиотека позволит вам отправить: фото, видео, тексты, геоданные и т.д
- **Стилизация текста**: Вы можете отправлять красиво отформатированные сообщения (по умолчанию HTML)
- **Поддержка with**: Благодоря этому вы сможете выстраивать серию из отправок сообщений, вплетая своим функции в соединение с API
- **Отправка уведомлений одному или нескольким пользователям**: На входе принимается или TelegramID пользователя или список
- **Logging**: Настраиваемый логгер, который позволит отследить любые события и ошибки

## Установка

Установить библиотеку можно через pip

```bash
pip install --upgrade easy_async_tg_notify
```

## Пример использования

```python
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

```

## License

Этот проект лицензируется по лицензии [MIT](https://choosealicense.com/licenses/mit/).
