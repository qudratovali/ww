import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram import enums
from pyrogram.types import Message
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, FloodWait

# ===================== CONFIG =====================
API_ID = int(os.environ.get("API_ID", "32442870"))
API_HASH = os.environ.get("API_HASH", "3dcb0696714df4c0a79cd289831c94c7")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8635279428:AAGdiC38oQxpxleUv-3v8WfbcHgGFCRmKGI")

# ===================== LOGGING =====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ===================== BOT =====================
app = Client(
    "storybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===================== HELPERS =====================
def estimate_account_age(user_id: int) -> str:
    if user_id < 100000000:
        return "2013-2014 yillar (juda eski)"
    elif user_id < 200000000:
        return "2014-2015 yillar"
    elif user_id < 400000000:
        return "2015-2016 yillar"
    elif user_id < 700000000:
        return "2016-2017 yillar"
    elif user_id < 1000000000:
        return "2017-2018 yillar"
    elif user_id < 1500000000:
        return "2018-2019 yillar"
    elif user_id < 2000000000:
        return "2019-2020 yillar"
    elif user_id < 3000000000:
        return "2020-2021 yillar"
    elif user_id < 4000000000:
        return "2021-2022 yillar"
    elif user_id < 5000000000:
        return "2022-2023 yillar"
    elif user_id < 6000000000:
        return "2023-2024 yillar"
    else:
        return "2024-2025 yillar (yangi)"

def main_kb():
    from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup([
        [KeyboardButton("📖 Hikoyalar"), KeyboardButton("👤 Ma'lumotlar")],
        [KeyboardButton("ℹ️ Yordam")]
    ], resize_keyboard=True)

# ===================== HANDLERS =====================

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text(
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        "🤖 Men nima qila olaman:\n\n"
        "📖 <b>Hikoyalar</b> — @username yoki ID hikoyalarini yuklab beraman\n"
        "👤 <b>Ma'lumotlar</b> — @username yoki ID haqida batafsil ma'lumot\n\n"
        "Quyidagi tugmalardan birini tanlang 👇",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=main_kb()
    )

@app.on_message(filters.text & filters.regex("^📖 Hikoyalar$"))
async def stories_menu(client, message: Message):
    await message.reply_text(
        "📖 <b>Hikoyalar yuklab olish</b>\n\n"
        "@username yoki ID yuboring:\nMasalan: @durov yoki 12345678",
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.text & filters.regex("^👤 Ma'lumotlar$"))
async def info_menu(client, message: Message):
    await message.reply_text(
        "👤 <b>Foydalanuvchi ma'lumotlari</b>\n\n"
        "@username yoki ID yuboring:\nMasalan: @durov yoki 12345678",
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.text & filters.regex("^ℹ️ Yordam$"))
async def help_handler(client, message: Message):
    await message.reply_text(
        "ℹ️ <b>Yordam</b>\n\n"
        "📖 <b>Hikoyalar:</b>\n"
        "→ @username yoki ID yuboring → hikoyalar yuklanadi\n\n"
        "👤 <b>Ma'lumotlar:</b>\n"
        "→ @username yoki ID yuboring → profil ma'lumotlari\n\n"
        "⚠️ Faqat ommaviy profillar ko'rinadi",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=main_kb()
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def username_handler(client, message: Message):
    text = message.text.strip()

    # Tugmalarni o'tkazib yuborish
    if text in ["📖 Hikoyalar", "👤 Ma'lumotlar", "ℹ️ Yordam"]:
        return

    # @username yoki ID tekshirish
    if text.startswith("@"):
        target = text[1:]
        display = f"@{target}"
    elif text.lstrip("-").isdigit():
        target = int(text)
        display = f"ID: {target}"
    else:
        await message.reply_text(
            "❓ @username yoki ID yuboring!\nMasalan: @durov yoki 123456789",
            reply_markup=main_kb()
        )
        return

    wait_msg = await message.reply_text(f"⏳ {display} tekshirilmoqda...")

    try:
        try:
            user = await client.get_users(target)
        except (UsernameNotOccupied, UsernameInvalid):
            await wait_msg.edit_text(f"❌ {display} topilmadi.")
            return
        except Exception:
            await wait_msg.edit_text(f"❌ {display} topilmadi yoki yopiq profil.")
            return

        user_id = user.id
        first_name = user.first_name or "—"
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        uname = f"@{user.username}" if user.username else "—"
        bio = getattr(user, "bio", getattr(user, "about", "—")) or "—"
        is_bot = "🤖 Ha" if user.is_bot else "Yo'q"
        is_premium = "💎 Ha" if user.is_premium else "Yo'q"
        is_verified = "✅ Ha" if user.is_verified else "Yo'q"
        is_scam = "⚠️ Ha" if user.is_scam else "Yo'q"
        is_restricted = "🚫 Ha" if user.is_restricted else "Yo'q"
        acc_age = estimate_account_age(user_id)

        info_text = (
            f"👤 <b>Foydalanuvchi ma'lumotlari</b>\n\n"
            f"📛 Ism: <b>{full_name}</b>\n"
            f"🔗 Username: <b>{uname}</b>\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"📝 Bio: {bio}\n\n"
            f"🤖 Bot: {is_bot}\n"
            f"💎 Premium: {is_premium}\n"
            f"✅ Tekshirilgan: {is_verified}\n"
            f"⚠️ Scam: {is_scam}\n"
            f"🚫 Cheklangan: {is_restricted}\n\n"
            f"📅 Taxminiy ro'yxatdan o'tish: <b>{acc_age}</b>"
        )

        # Profil rasmlari
        photos = []
        async for photo in client.get_chat_photos(user_id, limit=5):
            photos.append(photo.file_id)

        await wait_msg.delete()

        if photos:
            await client.send_photo(
                message.chat.id,
                photos[0],
                caption=info_text,
                parse_mode=enums.ParseMode.HTML
            )
            for photo in photos[1:]:
                await client.send_photo(message.chat.id, photo)
        else:
            await message.reply_text(info_text, parse_mode=enums.ParseMode.HTML)

        # Hikoyalar bormi tekshirish
        story_count = 0
        try:
            async for _ in client.get_stories(user_id):
                story_count += 1
        except Exception:
            pass

        if story_count > 0:
            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"📖 {story_count} ta hikoyani yuklab olish",
                    callback_data=f"stories_{user_id}"
                )
            ]])
            await message.reply_text(
                f"📖 Bu foydalanuvchining <b>{story_count}</b> ta aktiv hikoyasi bor!",
                parse_mode=enums.ParseMode.HTML,
                reply_markup=kb
            )

    except FloodWait as e:
        await wait_msg.edit_text(f"⏳ Biroz kuting ({e.value} soniya)...")
        await asyncio.sleep(e.value)
    except Exception as e:
        log.error(f"Xato: {e}")
        await wait_msg.edit_text("❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.")

