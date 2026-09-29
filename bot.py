from music_service import search_music
import os
from config import ADMIN_ID
from dotenv import load_dotenv
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

from database import (
    create_database,
    save_user_language,
    get_user_language,
    get_all_users,get_users
)
from handlers import admin,broadcast, stats,users,remind,notify,monitor_database
load_dotenv("token.env")
TOKEN =os.getenv("BOT_TOKEN")

CHOOSING_LANGUAGE = 1
WAITING_FOR_SONG = 2
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "🎤 Popular Singers",
                callback_data="popular_singers"
            )
        ],
        [
            InlineKeyboardButton(
                "🔎 Search Music",
                callback_data="search_music"
            )
        ],
        [
            InlineKeyboardButton(
                "🔥 Trending",
                callback_data="trending"
            )
        ],
        [
            InlineKeyboardButton(
                "❤️ Favorites",
                callback_data="favorites"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ Help",
                callback_data="help"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎵 *Welcome to Music Bot!*\n\n"
        "What would you like to do?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def language_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if query.data == "hindi":
        selected_language = "Hindi 🇮🇳"

    else:
        selected_language = "English 🇬🇧"

    save_user_language(user_id, selected_language)

    context.user_data["language"] = selected_language
    saved_language = get_user_language(user_id)

    print("Language saved in database:", saved_language)

    await query.message.reply_text(
        f"You selected {selected_language}\n\n"
        "Enter a singer or song name:"
    )

    return WAITING_FOR_SONG

async def search_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_text = update.message.text

    try:

        results = search_music(user_text)

        if not results:
            await update.message.reply_text(
                "❌ No music results found."
            )
            return ConversationHandler.END

        message = "🎵 Music Results\n\n"

        for number, result in enumerate(results, start=1):

            message += (
                f"{number}. {result['song']}\n"
                f"Artist: {result['artist']}\n"
                f"Album: {result['album']}\n"
                f"🔗 {result['link']}\n\n"
            )

        await update.message.reply_text(message)

    except Exception as error:

        print("Music search error:", error)

        await update.message.reply_text(
            "❌ Sorry, I couldn't search for music right now."
        )

    return ConversationHandler.END


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Search cancelled."
    )

    return ConversationHandler.END

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):

    city = " ".join(context.args)

    if not city:
        await update.message.reply_text(
            "Please enter a city name.\nExample: /weather Hyderabad"
        )
        return

    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    geocoding_parameters = {
        "name": city,
        "count": 1
    }

    geocoding_response = requests.get(
        geocoding_url,
        params=geocoding_parameters
    )

    if geocoding_response.status_code != 200:
        await update.message.reply_text(
            "Sorry, city search is unavailable."
        )
        return

    geocoding_data = geocoding_response.json()

    if not geocoding_data.get("results"):
        await update.message.reply_text(
            f"Sorry, I couldn't find {city}."
        )
        return

    latitude = geocoding_data["results"][0]["latitude"]
    longitude = geocoding_data["results"][0]["longitude"]

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m",
        "wind_speed_unit": "kmh"
    }

    response = requests.get(url, params=parameters)

    if response.status_code != 200:
        await update.message.reply_text(
            "Sorry, weather service is unavailable."
        )
        return

    data = response.json()

    temperature = data["current"]["temperature_2m"]
    wind_speed = data["current"]["wind_speed_10m"]

    await update.message.reply_text(
        f"🌤 Weather\n\n"
        f"Temperature: {temperature} °C\n"
        f"Wind speed: {wind_speed} km/h"
    )
async def home_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "popular_singers":
        await query.edit_message_text(
            "🎤 Popular Singers\n\n"
            "Coming next: singer selection 🎶"
        )

    elif query.data == "search_music":
        await query.edit_message_text(
            "🔎 Search Music\n\n"
            "Type the singer or song name."
        )

    elif query.data == "trending":
        await query.edit_message_text(
            "🔥 Trending\n\n"
            "Trending songs will appear here soon."
        )

    elif query.data == "favorites":
        await query.edit_message_text(
            "❤️ Favorites\n\n"
            "Your saved songs will appear here."
        )

    elif query.data == "help":
        await query.edit_message_text(
            "ℹ️ Help\n\n"
            "🎤 Choose a singer\n"
            "🔎 Search for music\n"
            "🔥 Explore trending songs\n"
            "❤️ Save your favorite songs"
        )
conversation_handler = ConversationHandler(

    entry_points=[
        CommandHandler("start", start)
    ],

    states={

        CHOOSING_LANGUAGE: [
    CallbackQueryHandler(language_selected)

        ],

        WAITING_FOR_SONG: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                search_text
            )
        ]
    },

    fallbacks=[
    CommandHandler("cancel", cancel),
    CommandHandler("weather", weather)
]
)


create_database()

app = Application.builder().token(TOKEN).build()

app.add_handler(conversation_handler)
app.add_handler(CallbackQueryHandler(home_button))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("users", users))
app.add_handler(CommandHandler("remind", remind))
app.add_handler(CommandHandler("notify", notify))

app.job_queue.run_repeating(
    monitor_database,
    interval=60,
    first=10
)
async def scheduled_message(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text="⏰ Scheduled task is working!"
    )


app.job_queue.run_once(
    scheduled_message,
    10
)


print("Bot is running...")

app.run_polling()
