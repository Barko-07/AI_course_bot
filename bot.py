import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from config import BOT_TOKEN, ADMIN_GROUP_ID, CARD_NUMBER, CARD_OWNER
import database

# Loggerni sozlash
logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    logging.error("BOT_TOKEN topilmadi! .env faylini tekshiring.")
    exit()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("statistika"))
async def cmd_statistika(message: types.Message):
    if str(message.chat.id) != str(ADMIN_GROUP_ID) and str(message.from_user.id) != str(ADMIN_GROUP_ID):
        return
        
    total_users, total_approved, beginner, premium = database.get_statistics()
    
    text = f"📊 **Umumiy Statistika:**\n\n" \
           f"👥 Botdagi jami ro'yxatdan o'tganlar: {total_users} ta\n" \
           f"✅ Faol obunachilar (To'laganlar): {total_approved} ta\n\n" \
           f"🟢 Beginner kanalida: {beginner} ta o'quvchi\n" \
           f"🟡 Premium kanalida: {premium} ta o'quvchi"
           
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.chat.type.in_({'group', 'supergroup'}))
async def group_messages(message: types.Message):
    if message.text and "test" in message.text.lower():
        await message.answer(f"Bu guruhning ID raqami: `{message.chat.id}`\nIltimos, ushbu ID ni .env fayliga ADMIN_GROUP_ID sifatida kiriting.", parse_mode="Markdown")

