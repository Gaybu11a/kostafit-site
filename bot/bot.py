"""QuvMarkets sotuv boti.

Xodimlar mijoz ma'lumotlarini (ism, telefon, qo'shimcha telefon, manzil,
mahsulot, summa) kiritadi — hammasi Google Sheets'ga yoziladi.
Admin xodimlarni tasdiqlaydi/o'chiradi va hisobotlarni ko'radi.
"""
import asyncio
import html
import logging
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, Message, ReplyKeyboardMarkup)
from dotenv import load_dotenv

from storage import ACTIVE, BLOCKED, PENDING, Storage

load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
SPREADSHEET = os.environ["SPREADSHEET"]
CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", "service-account.json")
ADMIN_ID_ENV = os.getenv("ADMIN_ID", "").strip()
TZ = ZoneInfo(os.getenv("TIMEZONE", "Asia/Tashkent"))

PRODUCTS = [
    "Mexanik yugurish yo'lagi",
    "Walking Pad",
    "Yugurish yo'lagi 1.5 o.k.",
    "Yugurish yo'lagi 2.0 o.k.",
    "Yugurish yo'lagi 2.5 o.k.",
    "Yugurish yo'lagi 3.0 o.k.",
    "Professional yo'lak 4.0 o.k.",
    "Magnitli velotrenajor",
    "Spin bayk",
    "Gorizontal velotrenajor",
    "Elektromagnit velotrenajor",
    "Air bike",
]

# ---------- tugmalar matni ----------
BTN_NEW = "➕ Yangi mijoz"
BTN_REPORT = "📊 Hisobot"
BTN_MY = "📊 Mening sotuvlarim"
BTN_STAFF = "👥 Xodimlar"
BTN_CANCEL = "❌ Bekor qilish"
BTN_SKIP = "⏭ Yo'q"
BTN_OTHER = "✍️ Boshqa mahsulot"
BTN_SAVE = "✅ Saqlash"

log = logging.getLogger("quvbot")
router = Router()
store: Storage  # main() da ishga tushiriladi
admin_id: int | None = None


class NewClient(StatesGroup):
    name = State()
    phone = State()
    phone2 = State()
    address = State()
    product = State()
    product_other = State()
    amount = State()
    confirm = State()


# ---------- yordamchi funksiyalar ----------
def now() -> datetime:
    return datetime.now(TZ).replace(tzinfo=None)


def esc(s: str) -> str:
    return html.escape(s or "")


def money(n: int) -> str:
    return f"{n:,}".replace(",", " ") + " so'm"


def kb(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t) for t in row] for row in rows],
        resize_keyboard=True,
    )


CANCEL_KB = kb([[BTN_CANCEL]])
SKIP_KB = kb([[BTN_SKIP], [BTN_CANCEL]])
CONFIRM_KB = kb([[BTN_SAVE], [BTN_CANCEL]])
PRODUCT_KB = kb([PRODUCTS[i:i + 2] for i in range(0, len(PRODUCTS), 2)] + [[BTN_OTHER], [BTN_CANCEL]])


def is_admin(user_id: int) -> bool:
    return admin_id is not None and user_id == admin_id


def is_active(user_id: int) -> bool:
    if is_admin(user_id):
        return True
    s = store.staff.get(user_id)
    return bool(s and s.status == ACTIVE)


def menu_kb(user_id: int) -> ReplyKeyboardMarkup:
    if is_admin(user_id):
        return kb([[BTN_NEW], [BTN_REPORT, BTN_STAFF]])
    return kb([[BTN_NEW], [BTN_MY]])


def full_name(msg_or_cb) -> str:
    u = msg_or_cb.from_user
    return " ".join(p for p in [u.first_name, u.last_name] if p) or str(u.id)


def normalize_phone(text: str) -> str | None:
    """'99 610 99 06', '+998996109906', '998996109906' -> '+998 99 610 99 06'"""
    d = re.sub(r"\D", "", text or "")
    if len(d) == 9:
        d = "998" + d
    if len(d) == 12 and d.startswith("998"):
        return f"+{d[:3]} {d[3:5]} {d[5:8]} {d[8:10]} {d[10:]}"
    if 7 <= len(d) <= 15:  # chet el raqami
        return "+" + d
    return None