@app.on_callback_query(filters.regex(r"^stories_(.+)$"))
async def download_stories_cb(client, callback_query):
    user_id = int(callback_query.data.split("_", 1)[1])
    await callback_query.answer("⏳ Yuklanmoqda...")

    try:
        stories = []
        async for story in client.get_stories(user_id):
            stories.append(story)

        if not stories:
            await callback_query.message.reply_text("📭 Hikoyalar topilmadi.")
            return

        for i, story in enumerate(stories, 1):
            try:
                if story.photo:
                    file = await client.download_media(story.photo)
                    await client.send_photo(
                        callback_query.message.chat.id, file,
                        caption=f"📸 Hikoya {i}/{len(stories)}"
                    )
                    os.remove(file)
                elif story.video:
                    file = await client.download_media(story.video)
                    await client.send_video(
                        callback_query.message.chat.id, file,
                        caption=f"🎥 Hikoya {i}/{len(stories)}"
                    )
                    os.remove(file)
            except Exception as e:
                log.error(f"Story {i}: {e}")

        await callback_query.message.reply_text("✅ Barcha hikoyalar yuborildi!")

    except Exception as e:
        log.error(f"Callback xato: {e}")
        await callback_query.message.reply_text("❌ Xatolik yuz berdi.")

# ===================== MAIN =====================
if __name__ == "__main__":
    log.info("StoryBot ishga tushdi!")
    app.run()
