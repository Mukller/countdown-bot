from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, CountdownRepository
from app.services import CountdownService, UserService, CalendarService
from app.bot.states import CountdownStates
from app.core.constants import MAX_TITLE_LENGTH, REPEAT_TYPE_NONE, REPEAT_TYPE_YEARLY
from app.core.logger import get_logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
logger = get_logger(__name__)


@router.message(CountdownStates.title)
async def process_title(message: Message, state: FSMContext):
    if not message.text or len(message.text) > MAX_TITLE_LENGTH:
        await message.answer("❌ Название должно быть от 1 до 255 символов")
        return

    await state.update_data(title=message.text)
    await state.set_state(CountdownStates.emoji)
    await message.answer(
        f"✨ Название: **{message.text}**\n\n"
        "Выберите emoji:\n\n"
        "🎂 🎉 🎄 🎁 ⛱️ 🏖️ 📅 ✈️ 🚗 💒 👶 🐶 📚 🎮 🎬 🎵 💍 🏆",
        parse_mode="Markdown"
    )


@router.message(CountdownStates.emoji)
async def process_emoji(message: Message, state: FSMContext):
    emoji = message.text
    if not emoji or len(emoji) > 2:
        await message.answer("❌ Введите одиночный emoji")
        return

    await state.update_data(emoji=emoji)
    await state.set_state(CountdownStates.date)

    data = await state.get_data()
    title = data.get("title")

    today = date.today()
    buttons = []

    for i in range(1, 8):
        d = today + timedelta(days=i)
        buttons.append([InlineKeyboardButton(
            text=f"+{i} день" if i == 1 else f"+{i} дней",
            callback_data=f"quickdate:{d.year}:{d.month}:{d.day}"
        )])

    buttons.append([InlineKeyboardButton(text="📅 Выбрать другую дату", callback_data="custom_date")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        f"📅 **{title}** {emoji}\n\nВыберите дату:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("quickdate:"), CountdownStates.date)
async def process_quickdate(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    year = int(parts[1])
    month = int(parts[2])
    day = int(parts[3])

    selected_date = date(year, month, day)
    await state.update_data(date=selected_date)
    await state.set_state(CountdownStates.repeat)

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Без повтора", callback_data=f"repeat:{REPEAT_TYPE_NONE}")],
        [InlineKeyboardButton(text="🔁 Каждый год", callback_data=f"repeat:{REPEAT_TYPE_YEARLY}")],
    ])

    await callback.message.edit_text(
        f"📅 **{title}** {emoji}\n"
        f"Дата: **{selected_date.strftime('%d.%m.%Y')}**\n\n"
        "Повторение:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "custom_date", CountdownStates.date)
async def custom_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CountdownStates.year)

    year_selector = CalendarService.get_year_selector(date.today().year)

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")

    await callback.message.edit_text(
        f"📅 **{title}** {emoji}\n\nВыберите год:",
        reply_markup=year_selector,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("yearchosen:"), CountdownStates.year)
async def process_year(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split(":")[1])
    await state.update_data(year=year)
    await state.set_state(CountdownStates.month)

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")

    month_selector = CalendarService.get_month_selector(year)
    await callback.message.edit_text(
        f"📅 **{title}** {emoji}\n\nВыберите месяц:",
        reply_markup=month_selector,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("monthchosen:"), CountdownStates.month)
async def process_month(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    year = int(parts[1])
    month = int(parts[2])

    await state.update_data(month=month)
    await state.set_state(CountdownStates.date)

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")

    calendar = CalendarService.get_calendar(year, month, date.today())
    await callback.message.edit_text(
        f"📅 **{title}** {emoji}\n\nВыберите дату:",
        reply_markup=calendar,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("calday:"), CountdownStates.date)
async def process_date(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    year = int(parts[1])
    month = int(parts[2])
    day = int(parts[3])

    selected_date = date(year, month, day)
    today = date.today()

    if selected_date < today:
        await callback.answer("❌ Прошлая дата", show_alert=True)
        return

    await state.update_data(date=selected_date)
    await state.set_state(CountdownStates.repeat)

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Без повтора", callback_data=f"repeat:{REPEAT_TYPE_NONE}")],
        [InlineKeyboardButton(text="🔁 Каждый год", callback_data=f"repeat:{REPEAT_TYPE_YEARLY}")],
    ])

    await callback.message.edit_text(
        f"📅 **{title}** {emoji}\n"
        f"Дата: **{selected_date.strftime('%d.%m.%Y')}**\n\n"
        "Повторение:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("repeat:"), CountdownStates.repeat)
async def process_repeat(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    repeat_type = callback.data.split(":")[1]

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")
    target_date = data.get("date")

    user_repo = UserRepository(session)
    user_service = UserService(user_repo)
    user = await user_service.get_or_create_user(callback.from_user.id)

    countdown_repo = CountdownRepository(session)
    countdown_service = CountdownService(countdown_repo)

    countdown = await countdown_service.create_countdown(
        user_id=user.id,
        title=title,
        emoji=emoji,
        target_date=target_date,
        repeat_type=repeat_type
    )

    card = countdown_service.format_countdown(countdown)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Меню", callback_data="start")],
    ])

    await callback.message.edit_text(
        f"✅ Создано!\n\n{card}",
        reply_markup=keyboard
    )

    await state.clear()
    logger.info("countdown_created", user_id=user.id, countdown_id=countdown.id)
    await callback.answer()


@router.callback_query(F.data.startswith("cal:"), CountdownStates.date)
async def navigate_calendar(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    month = int(parts[1])
    year = int(parts[2]) if len(parts) > 2 else date.today().year

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    calendar = CalendarService.get_calendar(year, month, date.today())
    await callback.message.edit_text(
        "📅 Выберите дату:",
        reply_markup=calendar
    )
    await callback.answer()


@router.callback_query(F.data.startswith("yearchg:"), CountdownStates.year)
async def change_year_decade(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split(":")[1])
    year_selector = CalendarService.get_year_selector(year)
    await callback.message.edit_text(
        "📅 Выберите год:",
        reply_markup=year_selector
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()