def parse_amount(text: str) -> int | None:
    """'4 900 000', '4900000', '4.9 mln', '4,9mln', '850 ming' -> int"""
    t = (text or "").lower().replace(" ", "").replace(",", ".")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(mln|million|ming|k)?(so'?m|sum|сум)?", t)
    if not m:
        digits = re.sub(r"\D", "", t)
        return int(digits) if digits else None
    value = float(m.group(1))
    unit = m.group(2)
    if unit in ("mln", "million"):
        value *= 1_000_000
    elif unit in ("ming", "k"):
        value *= 1_000
    elif "." in m.group(1):
        # "4.900.000" kabi yozilgan bo'lsa
        return int(re.sub(r"\D", "", m.group(1)))
    return int(round(value))


async def db(func, *args):
    """Google Sheets chaqiruvlari bloklovchi — alohida oqimda bajaramiz."""
    return await asyncio.to_thread(func, *args)


# ---------- /start va ruxsat ----------
@router.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):
    global admin_id
    await state.clear()
    uid = message.from_user.id

    if admin_id is None:
        admin_id = uid
        await db(store.set_setting, "admin_id", str(uid))
        await message.answer(
            "👑 Siz botning <b>admini</b> bo'ldingiz!\n\n"
            "Xodimlaringiz botga /start yozsa, sizga so'rov keladi — "
            "<b>✅ Ruxsat berish</b> tugmasini bosasiz.\n"
            "Barcha mijozlar Google Sheets'dagi <b>Sotuvlar</b> varag'iga tushadi.",
            reply_markup=menu_kb(uid),
        )
        return

    if is_active(uid):
        role = "admin" if is_admin(uid) else "xodim"
        await message.answer(f"Assalomu alaykum, {esc(message.from_user.first_name)}! Siz — {role}.\n"
                             f"Yangi mijoz qo'shish uchun <b>{BTN_NEW}</b> ni bosing.",
                             reply_markup=menu_kb(uid))
        return

    await request_access(message, bot)


async def request_access(message: Message, bot: Bot):
    uid = message.from_user.id
    if admin_id is None:
        await message.answer("Botni ishga tushirish uchun /start ni bosing.")
        return
    s = store.staff.get(uid)
    if s and s.status == BLOCKED:
        await message.answer("⛔ Sizga bu botdan foydalanishga ruxsat berilmagan.")
        return
    if s and s.status == PENDING:
        await message.answer("⏳ So'rovingiz adminga yuborilgan. Tasdiqlashini kuting.")
        return

    name = full_name(message)
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    await db(store.add_staff, uid, name, username, now())
    await message.answer("📨 So'rovingiz adminga yuborildi. Tasdiqlangach, sizga xabar keladi.")
    await bot.send_message(
        admin_id,
        f"🆕 Yangi xodim ruxsat so'rayapti:\n<b>{esc(name)}</b> {esc(username)}\nID: <code>{uid}</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"ok:{uid}"),
            InlineKeyboardButton(text="🚫 Rad etish", callback_data=f"no:{uid}"),
        ]]),
    )


@router.callback_query(F.data.regexp(r"^(ok|no|del|on):-?\d+$"))
async def staff_action(cb: CallbackQuery, bot: Bot):
    if not is_admin(cb.from_user.id):
        await cb.answer("Faqat admin uchun", show_alert=True)
        return
    action, raw_id = cb.data.split(":")
    uid = int(raw_id)
    new_status = ACTIVE if action in ("ok", "on") else BLOCKED
    s = await db(store.set_staff_status, uid, new_status)
    if not s:
        await cb.answer("Xodim topilmadi", show_alert=True)
        return

    label = {"ok": "✅ Ruxsat berildi", "on": "✅ Ruxsat berildi",
             "no": "🚫 Rad etildi", "del": "🚫 O'chirildi"}[action]
    await cb.message.edit_text(f"{label}: <b>{esc(s.name)}</b> {esc(s.username)}")
    await cb.answer(label)
    try:
        if new_status == ACTIVE:
            await bot.send_message(uid, "✅ Admin sizga ruxsat berdi! Endi mijozlarni kiritishingiz mumkin.",
                                   reply_markup=menu_kb(uid))
        elif action == "no":
            await bot.send_message(uid, "⛔ Admin so'rovingizni rad etdi.")
        else:
            await bot.send_message(uid, "⛔ Sizning botdan foydalanish huquqingiz o'chirildi.")
    except Exception as e:  # xodim botni bloklagan bo'lishi mumkin
        log.warning("Xodimga xabar yuborilmadi: %s", e)


# ---------- ruxsatsiz foydalanuvchilarni to'xtatish ----------
@router.message(lambda m: not is_active(m.from_user.id))
async def not_allowed(message: Message, bot: Bot):
    await request_access(message, bot)


# ---------- bekor qilish (istalgan bosqichda) ----------
@router.message(F.text == BTN_CANCEL)
@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=menu_kb(message.from_user.id))