def get_main_menu():
    kb = [
        [KeyboardButton(text="📚 Kursga qo‘shilish")],
        [KeyboardButton(text="🧾 Obuna holati")],
        [KeyboardButton(text="📞 Yordam")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if message.chat.type != 'private':
        return
    
    keyboard = get_main_menu()
    
    try:
        photo = FSInputFile("banner.png")
        await message.answer_photo(
            photo=photo,
            caption="Assalomu alaykum! 🎓 Kursga obuna bo‘ling va yopiq guruhga qo‘shiling."
        )
    except Exception as e:
        logging.error(f"Error loading banner: {e}")
        await message.answer("Assalomu alaykum! 🎓 Kursga obuna bo‘ling va yopiq guruhga qo‘shiling.")
        
    await message.answer("Kerakli bo'limni pastdagi menyudan tanlang 👇", reply_markup=keyboard)

@dp.message(F.text == "📚 Kursga qo‘shilish")
async def join_course_menu(message: types.Message):
    user = database.get_user(message.from_user.id)
    if user and user.get('phone_number'):
        await ask_course(message)
    else:
        kb = [
            [KeyboardButton(text="📱 Raqamni yuborish va Davom etish", request_contact=True)]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Ro'yxatdan o'tish uchun pastdagi tugma orqali telefon raqamingizni yuboring:", reply_markup=keyboard)

@dp.message(F.text == "🧾 Obuna holati")
async def subscription_status(message: types.Message):
    payment = database.get_latest_payment(message.from_user.id)
    if not payment:
        await message.answer("Sizda hozircha faol obunalar yo'q. Kursga qo'shilish uchun '📚 Kursga qo‘shilish' tugmasini bosing.")
        return
    
    course_name = payment['course_name']
    status = payment['status']
    
    if status == 'approved':
        await message.answer(f"Sizning obunangiz holati: Faol ✅\nSiz **{course_name}** guruhidasiz.", parse_mode="Markdown")
    elif status == 'pending':
        await message.answer(f"Sizning obunangiz holati: Kutilmoqda ⏳\nSizning to'lovingiz admin tomonidan tekshirilmoqda.")
    elif status == 'pending_screenshot':
        await message.answer(f"Sizning obunangiz holati: To'lov kutilmoqda ⏳\nIltimos, to'lovni amalga oshirib skrinshot yuboring.")
    elif status == 'rejected':
        await message.answer(f"Sizning obunangiz holati: Rad etilgan ❌\nIltimos, qaytadan to'lov qiling yoki adminga murojaat qiling.")

@dp.message(F.text == "📞 Yordam")
async def help_menu(message: types.Message):
    await message.answer("Yordam uchun adminga murojaat qiling: @SizningAdminUsername")

@dp.message(F.contact)
async def process_phone(message: types.Message):
    phone_number = message.contact.phone_number
    full_name = message.contact.first_name
    if message.contact.last_name:
        full_name += f" {message.contact.last_name}"
        
    database.add_user(message.from_user.id, full_name, phone_number)
    
    await message.answer("Ajoyib! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.", reply_markup=types.ReplyKeyboardRemove())
    await ask_course(message)

async def ask_course(message: types.Message):
    kb = [
        [InlineKeyboardButton(text="🟢 Beginner Kanal", callback_data="course_beginner")],
        [InlineKeyboardButton(text="🟡 Premium Kanal", callback_data="course_premium")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer("Iltimos, qaysi kursga qo'shilmoqchi ekanligingizni tanlang:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("course_"))
async def process_course_selection(callback: types.CallbackQuery):
    course_type = callback.data.split("_")[1]
    
    if course_type == "beginner":
        course_name = "Beginner Kanal"
    else:
        course_name = "Premium Kanal"
        
    database.add_payment(callback.from_user.id, course_name, status="pending_screenshot")
    
    payment_msg = f"To‘lov uchun ma’lumotlar:\n" \
                  f"💰 To‘lov: 90.000 so'm\n" \
                  f"⏳ Muddat: 1 oy\n" \
                  f"👤 Holder: {CARD_OWNER}\n" \
                  f"🏦 Bank: Humo/Uzcard\n" \
                  f"💳 Karta: `{CARD_NUMBER}`\n\n" \
                  f"To‘lovni amalga oshirgach, pastdagi tugmani bosing:"
                  
    kb = [[InlineKeyboardButton(text="💸 To‘lov qildim", callback_data="paid_btn")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
                  
    await callback.message.answer(payment_msg, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "paid_btn")
async def ask_for_screenshot(callback: types.CallbackQuery):
    await callback.message.answer("Iltimos, to'lov chekini (skrinshot) yuboring:")
    await callback.answer()

@dp.message(F.photo)
async def process_payment_receipt(message: types.Message):
    if not ADMIN_GROUP_ID:
        await message.answer("Admin guruhi sozlanmagan, hozircha to'lovni tekshira olmaymiz.")
        return

    payment = database.get_pending_screenshot_payment(message.from_user.id)
    if not payment:
        # Check if they have a pending admin approval
        latest_payment = database.get_latest_payment(message.from_user.id)
        if latest_payment and latest_payment['status'] == 'pending':
            await message.answer("Sizning oldingi to'lovingiz hozirda admin tomonidan tekshirilmoqda. Iltimos kuting.")
        return
        
    course_name = payment['course_name']
    payment_id = payment['id']
    
    user = database.get_user(message.from_user.id)
    full_name = user['full_name']
    phone_number = user['phone_number']
    
    database.update_payment_status(payment_id, 'pending')
    
    admin_msg = f"🔔 **Yangi To'lov!**\n\n" \
                f"👤 Ism: {full_name}\n" \
                f"📞 Raqam: {phone_number}\n" \
                f"📚 Kurs: {course_name}\n" \
                f"ID: {payment_id}"
                
    kb = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{payment_id}_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{payment_id}_{message.from_user.id}")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=message.photo[-1].file_id,
            caption=admin_msg,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await message.answer("Sizning chekingiz qabul qilindi va tekshirish uchun adminga yuborildi. Tez orada ruxsat (link) yuboriladi. Kutganingiz uchun rahmat!")
    except Exception as e:
        await message.answer("Adminga xabar yuborishda xatolik yuz berdi. Iltimos keyinroq urinib ko'ring yoki admin bilan bog'laning.")
        logging.error(f"Error sending to admin group: {e}")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: types.CallbackQuery):
    _, payment_id, user_id = callback.data.split("_")
    
    database.update_payment_status(payment_id, 'approved')
    payment = database.get_payment(payment_id)
    course_name = payment['course_name']
    
    if "Beginner" in course_name:
        invite_link = "https://t.me/+B_EGINNER_LINK"
    else:
        invite_link = "https://t.me/+P_REMIUM_LINK"
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"Tabriklaymiz! 🎉 To'lovingiz tasdiqlandi.\n\n"
                 f"Siz **{course_name}**ga qo'shilishingiz mumkin.\n"
                 f"Kanalga kirish uchun havola:\n{invite_link}",
            parse_mode="Markdown"
        )
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n✅ **Tasdiqlandi va link yuborildi!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(e)
        await callback.answer("Foydalanuvchiga xabar yuborib bo'lmadi!", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: types.CallbackQuery):
    _, payment_id, user_id = callback.data.split("_")
    
    database.update_payment_status(payment_id, 'rejected')
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text="Kechirasiz, siz yuborgan to'lov cheki tasdiqlanmadi ❌.\n"
                 "Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning."
        )
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n❌ **Rad etildi!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(e)
        await callback.answer("Foydalanuvchiga xabar yuborib bo'lmadi!", show_alert=True)

async def main():
    database.init_db() if hasattr(database, 'init_db') else None
    logging.info("Bot ishga tushdi (Polling mode)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
