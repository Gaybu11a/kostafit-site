# QuvMarkets sotuv boti (Telegram → Google Sheets)

Xodimlar botga mijoz ma'lumotlarini kiritadi. Har bir yozuv Google Sheets'dagi **Sotuvlar** varag'iga tushadi:

| Sana | Mijoz ismi | Telefon | Qo'shimcha telefon | Manzil | Mahsulot | Summa (so'm) | Xodim | Xodim ID |
|---|---|---|---|---|---|---|---|---|

**Admin (siz):**
- xodimlarga ruxsat berasiz yoki rad etasiz, keyinroq o'chirib ham qo'yasiz (👥 Xodimlar);
- har bir yangi sotuv haqida xabar olasiz;
- 📊 Hisobot: bugun, shu oy va jami sotuvlar, xodimlar bo'yicha bo'lingan holda.

**Xodim:**
- ➕ Yangi mijoz: ism → telefon → qo'shimcha telefon (ixtiyoriy) → manzil → mahsulot → summa → ✅ Saqlash;
- 📊 Mening sotuvlarim.

Bot quyidagi varaqlarni o'zi yaratadi:
- **Sotuvlar** — mijozlar yoziladigan asosiy varaq;
- **Xodimlar** — xodimlar ro'yxati;
- **Sozlamalar** — admin ID saqlanadi.

---

## O'rnatish

### 1. Telegram bot yaratish
1. Telegram'da [@BotFather](https://t.me/BotFather) ni oching → `/newbot`.
2. Botga nom bering (masalan `QuvMarkets Sotuv`), keyin username bering (masalan `quvmarkets_sotuv_bot`).
3. BotFather bergan **token**ni saqlab qo'ying (`1234567890:AA...` ko'rinishida). Uni hech kimga bermang.

### 2. Google Sheets jadval
1. https://sheets.google.com da yangi jadval oching (masalan "QuvMarkets mijozlar").
2. Brauzer manzil satridagi havolani nusxalang.

### 3. Google service account (bot jadvalga yozishi uchun "kalit")
1. https://console.cloud.google.com ga kiring → yuqorida **Select a project → New project** → nom bering → **Create**.
2. **APIs & Services → Library** bo'limida **Google Sheets API** ni toping → **Enable**. **Google Drive API** ni ham yoqing.
3. **APIs & Services → Credentials → Create credentials → Service account** → nom bering → **Done**.
4. Yaratilgan service account'ni oching → **Keys → Add key → Create new key → JSON**. Kompyuteringizga fayl yuklanadi.
5. Shu faylni `service-account.json` deb qayta nomlang.
6. Faylni oching va `client_email` qatoridagi manzilni nusxalang (`...@....iam.gserviceaccount.com`).
7. Google Sheets jadvalingizda **Share (Bulish)** tugmasini bosing → shu email'ni qo'shing → **Editor** huquqini bering → **Send**.

### 4. Raven Host'ga joylash (panel orqali)
1. Raven Host panelida yangi server oching va turini **Python** qilib tanlang. Python versiyasi **3.10 yoki undan yangi** bo'lsin (3.11/3.12 tavsiya qilinadi).
2. **Files (Fayllar)** bo'limiga quyidagi fayllarni yuklang:
   - `bot.py`, `storage.py`, `requirements.txt` (yoki ZIP arxivni yuklab, **Unarchive** qiling);
   - `service-account.json` (3-qadamda olingan Google kaliti).
3. Panelda **New file** tugmasi orqali `.env` nomli fayl yarating. Ichiga quyidagini yozing:
   ```
   BOT_TOKEN=BotFather bergan token
   SPREADSHEET=Google Sheets jadval havolasi
   GOOGLE_CREDENTIALS=service-account.json
   ```
4. **Startup** bo'limida quyidagilarni sozlang:
   - ishga tushadigan fayl (App py file / Startup file) — `bot.py`;
   - requirements fayli — `requirements.txt`.
5. **Console** bo'limida **Start** ni bosing. Kutubxonalar o'rnatiladi, keyin ekranda `Google Sheets ulandi` yozuvi chiqadi.
6. Bot ishlayotganini tekshirish uchun Telegram'da botga `/start` yozing.

> Bepul serverlarda ba'zan muddatni uzaytirish (renew) talab qilinadi. Panelda shunday tugma bo'lsa, vaqtida bosib turing.

### 4b. Oddiy Linux VPS'ga joylash
`bot` papkasini serverga ko'chiring. `service-account.json` faylini ham shu papkaga qo'ying. Keyin quyidagilarni bajaring:

```bash
cd bot
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
nano .env        # BOT_TOKEN va SPREADSHEET ni yozing
./venv/bin/python bot.py
```

Ekranda `Google Sheets ulandi` yozuvi chiqsa, bot ishlayapti.

### 5. Birinchi ishga tushirish
1. **Avval o'zingiz** botga `/start` yozing. Birinchi `/start` yozgan odam **admin** bo'ladi.
2. Xodimlaringiz botga `/start` yozadi. Sizga so'rov keladi, **✅ Ruxsat berish** tugmasini bosasiz.

### 6. Bot doim ishlab turishi uchun (faqat oddiy Linux VPS, Raven Host uchun kerak emas)
```bash
sudo cp quvbot.service /etc/systemd/system/   # ichidagi USER va yo'llarni to'g'rilang
sudo systemctl daemon-reload
sudo systemctl enable --now quvbot
sudo systemctl status quvbot      # holatini ko'rish
journalctl -u quvbot -f           # loglarni ko'rish
```

---

## Sozlash
- **Mahsulotlar ro'yxati:** `bot.py` dagi `PRODUCTS` ro'yxatini o'zgartiring. Xodim ro'yxatda yo'q mahsulotni "✍️ Boshqa mahsulot" orqali qo'lda yozishi ham mumkin.
- **Adminni almashtirish:** `.env` faylida `ADMIN_ID=` ga yangi admin Telegram ID sini yozing yoki jadvaldagi **Sozlamalar** varag'idan `admin_id` ni o'zgartiring. Keyin botni qayta ishga tushiring.
- **Xodimni o'chirish:** botda 👥 Xodimlar → 🚫 O'chirish. Yoki **Xodimlar** varag'idagi "Holat" ustuniga `o'chirilgan` deb yozing.

## Xavfsizlik
`.env` va `service-account.json` fayllarini GitHub'ga **yuklamang**. Ular `.gitignore` ga qo'shilgan.
