from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from app.cfg_reader import config
from app.keyboards import admin_keyboards as admin_kb
import app.keyboards.user_keyboards as user_kb
from app.filters.chat_type import ChatTypeFilter

from datetime import datetime

admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]
router = Router()
router.message.filter(ChatTypeFilter(chat_type=["private"]))
started_at = datetime.now().strftime("%Y-%m-%d %H:%M")


@router.message(F.text.lower() == 'управление')
async def go_to_admin_panel(message: types.Message):
    if message.from_user.id not in admin_ids:
        await message.answer('Я не знаю такой команды', reply_markup=user_kb.help_inline_keyboard())
    else:
        await message.answer(("fadf"))


@router.message(Command("adm_info"))
async def adm_info(message: types.Message, started_at: str):
    if message.from_user.id in admin_ids:
        await message.answer(f"Bot started at {started_at}")

