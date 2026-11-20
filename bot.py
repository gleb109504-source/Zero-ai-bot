import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

router = Router()


class BookingForm(StatesGroup):
    choosing_service = State()
    choosing_time = State()
    entering_contact = State()


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записаться на услугу / демо", callback_data="book")],
            [InlineKeyboardButton(text="💼 Услуги и цены", callback_data="prices")],
            [InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq")],
        ]
    )


def services_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Telegram-бот (от 5 000 ₽)", callback_data="srv:Telegram-бот")],
            [InlineKeyboardButton(text="🌐 Сайт / Лендинг (от 7 000 ₽)", callback_data="srv:Сайт / Лендинг")],
            [InlineKeyboardButton(text="📊 CRM и таблица (от 5 000 ₽)", callback_data="srv:CRM и таблица")],
            [InlineKeyboardButton(text="⚡ Мини-приложение / ИИ", callback_data="srv:Мини-приложение / ИИ")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
        ]
    )


def time_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сегодня", callback_data="time:Сегодня"),
                InlineKeyboardButton(text="Завтра", callback_data="time:Завтра"),
            ],
            [
                InlineKeyboardButton(text="На этой неделе", callback_data="time:На этой неделе"),
                InlineKeyboardButton(text="Просто консультация", callback_data="time:Консультация"),
            ],
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="back_main")],
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Это демо-бот записи от <b>ZERO AI</b>.\n\n"
        "Посмотри, как бот принимает заявки от клиентов 24/7, отвечает на вопросы и сразу передает данные владельцу бизнеса.\n\n"
        "Выбери действие ниже:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Главное меню <b>ZERO AI</b>. Выбери нужный раздел:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "prices")
async def show_prices(callback: CallbackQuery):
    text = (
        "<b>Услуги и стартовые ориентиры:</b>\n\n"
        "• <b>Telegram-бот</b> — от 5 000 до 10 000 ₽\n"
        "• <b>Сайт / лендинг</b> — от 7 000 до 12 000 ₽\n"
        "• <b>CRM и таблица клиентов</b> — от 5 000 до 8 000 ₽\n"
        "• <b>Мини-приложение в Telegram</b> — от 18 000 ₽\n"
        "• <b>ИИ-консультант по базе знаний</b> — от 15 000 ₽\n\n"
        "Хочешь такого же бота под свой бизнес? Нажми кнопку записи ниже."
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Оставить заявку", callback_data="book")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_main")],
        ]
    )
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery):
    text = (
        "<b>Частые вопросы:</b>\n\n"
        "<b>1. Зачем бизнесу такой бот?</b>\n"
        "Чтобы ни одна заявка не терялась в личке: клиент сам выбирает услугу и время, а вы получаете готовую карточку.\n\n"
        "<b>2. Сколько занимает сборка?</b>\n"
        "От 1 до 4 дней под ключ.\n\n"
        "<b>3. Можно подключить таблицу или CRM?</b>\n"
        "Да, заявки могут сразу падать в Telegram и в Google Таблицу."
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Попробовать запись", callback_data="book")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_main")],
        ]
    )
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "book")
async def start_booking(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BookingForm.choosing_service)
    await callback.message.edit_text(
        "<b>Шаг 1 из 3.</b> Выберите интересующее направление:",
        reply_markup=services_menu(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(BookingForm.choosing_service, F.data.startswith("srv:"))
async def select_service(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split(":", 1)[1]
    await state.update_data(service=service)
    await state.set_state(BookingForm.choosing_time)
    await callback.message.edit_text(
        f"Выбрано: <b>{service}</b>\n\n<b>Шаг 2 из 3.</b> Когда удобно обсудить задачу?",
        reply_markup=time_menu(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(BookingForm.choosing_time, F.data.startswith("time:"))
async def select_time(callback: CallbackQuery, state: FSMContext):
    when = callback.data.split(":", 1)[1]
    await state.update_data(when=when)
    await state.set_state(BookingForm.entering_contact)
    await callback.message.edit_text(
        f"Время: <b>{when}</b>\n\n<b>Шаг 3 из 3.</b> Напишите ваше имя и контакт (телефон или @username) одним сообщением:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(BookingForm.entering_contact)
async def finish_booking(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    service = data.get("service", "Не указано")
    when = data.get("when", "Не указано")
    contact = message.text or "Без текста"
    user_tag = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"

    await state.clear()

    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        f"• Направление: <b>{service}</b>\n"
        f"• Когда: <b>{when}</b>\n"
        f"• Контакт: <b>{contact}</b>\n\n"
        "Именно так ваш клиент получает подтверждение, а вы — мгновенное уведомление в личку.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )

    if ADMIN_ID:
        admin_text = (
            "🔥 <b>Новая заявка из бота ZERO AI!</b>\n\n"
            f"• Услуга: {service}\n"
            f"• Время: {when}\n"
            f"• Контакт из формы: {contact}\n"
            f"• Telegram: {user_tag}"
        )
        try:
            await bot.send_message(chat_id=int(ADMIN_ID), text=admin_text, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Не удалось отправить заявку админу: {e}")


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN в переменных окружения!")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
