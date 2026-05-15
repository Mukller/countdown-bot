from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, CountdownRepository
from app.services import UserService, CountdownService
from app.ui.keyboards import main_menu, empty_state
from app.core.logger import get_logger

router = Router()
logger = get_logger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)
    user_service = UserService(user_repo)

    user = await user_service.get_or_create_user(message.from_user.id)

    logger.info("start_handler", user_id=user.id, telegram_id=user.telegram_id)

    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в Countdown Bot!\n\n"
        "Создавайте таймеры до важных событий и получайте ежедневные напоминания.",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "start")
async def cb_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 Главное меню",
        reply_markup=main_menu()
    )
    await callback.answer()
