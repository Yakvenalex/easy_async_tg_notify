import httpx
import logging
from typing import List, Optional, Union
from aiofiles import open as aio_open


class Notifier:
    """
    Асинхронный отправщик уведомлений через Telegram API.

    Аргументы:
        token: Токен бота Telegram.
        log_level: Уровень логирования.
    """

    def __init__(self, token: str, log_level: Optional[int] = logging.INFO) -> None:
        self._base_url = f'https://api.telegram.org/bot{token}/'
        self._client: Optional[httpx.AsyncClient] = None

        # Настройка логирования
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    async def _handle_request_exceptions(self, request_func: callable, *args, **kwargs) -> httpx.Response:
        """Обработка исключений для HTTP-запросов."""
        try:
            response = await request_func(*args, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Произошла ошибка HTTP: {e}")
            raise
        except httpx.RequestError as e:
            self.logger.error(f"Произошла ошибка запроса: {e}")
            raise

    async def __aenter__(self) -> 'Notifier':
        """Вход в контекст исполнения этого объекта."""
        self._client = httpx.AsyncClient(base_url=self._base_url)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Выход из контекста исполнения этого объекта."""
        if self._client:
            await self._client.aclose()

    async def send_text(self, text: str, to_chat_ids: Union[int, List[int]], parse_mode: Optional[str] = 'HTML') -> \
            List[httpx.Response]:
        """
        Отправить текстовое уведомление нескольким чатам или одному чату.

        Аргументы:
            text: Сообщение для отправки.
            to_chat_ids: Список или единичный ID чата.
            parse_mode: Режим форматирования текста (например, 'HTML' или 'Markdown').

        Возвращает:
            Список объектов httpx.Response.
        """
        if isinstance(to_chat_ids, int):
            to_chat_ids = [to_chat_ids]

        responses = []
        for chat_id in to_chat_ids:
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            try:
                response = await self._handle_request_exceptions(self._client.get, 'sendMessage', params=data)
                responses.append(response)
                self.logger.info(f"Сообщение отправлено в чат {chat_id}.")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
        return responses

    async def send_media(
            self, media_path: str, to_chat_ids: Union[int, List[int]], media_type: str, caption: Optional[str] = "",
            additional_params: Optional[dict] = None
    ) -> List[httpx.Response]:
        """
        Отправить медиафайл (фото, документ, аудио) нескольким чатам или одному чату.

        Аргументы:
            media_path: Путь к медиафайлу.
            to_chat_ids: Список или единичный ID чата.
            media_type: Тип медиафайла ('photo', 'document', 'audio', 'video').
            caption: Подпись к медиафайлу.
            additional_params: Дополнительные параметры запроса.

        Возвращает:
            Список объектов httpx.Response.
        """
        if isinstance(to_chat_ids, int):
            to_chat_ids = [to_chat_ids]

        responses = []
        for chat_id in to_chat_ids:
            data = {'chat_id': chat_id, 'caption': caption}
            if additional_params:
                data.update(additional_params)
            try:
                async with aio_open(media_path, "rb") as f:
                    media_file = await f.read()
                    # Используем 'files' параметр правильно
                    files = {media_type: (media_path, media_file, 'multipart/form-data')}
                    response = await self._handle_request_exceptions(
                        self._client.post, f'send{media_type.capitalize()}', data=data, files=files
                    )
                    responses.append(response)
                    self.logger.info(f"{media_type.capitalize()} отправлен в чат {chat_id}.")
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Ошибка HTTP при отправке {media_type} в чат {chat_id}: {e}")
            except httpx.RequestError as e:
                self.logger.error(f"Ошибка запроса при отправке {media_type} в чат {chat_id}: {e}")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке {media_type} в чат {chat_id}: {e}")
        return responses

    async def send_photo(self, photo_path: str, to_chat_ids: Union[int, List[int]], caption: str = "") -> List[
        httpx.Response]:
        return await self.send_media(photo_path, to_chat_ids, 'photo', caption)

    async def send_document(self, document_path: str, to_chat_ids: Union[int, List[int]],
                            caption: Optional[str] = "") -> List[httpx.Response]:
        return await self.send_media(document_path, to_chat_ids, 'document', caption)

    async def send_audio(self, audio_path: str, to_chat_ids: Union[int, List[int]], caption: Optional[str] = "") -> \
            List[httpx.Response]:
        return await self.send_media(audio_path, to_chat_ids, 'audio', caption)

    async def send_video(self, video_path: str, to_chat_ids: Union[int, List[int]], caption: Optional[str] = "") -> \
            List[httpx.Response]:
        return await self.send_media(video_path, to_chat_ids, 'video', caption)

    async def send_venue(self, latitude: float, longitude: float, title: str, address: str,
                         to_chat_ids: Union[int, List[int]]) -> List[httpx.Response]:
        """
        Отправить информацию о месте (venue) нескольким чатам или одному чату.

        Аргументы:
            latitude: Широта.
            longitude: Долгота.
            title: Название места.
            address: Адрес.
            to_chat_ids: Список или единичный ID чата.

        Возвращает:
            Список объектов httpx.Response.
        """
        if isinstance(to_chat_ids, int):
            to_chat_ids = [to_chat_ids]

        responses = []
        for chat_id in to_chat_ids:
            data = {
                'chat_id': chat_id,
                'latitude': latitude,
                'longitude': longitude,
                'title': title,
                'address': address
            }
            try:
                response = await self._handle_request_exceptions(self._client.get, 'sendVenue', params=data)
                responses.append(response)
                self.logger.info(f"Информация о месте отправлена в чат {chat_id}.")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке информации о месте в чат {chat_id}: {e}")
        return responses

    async def send_contact(self, phone_number: str, first_name: str, to_chat_ids: Union[int, List[int]],
                           last_name: Optional[str] = None,
                           ) -> List[httpx.Response]:
        """
        Отправить контактную информацию нескольким чатам или одному чату.

        Аргументы:
            phone_number: Номер телефона.
            first_name: Имя.
            last_name: Фамилия.
            to_chat_ids: Список или единичный ID чата.

        Возвращает:
            Список объектов httpx.Response.
        """
        if isinstance(to_chat_ids, int):
            to_chat_ids = [to_chat_ids]

        responses = []
        for chat_id in to_chat_ids:
            data = {
                'chat_id': chat_id,
                'phone_number': phone_number,
                'first_name': first_name,
                'last_name': last_name
            }
            try:
                response = await self._handle_request_exceptions(self._client.get, 'sendContact', params=data)
                responses.append(response)
                self.logger.info(f"Контакт отправлен в чат {chat_id}.")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке контакта в чат {chat_id}: {e}")
        return responses
