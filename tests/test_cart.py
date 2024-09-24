import pytest
from unittest.mock import AsyncMock
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import text
from unittest import mock

@pytest.mark.asyncio
async def test_add_to_cart_item_not_in_cart(monkeypatch):
    # Устанавливаем переменные окружения до импорта модуля
    monkeypatch.setenv("BOT_TOKEN", "fake_token")
    monkeypatch.setenv("GROUP_ID", "123456")
    monkeypatch.setenv("ADMINS", "12345,67890")
    monkeypatch.setenv("DB_URL", "postgresql+asyncpg://user:password@localhost/test_db")

    # Импортируем функцию после установки переменных окружения
    from app.handlers.common_handlers import add_to_cart

    # Создаем замокированный объект session
    session = AsyncMock()

    # Мокаем session.begin() чтобы он возвращал асинхронный контекстный менеджер
    session_context_manager = AsyncMock()
    session.begin.return_value = session_context_manager
    session_context_manager.__aenter__.return_value = session
    session_context_manager.__aexit__.return_value = None

    # Мокаем session.execute()
    # Первый вызов: получение пользователя
    user_result = AsyncMock()
    user_result.fetchone.return_value = AsyncMock(id=1)
    # Второй вызов: проверка товара в корзине
    cart_check_result = AsyncMock()
    cart_check_result.scalar.return_value = None  # Товара нет в корзине
    # Третий вызов: добавление товара в корзину
    insert_result = AsyncMock()

    # Устанавливаем side_effect для session.execute()
    session.execute.side_effect = [user_result, cart_check_result, insert_result]

    # Мокаем session.commit()
    session.commit = AsyncMock()

    # Создаем замокированные объекты состояния и коллбэк-запроса
    state = AsyncMock(spec=FSMContext)
    callback_query = AsyncMock()
    callback_query.from_user = AsyncMock()
    callback_query.from_user.id = 12345
    callback_query.data = "add_to_cart_1_2"

    # Запускаем тестируемую функцию
    await add_to_cart(callback_query, state, session)

    # Проверяем, что запрос на получение пользователя был выполнен
    session.execute.assert_any_call(
        text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
        {"telegram_id": 12345}
    )

    # Проверяем, что запрос на проверку товара в корзине был выполнен
    session.execute.assert_any_call(
        text("SELECT 1 FROM cart WHERE user_id = :user_id AND product_id = :product_id"),
        {"user_id": 1, "product_id": 2}
    )

    # Проверяем, что запрос на добавление товара в корзину был выполнен
    session.execute.assert_any_call(
        text("INSERT INTO cart (user_id, product_id) VALUES (:user_id, :product_id)"),
        {"user_id": 1, "product_id": 2}
    )

    # Проверяем, что была вызвана фиксация транзакции
    session.commit.assert_awaited()

    # Проверяем, что коллбэк был успешно вызван с сообщением о добавлении товара
    callback_query.answer.assert_awaited_with("Товар добавлен в корзину.")
