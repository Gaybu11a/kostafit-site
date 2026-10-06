# QuvMarkets — yugurish yo'laklari va velotrenajorlar do'koni sayti

Toza HTML/CSS/JS, hech qanday build kerak emas. `index.html` ni brauzerda oching.

Sayt manzili (GitHub Pages yoqilgan bo'lsa): https://gaybu11a.github.io/kostafit-site/quvmarkets/

## Tuzilma
- `index.html` — barcha bo'limlar va mahsulotlar (katalog, afzalliklar, maslahat, savollar, aloqa)
- `css/style.css` — dizayn
- `js/main.js` — filtr/saralash, buyurtma oynasi, Telegram ariza formasi
- `img/` — vaqtinchalik rasmlar

## Rasmlarni o'z mahsulotingiz rasmiga almashtirish
1. Rasmingizni `img/products/` papkasiga qo'ying (masalan `yugurish-yolagi-20.jpg`).
2. `index.html` da shu mahsulotdagi `src="img/products/yugurish-yolagi-20.svg"` ni `.jpg` ga almashtiring.
   Eng yaxshi o'lcham: 1200×900 (4:3), 300 KB dan kichik.
3. Bosh sahifadagi katta rasmlar: `img/hero.svg` va `img/hero-bike.svg`.

## Mahsulot / narx qo'shish yoki o'zgartirish
`index.html` dagi har bir `<article class="card" ... data-price="6800000">` — bitta mahsulot.
Narxni o'zgartirsangiz, `data-price` va ko'rinadigan narxni ikkalasini ham yangilang.
Yangi mahsulot uchun bitta `<article>` blokini nusxalab, matnini o'zgartiring
(`data-cat="treadmill"` — yugurish yo'lagi, `data-cat="bike"` — velotrenajor).

## Aloqa ma'lumotlari
Telefon: +998 99 610 99 06 · Telegram: @quvmarkets · Instagram: QuvMarkets.
Do'kon manzilini qo'shmoqchi bo'lsangiz: `index.html` dagi "Offline do'kon" kartasi va
yuqoridagi JSON-LD (`"address"`) qismiga ko'cha nomini yozing.

## Google'da chiqarish
1. GitHub Pages: repo → Settings → Pages → Branch: `main` / `(root)`.
2. https://search.google.com/search-console da sayt manzilini qo'shing, `sitemap.xml` ni yuboring,
   "URL Inspection" → "Request indexing".
3. Eng muhimi: https://business.google.com da **Google Business Profile** oching (do'kon manzili, telefon,
   rasmlar, sayt havolasi) — "begovaya dorojka Toshkent" kabi qidiruvlarda xaritada chiqasiz.
4. Instagram va Telegram profilingizga sayt havolasini qo'ying.
