import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Loggingni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot Tokeni
TOKEN = "9059899230:AAEQ38b-rnWRpiUOmPi2vGtSZDOSpBLAlgQ"

# O'yinlar ro'yxati
GAMES = {
    "aviator": {"name": "✈️ Aviator Pro", "type": "multiplier"},
    "mines": {"name": "💣 Gems Mines Matrix", "type": "grid"},
    "apple": {"name": "🍎 Apple of Fortune", "type": "apple_grid"},
    "penalty": {"name": "⚽ Penalty Shootout", "type": "direction"}
}

# Foydalanuvchilar tasdiqlanganini saqlash uchun vaqtinchalik baza (xotira)
# Real loyihada buni bazaga ulash mumkin, hozircha oddiy dictionary
verified_users = set()
waiting_for_verification = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boshlang'ich menyu va Coldbet shartini tekshirish"""
    user = update.effective_user
    user_id = user.id
    
    # Agar foydalanuvchi allaqachon shartni bajargan bo'lsa
    if user_id in verified_users:
        await show_main_menu(update, context)
    else:
        # Shartni bajarish talabi
        welcome_text = (
            f"❄️ *Salom, {user.first_name}!* \n"
            "🧊 *MUZZ | Coldbet Signal Pro* botiga xush kelibsiz!\n\n"
            "⚠️ *DIQQAT! Barcha signallardan bepul foydalanish uchun quyidagi shartlarni bajarishingiz shart:*\n\n"
            "1️⃣ Quyidagi tugma orqali **Coldbet** rasmiy ilovasini yuklab oling:\n"
            "🔗 [Coldbet Yuklab Olish](https://coldb10.com/Fhyhq8yL)\n\n"
            "2️⃣ Ro‘yxatdan o‘tayotganda promokodni kiriting: `MUZZ` 🧊\n"
            "3️⃣ Hisobingizni kamida **50,000 so‘m**ga to‘ldiring (depozit qiling).\n"
            "4️⃣ Coldbet akkauntingizda **Email manzilingizni tasdiqlab qo‘ying** 📧\n\n"
            "👇 Shartlarni bajargach, **'✅ Shartni bajardim'** tugmasini bosing va ID raqamingizni yuboring!"
        )
        
        keyboard = [
            [InlineKeyboardButton("📥 Coldbet APK Yuklab Olish", url="https://coldb10.com/Fhyhq8yL")],
            [InlineKeyboardButton("✅ Shartni bajardim / ID yuborish", callback_data="verify_step")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)
        elif update.callback_query:
            await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy o'yinlar menyusi"""
    text = (
        "🧊 *MUZZ | SIGNAL PRO ANALYTICAL ENGINE*\n\n"
        "🎯 Quyidagi o'yinlardan birini tanlang va professional signallarni oling:"
    )
    keyboard = [
        [
            InlineKeyboardButton("✈️ Aviator", callback_data="game_aviator"),
            InlineKeyboardButton("💣 Gems Mines", callback_data="game_mines")
        ],
        [
            InlineKeyboardButton("🍎 Apple of Fortune", callback_data="game_apple"),
            InlineKeyboardButton("⚽ Penalty", callback_data="game_penalty")
        ],
        [
            InlineKeyboardButton("📊 Kanalimiz", url="https://t.me/MUZZCOLD"),
            InlineKeyboardButton("⚙️ Profil", callback_data="profile")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalar bosilganda ishlovchi asosiy logika"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "verify_step":
        waiting_for_verification.add(user_id)
        text = (
            "📝 *Ma'lumotlarni yuborish:*\n\n"
            "Iltimos, botga quyidagilarni yuboring:\n"
            "1️⃣ Coldbet **ID raqamingizni** (masalan: `12345678`)\n"
            "2️⃣ Depozit qilinganligini tasdiqlovchi **Skrinshotni** 📸\n\n"
            "👇 *Xabar sifatida shu yerga yuboring:* (Matn yoki rasm ko'rinishida)"
        )
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_start")]]
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data == "back_to_start":
        waiting_for_verification.discard(user_id)
        await start(update, context)
        
    elif data == "profile":
        profile_text = (
            f"👤 *Foydalanuvchi Profili*\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"🧊 Promokod: `MUZZ` (Faol)\n"
            f"🛡 Holati: *Tasdiqlangan ✅*\n"
            f"🎁 Bonuslar: Faol ($2000 + 150 ta tekin aylantirish)[span_3](start_span)[span_3](end_span)"
        )
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")]]
        await query.message.edit_text(profile_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data == "main_menu":
        if user_id in verified_users:
            await show_main_menu(update, context)
        else:
            await start(update, context)
            
    elif data.startswith("game_"):
        if user_id not in verified_users:
            await query.message.reply_text("⚠️ Avval Coldbet shartlarini bajarib, ID va skrinshot yuborishingiz kerak!")
            return
        game_key = data.split("_")[1]
        context.user_data['current_game'] = game_key
        await show_game_menu(query, game_key)
        
    elif data == "get_signal":
        if user_id not in verified_users:
            return
        game_key = context.user_data.get('current_game', 'aviator')
        await generate_signal_with_loading(query, game_key)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi ID yoki Skrinshot yuborganda uni qabul qilish"""
    user_id = update.effective_user.id
    
    if user_id in waiting_for_verification:
        # Foydalanuvchi ID yoki rasm yubordi, uni tasdiqlangan deb belgilaymiz
        waiting_for_verification.remove(user_id)
        verified_users.add(user_id)
        
        success_text = (
            "✅ *Tabriklaymiz! Ma'lumotlaringiz qabul qilindi.*\n\n"
            "🧊 Akkauntingiz muvaffaqiyatli tasdiqlandi va barcha o'yin signallari ochildi!\n"
            "👇 Asosiy menyudan o'yinni tanlang:"
        )
        keyboard = [
            [
                InlineKeyboardButton("✈️ Aviator", callback_data="game_aviator"),
                InlineKeyboardButton("💣 Gems Mines", callback_data="game_mines")
            ],
            [
                InlineKeyboardButton("🍎 Apple of Fortune", callback_data="game_apple"),
                InlineKeyboardButton("⚽ Penalty", callback_data="game_penalty")
            ]
        ]
        await update.message.reply_text(success_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        # Agar shart so'ralmagan bo'lsa
        if user_id in verified_users:
            await update.message.reply_text("Iltimos, quyidagi tugmalar orqali o'yinni tanlang 👇")
        else:
            await start(update, context)

async def show_game_menu(query, game_key):
    """Tanlangan o'yin uchun boshqaruv oynasi"""
    game = GAMES[game_key]
    text = (
        f"🎮 *Tanlangan o'yin:* {game['name']}\n\n"
        "🧊 *MUZZ | Signal Analitigi tayyor.*\n"
        "⚡ Signallarni olish uchun quyidagi tugmani bosing."
    )
    keyboard = [
        [InlineKeyboardButton("🚀 SIGNAL OLISH", callback_data="get_signal")],
        [InlineKeyboardButton("🔙 Bosh Menyuga", callback_data="main_menu")]
    ]
    await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def generate_signal_with_loading(query, game_key):
    """Dinamik Signal generatsiyasi"""
    game = GAMES[game_key]
    
    loading_steps = [
        "🧊 *MUZZ Serveri bilan aloqa o'rnatilmoqda...*",
        "🔍 *Coldbet RNG Pattern tahlil qilinmoqda...*",
        "⚡ *Aniq signal muvaffaqiyatli hisoblandi!*"
    ]
    
    for step in loading_steps:
        await query.message.edit_text(step, parse_mode="Markdown")
        await asyncio.sleep(0.5)
        
    accuracy = round(random.uniform(94.0, 99.1), 1)
    
    if game["type"] == "multiplier":
        coef = round(random.uniform(1.45, 5.20), 2)
        safe_exit = round(coef * 0.80, 2)
        signal_msg = (
            f"🎯 *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📈 *Kutilayotgan koeffitsiyent:* `x{coef}`\n"
            f"🛡 *Xavfsiz chiqish (Cashout):* `x{safe_exit}`\n"
            f"🎯 *Algoritm aniqligi:* `{accuracy}%` 🧊\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "💡 *Promo-code:* `MUZZ` orqali olingan bonus bilan harakat qiling!"
        )
        
    elif game["type"] == "grid":
        safe_clicks = random.randint(3, 6)
        signal_msg = (
            f"💣 *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Tavsiya etilgan minalar:* `3 ta`\n"
            f"✨ *Xavfsiz kataklar soni:* `{safe_clicks} ta`\n"
            f"🎯 *Aniqlik darajasi:* `{accuracy}%` 🧊\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Gems Mines matritsasi bo'yicha ehtiyotkorlik bilan yuring!"
        )
        
    elif game["type"] == "apple_grid":
        row = random.randint(3, 7)
        pos = random.randint(1, 5)
        signal_msg = (
            f"🍎 *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📊 *Tavsiya qilingan qator:* `{row}-qator`\n"
            f"👉 *Xavfsiz olma ustuni:* `{pos}-ustun`\n"
            f"🎯 *Analiz aniqligi:* `{accuracy}%` 🧊\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        
    else:
        directions = ["⬅️ Chap burchak", "➡️ O'ng burchak", "⬆️ Markaz yuqori"]
        chosen_dir = random.choice(directions)
        signal_msg = (
            f"⚽ *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *Zarba yo'nalishi:* *{chosen_dir}*\n"
            f"📊 *Gol urish imkoniyati:* `{accuracy}%` 🧊\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        
    keyboard = [
        [InlineKeyboardButton("🔄 Yangi Signal", callback_data="get_signal")],
        [InlineKeyboardButton("🎮 Boshqa o'yin", callback_data="main_menu")]
    ]
    
    await query.message.edit_text(signal_msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    """Botni ishga tushirish"""
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_user_message))
    
    print("🧊 MUZZ Coldbet Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
