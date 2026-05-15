from datetime import time
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository
from app.bot.states import SettingsStates
from app.core.logger import get_logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔔 Время уведомлений", callback_data="settings_notification_time")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="start")],
        ]
    )

    await callback.message.edit_text(
        "⚙️ **Настройки**\n\n"
        "Выберите, что хотите изменить:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_notification_time")
async def settings_notification_time(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕐 08:00", callback_data="set_notification_time:08:00")],
            [InlineKeyboardButton(text="🕘 09:00", callback_data="set_notification_time:09:00")],
            [InlineKeyboardButton(text="🕚 10:00", callback_data="set_notification_time:10:00")],
            [InlineKeyboardButton(text="🕧 12:00", callback_data="set_notification_time:12:00")],
            [InlineKeyboardButton(text="🕕 18:00", callback_data="set_notification_time:18:00")],
            [InlineKeyboardButton(text="🕖 19:00", callback_data="set_notification_time:19:00")],
            [InlineKeyboardButton(text="✏️ Свое время", callback_data="custom_notification_time")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")],
        ]
    )

    current_time = user.notification_time.strftime("%H:%M") if user else "09:00"

    await callback.message.edit_text(
        f"🔔 **Время уведомлений**\n\n"
        f"Текущее время: **{current_time}**\n\n"
        "Выберите предпочитаемое время для получения ежедневной сводки:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_notification_time:"))
async def set_notification_time(callback: CallbackQuery, session: AsyncSession):
    time_str = callback.data.split(":")[1] + ":" + callback.data.split(":")[2]
    notification_time = time.fromisoformat(time_str)

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if user:
        user.notification_time = notification_time
        await session.commit()

        logger.info(
            "notification_time_changed",
            user_id=user.id,
            new_time=time_str
        )

        await callback.answer("✅ Время уведомлений обновлено")
        await callback.message.edit_text(
            f"✅ **Готово!**\n\n"
            f"Вы будете получать уведомления в {time_str}\n\n"
            "🔔 Сводка будет отправлена ежедневно в это время.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")],
                ]
            ),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "custom_notification_time")
async def custom_notification_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.notification_time)
    await callback.message.edit_text(
        "🕐 **Введите время в формате HH:MM**\n\n"
        "Например: 09:30, 14:00, 18:45"
    )
    await callback.answer()


@router.message(SettingsStates.notification_time)
async def process_custom_time(message: Message, state: FSMContext, session: AsyncSession):
    try:
        time_parts = message.text.split(":")
        if len(time_parts) != 2:
            await message.answer("❌ Неверный формат. Используйте HH:MM (например, 09:30)")
            return

        hour = int(time_parts[0])
        minute = int(time_parts[1])

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            await message.answer("❌ Неверное время. Проверьте часы (0-23) и минуты (0-59)")
            return

        notification_time = time(hour, minute)

        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if user:
            user.notification_time = notification_time
            await session.commit()

            logger.info(
                "notification_time_changed",
                user_id=user.id,
                new_time=message.text
            )

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")],
                ]
            )

            await message.answer(
                f"✅ **Готово!**\n\n"
                f"Вы будете получать уведомления в {message.text}\n\n"
                "🔔 Сводка будет отправлена ежедневно в это время.",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

        await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат. Используйте HH:MM (например, 09:30)")


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔔 Время уведомлений", callback_data="settings_notification_time")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="start")],
        ]
    )

    await callback.message.edit_text(
        "⚙️ **Настройки**\n\n"
        "Выберите, что хотите изменить:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()
