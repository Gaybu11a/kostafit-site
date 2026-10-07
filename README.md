# KostaFit — fitnes klub sayti

Toza HTML/CSS/JS, hech qanday build kerak emas. `index.html` ni brauzerda oching yoki GitHub Pages'ga joylang.

## Tuzilma
- `index.html` — barcha bo'limlar (hero video, dasturlar, video galereya, BMI kalkulyator, murabbiylar, jadval, narxlar, fikrlar, ariza formasi)
- `css/style.css` — dizayn (qora + neon-yashil, Anton + Manrope shriftlari)
- `js/main.js` — animatsiyalar, video modal, BMI, jadval, narx almashtirgich, slayder
- `assets/` — o'z rasm/videolaringiz uchun (qarang: `assets/README.md`)

## Media
Rasmlar Unsplash'dan, videolar Pexels'dan (bepul litsenziya) havola orqali ulangan.
O'zingiznikini qo'yish uchun `index.html` dagi havolalarni almashtiring.
Jadval ma'lumotlari `js/main.js` dagi `schedule` obyektida.

## Google'da chiqarish
1. **GitHub Pages yoqish:** repo → Settings → Pages → Source: "Deploy from a branch", Branch: `main` / `(root)` → Save.
   Sayt manzili: https://gaybu11a.github.io/kostafit-site/
2. **Google Search Console:** https://search.google.com/search-console → "URL prefix" → sayt manzilini kiriting →
   "HTML tag" usulini tanlang → berilgan kodni `index.html` dagi `google-site-verification` qatoriga qo'ying (izohdan chiqarib).
3. Search Console'da **Sitemaps** → `sitemap.xml` ni yuboring, **URL Inspection** → "Request indexing".
4. **Google Maps / Business Profile:** https://business.google.com — "fitnes Toshkent" kabi qidiruvlarda xaritada chiqish uchun.

Agar o'z domeningiz bo'lsa (masalan `kostafit.uz`), `index.html`, `sitemap.xml`, `robots.txt` dagi
`https://gaybu11a.github.io/kostafit-site/` manzilini yangisiga almashtiring.

## O'yin (offline)
`game.html` — **KostaFit Runner**: internetsiz ishlaydigan yugurish o'yini (`game-sw.js` keshlaydi).
Manzil: https://gaybu11a.github.io/kostafit-site/game.html — bir marta oching, keyin offline o'ynash mumkin.
Telefonda "Bosh ekranga qo'shish" orqali ilova kabi o'rnatsa ham bo'ladi.
