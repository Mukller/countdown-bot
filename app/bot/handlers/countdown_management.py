from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import CountdownRepository
from app.services import CountdownService
from app.core.logger import get_logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
logger = get_logger(__name__)


@router.callback_query(F.data.startswith("view_countdown:"))
async def view_countdown(callback: CallbackQuery, session: AsyncSession):
    countdown_id = int(callback.data.split(":")[1])

    countdown_repo = CountdownRepository(session)
    countdown = await countdown_repo.get_by_id(countdown_id)

    if not countdown:
        await callback.answer("❌ Таймер не найден", show_alert=True)
        return

    countdown_service = CountdownService(countdown_repo)
    card = countdown_service.format_countdown(countdown)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_countdown:{countdown_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="list_countdowns")],
        ]
    )

    await callback.message.edit_text(card, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_countdown:"))
async def delete_countdown(callback: CallbackQuery, session: AsyncSession):
    countdown_id = int(callback.data.split(":")[1])

    countdown_repo = CountdownRepository(session)
    success = await countdown_repo.delete(countdown_id)

    if success:
        logger.info("countdown_deleted", user_id=callback.from_user.id, countdown_id=countdown_id)
        await callback.answer("✅ Таймер удален")
        await callback.message.edit_text("✅ Таймер успешно удален")
        # Go back to list
        await callback.message.edit_text(
            "📋 Ваши таймеры:\n\n"
            "Перезагружаю список...",
            reply_markup=None
        )
    else:
        await callback.answer("❌ Не удалось удалить таймер", show_alert=True)
