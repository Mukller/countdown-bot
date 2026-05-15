from datetime import date
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, CountdownRepository
from app.services import CountdownService, UserService, CalendarService
from app.bot.states import CountdownStates
from app.core.logger import get_logger
from app.core.constants import REPEAT_TYPE_NONE, REPEAT_TYPE_YEARLY
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data == "calback")
async def back_from_calendar(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CountdownStates.title)
    await callback.message.edit_text(
        "📝 Введите название таймера:\n\n"
        "Например: День рождения, Отпуск, Премьера фильма"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("yearpick:"))
async def pick_year(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split(":")[1])

    await state.update_data(year=year)

    keyboard = CalendarService.get_year_selector(year)

    await callback.message.edit_text(
        "📅 Выберите год:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("yearchg:"))
async def change_year_decade(callback: CallbackQuery, state: FSMContext):
    start_year = int(callback.data.split(":")[1])

    keyboard = CalendarService.get_year_selector(start_year)

    await callback.message.edit_text(
        "📅 Выберите год:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("yearchosen:"))
async def choose_year(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split(":")[1])

    await state.update_data(year=year)

    keyboard = CalendarService.get_month_selector(year)

    await callback.message.edit_text(
        "📅 Выберите месяц:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("monthpick:"))
async def pick_month(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split(":")[1])

    await state.update_data(year=year)

    keyboard = CalendarService.get_month_selector(year)

    await callback.message.edit_text(
        "📅 Выберите месяц:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("monthchosen:"))
async def choose_month(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    year = int(parts[1])
    month = int(parts[2])

    await state.update_data(year=year, month=month)

    keyboard = CalendarService.get_calendar(year, month, date.today())

    await callback.message.edit_text(
        "📅 Выберите день:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cal:"))
async def navigate_calendar(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    month = int(parts[1])
    year = int(parts[2])

    data = await state.get_data()
    saved_year = data.get("year", year)

    await state.update_data(year=saved_year, month=month)

    keyboard = CalendarService.get_calendar(saved_year, month, date.today())

    await callback.message.edit_text(
        "📅 Выберите день:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("calday:"))
async def select_day(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    parts = callback.data.split(":")
    year = int(parts[1])
    month = int(parts[2])
    day = int(parts[3])

    selected_date = date(year, month, day)

    today = date.today()
    if selected_date <= today:
        await callback.answer("❌ Дата должна быть в будущем", show_alert=True)
        return

    data = await state.get_data()
    title = data.get("title")
    emoji = data.get("emoji")

    await state.update_data(date=selected_date)
    await state.set_state(CountdownStates.repeat)

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


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()
