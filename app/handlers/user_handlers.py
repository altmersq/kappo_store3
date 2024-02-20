from aiogram import Router, F
from aiogram.types import Message
from aiogram import types
from aiogram.filters import Command
from app.cfg_reader import config
from app.keyboards import admin_keyboards as admin_kb
import app.keyboards.user_keyboards as user_kb


router = Router()

