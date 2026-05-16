from datetime import datetime, date
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

    emojis = ["🎂", "🎉", "🎄", "🎁", "⛱️", "🏖️", "📅", "✈️", "🚗", "💒", "👶", "🐶", "📚", "🎮", "🎬", "🎵", "💍", "🏆"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=emoji, callback_data=f"emoji:{emoji}") for emoji in emojis[i:i+4]]
            for i in range(0, len(emojis), 4)
        ]
    )

    await message.answer(
        f"✨ Название: **{message.text}**\n\n"
        "Выберите эмодзи:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("emoji:"), CountdownStates.emoji)
async def process_emoji(callback: CallbackQuery, state: FSMContext):
    emoji = callback.data.split(":")[1]

    await state.update_data(emoji=emoji)
    await state.set_state(CountdownStates.date)

    data = await state.get_data()
    title = data.get("title")

    keyboard = CalendarService.get_year_selector()

    await callback.message.edit_text(
        f"📅 **{title}** {emoji}\n\n"
        "Выберите год:",
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


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()
