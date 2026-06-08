import os
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, FloodWait

API_ID = int(os.environ.get("API_ID", "32442870"))
API_HASH = os.environ.get("API_HASH", "3dcb0696714df4c0a79cd289831c94c7")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

bot = Client("storybot_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("storybot_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING) if SESSION_STRING else None

def estimate_age(uid):
    if uid < 400000000: return "2013-2016"
    elif uid < 1000000000: return "2016-2018"
    elif uid < 2000000000: return "2018-2020"
    elif uid < 4000000000: return "2020-2022"
    elif uid < 6000000000: return "2022-2024"
    else: return "2024-2025"

def main_kb():
    from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup([
        [KeyboardButton("📖 Hikoyalar"), KeyboardButton("👤 Ma'lumotlar")],
        [KeyboardButton("ℹ️ Yordam")]
    ], resize_keyboard=True)

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text(
        "👋 Salom, " + (message.from_user.first_name or "Do'st") + "!\n\n"
        "📖 <b>Hikoyalar</b> — @username yoki ID\n"
        "👤 <b>Ma'lumotlar</b> — @username yoki ID\n\n"
        "Tugmani bosing 👇",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=main_kb()
    )

@bot.on_message(filters.text & filters.regex("^📖 Hikoyalar$"))
async def stories_menu(client, message: Message):
    await message.reply_text("📖 @username yoki ID yuboring:")

@bot.on_message(filters.text & filters.regex("^👤 Ma'lumotlar$"))
async def info_menu(client, message: Message):
    await message.reply_text("👤 @username yoki ID yuboring:")

@bot.on_message(filters.text & filters.regex("^ℹ️ Yordam$"))
async def help_handler(client, message: Message):
    await message.reply_text(
        "ℹ️ @username yoki ID yuboring!\nMasalan: @durov yoki 12345678",
        reply_markup=main_kb()
    )

@bot.on_message(filters.text & ~filters.command(["start"]))
async def username_handler(client, message: Message):
    text = message.text.strip()
    if text in ["📖 Hikoyalar", "👤 Ma'lumotlar", "ℹ️ Yordam"]:
        return

    if text.startswith("@"):
        target = text[1:]
        display = "@" + target
    elif text.lstrip("-").isdigit():
        target = int(text)
        display = "ID: " + str(target)
    else:
        await message.reply_text("❓ @username yoki ID yuboring!", reply_markup=main_kb())
        return

    wait_msg = await message.reply_text("⏳ " + display + " tekshirilmoqda...")

    try:
        user = None
        try:
            user = await client.get_users(target)
        except Exception:
            if userbot and isinstance(target, int):
                try:
                    user = await userbot.get_users(target)
                except Exception:
                    pass

        if not user:
            await wait_msg.edit_text("❌ " + display + " topilmadi.")
            return

        uid = user.id
        fname = (user.first_name or "") + " " + (user.last_name or "")
        fname = fname.strip() or "—"
        uname = "@" + user.username if user.username else "—"
        bio = getattr(user, "bio", getattr(user, "about", "—")) or "—"
        is_bot = "Ha" if user.is_bot else "Yoq"
        is_premium = "Ha" if user.is_premium else "Yoq"
        is_verified = "Ha" if user.is_verified else "Yoq"

        info = (
            "<b>Foydalanuvchi ma'lumotlari</b>\n\n"
            "Ism: <b>" + fname + "</b>\n"
            "Username: <b>" + uname + "</b>\n"
            "ID: <code>" + str(uid) + "</code>\n"
            "Bio: " + bio + "\n\n"
            "Bot: " + is_bot + "\n"
            "Premium: " + is_premium + "\n"
            "Tekshirilgan: " + is_verified + "\n\n"
            "Taxminiy yil: <b>" + estimate_age(uid) + "</b>"
        )

        photos = []
        try:
            async for photo in client.get_chat_photos(uid, limit=3):
                photos.append(photo.file_id)
        except Exception:
            pass

        await wait_msg.delete()

        if photos:
            await client.send_photo(message.chat.id, photos[0], caption=info, parse_mode=enums.ParseMode.HTML)
            for photo in photos[1:]:
                await client.send_photo(message.chat.id, photo)
        else:
            await message.reply_text(info, parse_mode=enums.ParseMode.HTML)

        if userbot:
            story_count = 0
            try:
                async for _ in userbot.get_stories(uid):
                    story_count += 1
            except Exception:
                pass

            if story_count > 0:
                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                kb = InlineKeyboardMarkup([[
                    InlineKeyboardButton(str(story_count) + " ta hikoyani yuklab olish", callback_data="stories_" + str(uid))
                ]])
                await message.reply_text(
                    "<b>" + str(story_count) + "</b> ta aktiv hikoya bor!",
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=kb
                )

    except Exception as e:
        log.error("Xato: " + str(e))
        try:
            await wait_msg.edit_text("❌ Xatolik yuz berdi.")
        except Exception:
            pass

@bot.on_callback_query(filters.regex(r"^stories_(\d+)$"))
async def download_stories_cb(client, callback_query):
    uid = int(callback_query.data.split("_")[1])
    await callback_query.answer("⏳ Yuklanmoqda...")

    if not userbot:
        await callback_query.message.reply_text("❌ Hikoya yuklab olish mavjud emas.")
        return

    try:
        stories = []
        async for story in userbot.get_stories(uid):
            stories.append(story)

        if not stories:
            await callback_query.message.reply_text("📭 Hikoyalar topilmadi.")
            return

        for i, story in enumerate(stories, 1):
            try:
                if story.photo:
                    file = await userbot.download_media(story.photo)
                    await client.send_photo(callback_query.message.chat.id, file, caption="Hikoya " + str(i) + "/" + str(len(stories)))
                    os.remove(file)
                elif story.video:
                    file = await userbot.download_media(story.video)
                    await client.send_video(callback_query.message.chat.id, file, caption="Hikoya " + str(i) + "/" + str(len(stories)))
                    os.remove(file)
            except Exception as e:
                log.error("Story " + str(i) + ": " + str(e))

        await callback_query.message.reply_text("✅ Barcha hikoyalar yuborildi!")
    except Exception as e:
        log.error("Callback: " + str(e))
        await callback_query.message.reply_text("❌ Xatolik yuz berdi.")

async def main():
    log.info("StoryBot ishga tushdi!")
    await bot.start()
    if userbot:
        await userbot.start()
        log.info("Userbot started!")
    log.info("Bot started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
