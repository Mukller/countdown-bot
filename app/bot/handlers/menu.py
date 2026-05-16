from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, CountdownRepository
from app.services import CountdownService, UserService, CalendarService
from app.ui.keyboards import main_menu, empty_state
from app.bot.states import CountdownStates
from app.core.logger import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data == "create_countdown")
async def cb_create_countdown(callback: CallbackQuery, state: FSMContext):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎂 День рождения", callback_data="template:birthday:🎂")],
            [InlineKeyboardButton(text="⛱️ Отпуск", callback_data="template:vacation:⛱️")],
            [InlineKeyboardButton(text="📚 Экзамен", callback_data="template:exam:📚")],
            [InlineKeyboardButton(text="✏️ Свой отсчёт", callback_data="create_custom")],
        ]
    )

    await callback.message.edit_text(
        "🎯 Выберите тип отсчёта или создайте свой:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("template:"))
async def create_from_template(callback: CallbackQuery, state: FSMContext):
    from datetime import date
    parts = callback.data.split(":")
    template_name = parts[1]
    emoji = parts[2]

    titles = {
        "birthday": "День рождения",
        "vacation": "Отпуск",
        "exam": "Экзамен",
    }

    title = titles.get(template_name, template_name)

    await state.update_data(title=title, emoji=emoji)
    await state.set_state(CountdownStates.date)

    today = date.today()
    calendar = CalendarService.get_calendar(today.year, today.month, today)

    await callback.message.edit_text(
        f"📅 Выберите дату события:\n\n"
        f"**{title}** {emoji}",
        reply_markup=calendar,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "create_custom")
async def create_custom_countdown(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CountdownStates.title)
    await callback.message.edit_text(
        "📝 Введите название отсчёта:\n\n"
        "Например: День рождения, Отпуск, Премьера фильма"
    )
    await callback.answer()


@router.callback_query(F.data == "list_countdowns")
async def cb_list_countdowns(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)
    user_service = UserService(user_repo)
    user = await user_service.get_or_create_user(callback.from_user.id)

    countdown_repo = CountdownRepository(session)
    countdown_service = CountdownService(countdown_repo)

    countdowns = await countdown_service.get_user_countdowns(user.id)

    if not countdowns:
        await callback.message.edit_text(
            "⏳ У вас пока нет отсчётов\n\n"
            "Создайте первый отсчёт 👇",
            reply_markup=empty_state()
        )
    else:
        await state.update_data(current_countdown_idx=0, countdown_ids=[c.id for c in countdowns])
        await _show_countdown_card(callback, countdowns[0], countdown_service, 0, len(countdowns))

    await callback.answer()


@router.callback_query(F.data.startswith("nav_countdown:"))
async def navigate_countdowns(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    direction = callback.data.split(":")[1]

    data = await state.get_data()
    current_idx = data.get("current_countdown_idx", 0)
    countdown_ids = data.get("countdown_ids", [])

    if direction == "next":
        current_idx = (current_idx + 1) % len(countdown_ids)
    elif direction == "prev":
        current_idx = (current_idx - 1) % len(countdown_ids)

    await state.update_data(current_countdown_idx=current_idx)

    countdown_repo = CountdownRepository(session)
    countdown = await countdown_repo.get_by_id(countdown_ids[current_idx])
    countdown_service = CountdownService(countdown_repo)

    await _show_countdown_card(callback, countdown, countdown_service, current_idx, len(countdown_ids))
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

    keyboard_buttons = []

    if total > 1:
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️", callback_data="nav_countdown:prev"),
            InlineKeyboardButton(text=f"{idx+1}/{total}", callback_data="noop"),
            InlineKeyboardButton(text="➡️", callback_data="nav_countdown:next"),
        ])

    keyboard_buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_countdown:{countdown.id}")])
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="start")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text(card, reply_markup=keyboard)
