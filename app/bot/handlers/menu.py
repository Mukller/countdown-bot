from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, CountdownRepository
from app.services import CountdownService
from app.ui.keyboards import main_menu, empty_state
from app.bot.states import CountdownStates
from app.core.logger import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data == "create_countdown")
async def cb_create_countdown(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CountdownStates.title)
    await callback.message.edit_text(
        "📝 Введите название таймера:\n\n"
        "Например: День рождения, Отпуск, Премьера фильма"
    )
    await callback.answer()


@router.callback_query(F.data == "list_countdowns")
async def cb_list_countdowns(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_id = callback.from_user.id
    countdown_repo = CountdownRepository(session)
    countdown_service = CountdownService(countdown_repo)

    countdowns = await countdown_service.get_user_countdowns(user_id)

    if not countdowns:
        await callback.message.edit_text(
            "⏳ У вас пока нет таймеров\n\n"
            "Создайте первый countdown 👇",
            reply_markup=empty_state()
        )
    else:
        await state.update_data(current_countdown_idx=0, countdowns=[c.id for c in countdowns])
        await _show_countdown_card(callback, countdowns[0], countdown_service, 0, len(countdowns))

    await callback.answer()


@router.callback_query(F.data == "settings")
async def cb_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ Настройки\n\n"
        "Скоро будут доступны более детальные настройки",
        reply_markup=__back_menu()
    )
    await callback.answer()


def __back_menu():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="start")],
        ]
    )


async def _show_countdown_card(callback: CallbackQuery, countdown, service, idx: int, total: int):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    card = service.format_countdown(countdown)
    nav_text = f"⬅️ {idx+1}/{total} ➡️"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=nav_text, callback_data="noop")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_countdown:{countdown.id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="start")],
        ]
    )

    await callback.message.edit_text(card, reply_markup=keyboard)
