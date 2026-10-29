# QuvMarkets — yugurish yo'laklari va velotrenajorlar do'koni sayti

Toza HTML/CSS/JS, hech qanday build kerak emas. `index.html` ni brauzerda oching.

Sayt manzili (GitHub Pages yoqilgan bo'lsa): https://gaybu11a.github.io/kostafit-site/quvmarkets/

## Tuzilma
- `index.html` — barcha bo'limlar va mahsulotlar (katalog, afzalliklar, maslahat, savollar, aloqa)
- `css/style.css` — dizayn
- `js/main.js` — filtr/saralash, buyurtma oynasi, Telegram ariza formasi
- `img/products/` — mahsulot rasmlari (900×1200, 3:4 JPG), `img/logo*.{jpg,png}` — logotip

## Mahsulot rasmlari
Rasmlar vertikal 3:4 (masalan 900×1200), JPG, 250 KB dan kichik bo'lsin.
Yangi rasmni `img/products/` ga qo'yib, `index.html` dagi mahsulot kartasidagi `src` ni almashtiring.

## Mahsulot / narx qo'shish yoki o'zgartirish
`index.html` dagi har bir `<article class="card" ... data-price="6800000">` — bitta mahsulot.
Narxni o'zgartirsangiz, `data-price` va ko'rinadigan narxni ikkalasini ham yangilang.
Narx hali ma'lum bo'lmasa `data-price` ni olib tashlang va narx o'rniga "Narxini so'rang" yozing.
Bir nechta rangli mahsulot uchun RUNEX-YT kartasidagi `swatches` blokiga qarang.
Yangi mahsulot uchun bitta `<article>` blokini nusxalab, matnini o'zgartiring
(`data-cat="treadmill"` — yugurish yo'lagi, `data-cat="bike"` — velotrenajor).

## Aloqa ma'lumotlari
Telefon: +998 93 168 94 74, +998 93 103 46 56 · Telegram: @quv_market · Instagram: QuvMarkets.
Do'kon manzilini qo'shmoqchi bo'lsangiz: `index.html` dagi "Offline do'kon" kartasi va
yuqoridagi JSON-LD (`"address"`) qismiga ko'cha nomini yozing.

## Google'da chiqarish
1. GitHub Pages: repo → Settings → Pages → Branch: `main` / `(root)`.
2. https://search.google.com/search-console da sayt manzilini qo'shing, `sitemap.xml` ni yuboring,
   "URL Inspection" → "Request indexing".
3. Eng muhimi: https://business.google.com da **Google Business Profile** oching (do'kon manzili, telefon,
   rasmlar, sayt havolasi) — "begovaya dorojka Toshkent" kabi qidiruvlarda xaritada chiqasiz.
4. Instagram va Telegram profilingizga sayt havolasini qo'ying.