# ---------- yangi mijoz kiritish ----------
@router.message(F.text == BTN_NEW)
async def new_client(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(NewClient.name)
    await message.answer("1/6. Mijozning <b>ism-familiyasi</b>:", reply_markup=CANCEL_KB)


@router.message(NewClient.name, F.text)
async def got_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Ismni to'liqroq yozing:")
        return
    await state.update_data(name=name)
    await state.set_state(NewClient.phone)
    await message.answer("2/6. Mijozning <b>telefon raqami</b>:\nmasalan: <code>99 610 99 06</code>",
                         reply_markup=CANCEL_KB)


@router.message(NewClient.phone)
async def got_phone(message: Message, state: FSMContext):
    raw = message.contact.phone_number if message.contact else message.text
    phone = normalize_phone(raw)
    if not phone:
        await message.answer("❗ Raqam noto'g'ri. Qaytadan yozing, masalan: <code>99 610 99 06</code>")
        return
    await state.update_data(phone=phone)
    await state.set_state(NewClient.phone2)
    await message.answer(f"3/6. <b>Qo'shimcha raqam</b> bormi? Bo'lsa yozing, bo'lmasa <b>{BTN_SKIP}</b> ni bosing.",
                         reply_markup=SKIP_KB)


@router.message(NewClient.phone2)
async def got_phone2(message: Message, state: FSMContext):
    if message.text == BTN_SKIP:
        phone2 = ""
    else:
        raw = message.contact.phone_number if message.contact else message.text
        phone2 = normalize_phone(raw)
        if not phone2:
            await message.answer(f"❗ Raqam noto'g'ri. Qaytadan yozing yoki <b>{BTN_SKIP}</b> ni bosing.")
            return
    await state.update_data(phone2=phone2)
    await state.set_state(NewClient.address)
    await message.answer("4/6. Mijozning <b>uy manzili</b>:\nmasalan: <i>Toshkent, Chilonzor 9-kvartal, 12-uy, 34-xonadon</i>",
                         reply_markup=CANCEL_KB)


@router.message(NewClient.address, F.text)
async def got_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 3:
        await message.answer("Manzilni to'liqroq yozing:")
        return
    await state.update_data(address=address)
    await state.set_state(NewClient.product)
    await message.answer("5/6. Mijoz <b>qaysi mahsulotni</b> oldi?", reply_markup=PRODUCT_KB)


@router.message(NewClient.product, F.text)
async def got_product(message: Message, state: FSMContext):
    if message.text == BTN_OTHER:
        await state.set_state(NewClient.product_other)
        await message.answer("Mahsulot nomini yozing:", reply_markup=CANCEL_KB)
        return
    await save_product(message, state, message.text.strip())


@router.message(NewClient.product_other, F.text)
async def got_product_other(message: Message, state: FSMContext):
    await save_product(message, state, message.text.strip())


async def save_product(message: Message, state: FSMContext, product: str):
    if len(product) < 2:
        await message.answer("Mahsulot nomini yozing:")
        return
    await state.update_data(product=product)
    await state.set_state(NewClient.amount)
    await message.answer("6/6. <b>Sotuv summasi</b> (so'mda):\nmasalan: <code>6 800 000</code> yoki <code>6.8 mln</code>",
                         reply_markup=CANCEL_KB)


@router.message(NewClient.amount, F.text)
async def got_amount(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    if not amount or amount < 1000:
        await message.answer("❗ Summani raqamda yozing, masalan: <code>6 800 000</code>")
        return
    await state.update_data(amount=amount)
    await state.set_state(NewClient.confirm)
    d = await state.get_data()
    await message.answer("Tekshiring:\n\n" + card(d) + "\n\nHammasi to'g'rimi?", reply_markup=CONFIRM_KB)


def card(d: dict) -> str:
    lines = [
        f"👤 <b>{esc(d['name'])}</b>",
        f"📞 {esc(d['phone'])}" + (f", {esc(d['phone2'])}" if d.get("phone2") else ""),
        f"🏠 {esc(d['address'])}",
        f"🛒 {esc(d['product'])}",
        f"💰 <b>{money(d['amount'])}</b>",
    ]
    return "\n".join(lines)


@router.message(NewClient.confirm, F.text == BTN_SAVE)
async def confirm_save(message: Message, state: FSMContext, bot: Bot):
    d = await state.get_data()
    uid = message.from_user.id
    s = store.staff.get(uid)
    staff_name = s.name if s else full_name(message)
    try:
        await db(store.add_sale, now(), d["name"], d["phone"], d.get("phone2", ""),
                 d["address"], d["product"], d["amount"], staff_name, uid)
    except Exception:
        log.exception("Google Sheets'ga yozib bo'lmadi")
        await message.answer(f"❗ Google Sheets'ga yozishda xatolik. Biroz kutib, yana <b>{BTN_SAVE}</b> ni bosing.",
                             reply_markup=CONFIRM_KB)
        return
    await state.clear()
    await message.answer("✅ Saqlandi! Mijoz Google Sheets'ga yozildi.", reply_markup=menu_kb(uid))
    if not is_admin(uid):
        try:
            await bot.send_message(admin_id, f"🛒 Yangi sotuv — {esc(staff_name)}:\n\n" + card(d))
        except Exception as e:
            log.warning("Adminga xabar yuborilmadi: %s", e)


@router.message(NewClient.confirm)
async def confirm_other(message: Message):
    await message.answer(f"<b>{BTN_SAVE}</b> yoki <b>{BTN_CANCEL}</b> ni bosing.", reply_markup=CONFIRM_KB)


@router.message(NewClient.name)
@router.message(NewClient.address)
@router.message(NewClient.product)
@router.message(NewClient.product_other)
@router.message(NewClient.amount)
async def need_text(message: Message):
    await message.answer("Iltimos, matn ko'rinishida yozing.")


# ---------- hisobotlar ----------
def summarize(sales: list[dict], since: datetime) -> tuple[int, int]:
    items = [s for s in sales if s["date"] >= since]
    return len(items), sum(s["amount"] for s in items)


@router.message(F.text.in_({BTN_REPORT, BTN_MY}))
async def report(message: Message):
    uid = message.from_user.id
    sales = await db(store.all_sales)
    if not (is_admin(uid) and message.text == BTN_REPORT):
        sales = [s for s in sales if s["staff_id"] == uid]

    t = now()
    today = t.replace(hour=0, minute=0, second=0, microsecond=0)
    month = today.replace(day=1)
    c1, s1 = summarize(sales, today)
    c2, s2 = summarize(sales, month)
    c3, s3 = len(sales), sum(s["amount"] for s in sales)

    title = "📊 <b>Umumiy hisobot</b>" if message.text == BTN_REPORT and is_admin(uid) else "📊 <b>Sizning sotuvlaringiz</b>"
    text = (f"{title}\n\n"
            f"Bugun: <b>{c1}</b> ta — {money(s1)}\n"
            f"Shu oy: <b>{c2}</b> ta — {money(s2)}\n"
            f"Jami: <b>{c3}</b> ta — {money(s3)}")

    if message.text == BTN_REPORT and is_admin(uid):
        by_staff: dict[str, list[int]] = {}
        for s in sales:
            if s["date"] >= month:
                v = by_staff.setdefault(s["staff_name"] or str(s["staff_id"]), [0, 0])
                v[0] += 1
                v[1] += s["amount"]
        if by_staff:
            text += "\n\n<b>Shu oy xodimlar bo'yicha:</b>\n" + "\n".join(
                f"• {esc(n)}: {c} ta — {money(a)}"
                for n, (c, a) in sorted(by_staff.items(), key=lambda x: -x[1][1]))
    await message.answer(text, reply_markup=menu_kb(uid))


# ---------- xodimlar ro'yxati (admin) ----------
@router.message(F.text == BTN_STAFF)
async def staff_list(message: Message):
    if not is_admin(message.from_user.id):
        return
    await db(store.reload_staff)
    if not store.staff:
        await message.answer("Hozircha xodim yo'q. Xodimingiz botga /start yozsin — sizga so'rov keladi.")
        return
    for s in store.staff.values():
        icon = {ACTIVE: "✅", PENDING: "⏳", BLOCKED: "🚫"}.get(s.status, "•")
        if s.status == ACTIVE:
            btn = InlineKeyboardButton(text="🚫 O'chirish", callback_data=f"del:{s.user_id}")
        else:
            btn = InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"on:{s.user_id}")
        await message.answer(f"{icon} <b>{esc(s.name)}</b> {esc(s.username)} — {s.status}",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[btn]]))


@router.message()
async def fallback(message: Message):
    await message.answer(f"Yangi mijoz qo'shish uchun <b>{BTN_NEW}</b> ni bosing.",
                         reply_markup=menu_kb(message.from_user.id))


# ---------- ishga tushirish ----------
def setup_storage() -> None:
    global store, admin_id
    store = Storage(CREDENTIALS, SPREADSHEET)
    saved = ADMIN_ID_ENV or store.get_setting("admin_id")
    admin_id = int(saved) if saved and saved.lstrip("-").isdigit() else None


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    setup_storage()
    log.info("Google Sheets ulandi. Admin: %s", admin_id or "hali yo'q (birinchi /start yozgan admin bo'ladi)")
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
