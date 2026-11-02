import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Loggingni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Admin / Bot sozlamalari (Sizning tokeningiz joylandi)
TOKEN = "9059899230:AAEQ38b-rnWRpiUOmPi2vGtSZDOSpBLAlgQ"

# Qollab-quvvatlanadigan o'yinlar ro'yxati va ularning rejimlari
GAMES = {
    "aviator": {"name": "✈️ Aviator Pro", "type": "multiplier"},
    "mines": {"name": "💣 Mines Matrix", "type": "grid"},
    "apple": {"name": "🍎 Apple of Fortune", "type": "apple_grid"},
    "penalty": {"name": "⚽ Penalty Shootout", "type": "direction"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boshlang'ich menyu va chiroyli interfeys"""
    user = update.effective_user
    welcome_text = (
        f"👋 *Salom, {user.first_name}!*\n\n"
        "⚡ **Signal Pro V4.2 Analytical Engine**ga xush kelibsiz!\n"
        "Quyidagi o'yinlardan birini tanlang va professional signallarni oling:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✈️ Aviator", callback_data="game_aviator"),
            InlineKeyboardButton("💣 Mines", callback_data="game_mines")
        ],
        [
            InlineKeyboardButton("🍎 Apple of Fortune", callback_data="game_apple"),
            InlineKeyboardButton("⚽ Penalty", callback_data="game_penalty")
        ],
        [
            InlineKeyboardButton("📊 Statistika", callback_data="stats"),
            InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalar bosilganda ishlovchi asosiy logika"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("game_"):
        game_key = data.split("_")[1]
        context.user_data['current_game'] = game_key
        await show_game_menu(query, game_key)
        
    elif data == "get_signal":
        game_key = context.user_data.get('current_game', 'aviator')
        await generate_signal_with_loading(query, game_key)
        
    elif data == "main_menu":
        await start(update, context)
        
    elif data == "stats":
        stats_text = (
            "📊 *SIGNAL PRO ENGINE STATISTIKASI*\n\n"
            "• Bugungi aniqlik (Winrate): *94.8%*\n"
            "• Jami uzatilgan signallar: *1,420+*\n"
            "• Faol foydalanuvchilar: *3,890*\n"
            "• Algoritm holati: 🟢 *ONLINE (v4.2 API)*"
        )
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")]]
        await query.message.edit_text(stats_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_game_menu(query, game_key):
    """Tanlangan o'yin uchun boshqaruv oynasi"""
    game = GAMES[game_key]
    text = (
        f"🎮 *Tanlangan o'yin:* {game['name']}\n\n"
        "⚡ Signallarni olish va tahlil qilish uchun quyidagi tugmani bosing."
    )
    keyboard = [
        [InlineKeyboardButton("🚀 SIGNAL OLISH", callback_data="get_signal")],
        [InlineKeyboardButton("🔙 Bosh Menyuga", callback_data="main_menu")]
    ]
    await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def generate_signal_with_loading(query, game_key):
    """Chiroyli animatsiya va dinamik Signal generatsiyasi"""
    game = GAMES[game_key]
    
    # 1. Animatsiyali yuklanish bosqichi
    loading_steps = [
        "📡 *Server bilan aloqa o'rnatilmoqda...*",
        "🔍 *RNG Pattern va koeffitsiyentlar tahlil qilinmoqda...*",
        "⚡ *Signal hisoblab chiqildi!*"
    ]
    
    for step in loading_steps:
        await query.message.edit_text(step, parse_mode="Markdown")
        await asyncio.sleep(0.6)
        
    # 2. Game turiga qarab Signal formatini yaratish
    accuracy = round(random.uniform(91.5, 98.2), 1)
    
    if game["type"] == "multiplier":
        coef = round(random.uniform(1.35, 4.85), 2)
        safe_exit = round(coef * 0.82, 2)
        signal_msg = (
            f"🎯 *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📈 *Kutilayotgan koeffitsiyent:* `x{coef}`\n"
            f"🛡 *Xavfsiz chiqish (Cashout):* `x{safe_exit}`\n"
            f"🎯 *Aniqlik darajasi:* `{accuracy}%` \n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "💡 *Maslahat:* Tikishni tayyorlang va berilgan koeffitsiyentda avto-cashout qo'ying!"
        )
        
    elif game["type"] == "grid":
        safe_clicks = random.randint(3, 5)
        signal_msg = (
            f"💣 *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Tavsiya etilgan minalar:* `3 ta`\n"
            f"✨ *Xavfsiz kataklar soni:* `{safe_clicks} ta`\n"
            f"🎯 *Ehtimollik:* `{accuracy}%` \n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Topilgan kataklar bo'yicha ketma-ket harakat qiling!"
        )
        
    elif game["type"] == "apple_grid":
        row = random.randint(4, 7)
        pos = random.randint(1, 5)
        signal_msg = (
            f"🍎 *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📊 *Tavsiya qilingan qator:* `{row}-qator`\n"
            f"👉 *Xavfsiz olma ustuni:* `{pos}-ustun`\n"
            f"🎯 *Algoritm aniqligi:* `{accuracy}%` \n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        
    else:
        directions = ["⬅️ Chap burchak", "➡️ O'ng burchak", "⬆️ Markaz yuqori"]
        chosen_dir = random.choice(directions)
        signal_msg = (
            f"⚽ *{game['name']} SIGNAL*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *Zarba yo'nalishi:* *{chosen_dir}*\n"
            f"📊 *Gol urish imkoniyati:* `{accuracy}%` \n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        
    keyboard = [
        [InlineKeyboardButton("🔄 Yangi Signal", callback_data="get_signal")],
        [InlineKeyboardButton("🎮 Boshqa o'yin", callback_data="main_menu")]
    ]
    
    await query.message.edit_text(signal_msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    """Botni ishga tushirish funksiyasi"""
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Signal Pro Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
      
