from datetime import datetime, timedelta, date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, CountdownRepository
from app.services import CountdownService, UserService
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

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Завтра", callback_data="date:tomorrow")],
        [InlineKeyboardButton(text="📅 Через неделю", callback_data="date:week")],
        [InlineKeyboardButton(text="📆 Через месяц", callback_data="date:month")],
    ])

    await message.answer(
        f"📅 **{title}** {emoji}\n\n"
        "Выберите дату или введите вручную\n\n"
        "Формат для ввода: **ДД.МММ.ГГГГ**\n"
        "Пример: **16.05.2026**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("date:"), CountdownStates.date)
async def process_quick_date(callback: CallbackQuery, state: FSMContext):
    date_type = callback.data.split(":")[1]
    today = date.today()

    if date_type == "tomorrow":
        target_date = today + timedelta(days=1)
    elif date_type == "week":
        target_date = today + timedelta(days=7)
    elif date_type == "month":
        target_date = today + timedelta(days=30)
    else:
        return

    await state.update_data(date=target_date)
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
        f"Дата: **{target_date.strftime('%d.%m.%Y')}**\n\n"
        "Повторение:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(CountdownStates.date)
async def process_date(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Введите дату или выберите быстрый вариант")
        return

    try:
        target_date = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте: ДД.МММ.ГГГГ\nНапример: 16.05.2026")
        return

    today = date.today()
    if target_date <= today:
        await message.answer("❌ Дата должна быть в будущем")
        return

    await state.update_data(date=target_date)
    await state.set_state(CountdownStates.repeat)

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Без повтора", callback_data=f"repeat:{REPEAT_TYPE_NONE}")],
        [InlineKeyboardButton(text="🔁 Каждый год", callback_data=f"repeat:{REPEAT_TYPE_YEARLY}")],
    ])

    await message.answer(
        f"📅 **{title}** {emoji}\n"
        f"Дата: **{target_date.strftime('%d.%m.%Y')}**\n\n"
        "Повторение:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


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


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()
