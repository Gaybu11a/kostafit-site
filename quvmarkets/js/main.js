(() => {
  const TG = "https://t.me/quvmarkets";
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  // ---------- nav ----------
  const nav = $("#nav");
  const burger = $("#burger");
  const links = $("#navLinks");
  const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 10);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  burger.addEventListener("click", () => {
    const open = links.classList.toggle("is-open");
    burger.setAttribute("aria-expanded", open);
  });
  $$("a", links).forEach(a => a.addEventListener("click", () => {
    links.classList.remove("is-open");
    burger.setAttribute("aria-expanded", "false");
  }));

  // ---------- catalog: filter & sort ----------
  const grid = $("#products");
  const cards = $$(".card", grid);
  cards.forEach((c, i) => (c.dataset.order = i));

  $$(".tab").forEach(tab => tab.addEventListener("click", () => {
    $$(".tab").forEach(t => { t.classList.remove("is-active"); t.setAttribute("aria-selected", "false"); });
    tab.classList.add("is-active");
    tab.setAttribute("aria-selected", "true");
    const f = tab.dataset.filter;
    cards.forEach(c => (c.hidden = f !== "all" && c.dataset.cat !== f));
  }));

  $("#sort").addEventListener("change", e => {
    const mode = e.target.value;
    const key = c => mode === "default" ? +c.dataset.order : +c.dataset.price;
    const dir = mode === "desc" ? -1 : 1;
    [...cards].sort((a, b) => (key(a) - key(b)) * dir).forEach(c => grid.appendChild(c));
  });

  // ---------- helpers ----------
  const fmt = n => Number(n).toLocaleString("ru-RU").replace(/ /g, " ") + " so'm";
  const copy = async text => {
    try { await navigator.clipboard.writeText(text); return true; }
    catch {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      let ok = false;
      try { ok = document.execCommand("copy"); } catch {}
      ta.remove();
      return ok;
    }
  };

  // ---------- product select in form ----------
  const select = $("#productSelect");
  cards.forEach(c => {
    const name = $("h3", c).textContent.trim();
    const opt = new Option(`${name} — ${fmt(c.dataset.price)}`, name);
    select.add(opt);
  });

  // ---------- order modal ----------
  const modal = $("#modal");
  let lastFocus = null;
  let orderText = "";
  const openModal = card => {
    const name = $("h3", card).textContent.trim();
    const price = fmt(card.dataset.price);
    $("#modalTitle").textContent = name;
    $("#modalPrice").textContent = price;
    orderText = `Assalomu alaykum! Saytingizdan yozyapman.\nMen "${name}" (${price}) ga buyurtma bermoqchiman. Mavjudmi?`;
    lastFocus = document.activeElement;
    modal.hidden = false;
    $("#modalClose").focus();
  };
  const closeModal = () => { modal.hidden = true; lastFocus && lastFocus.focus(); };
  $$(".order").forEach(btn => btn.addEventListener("click", () => openModal(btn.closest(".card"))));
  $("#modalClose").addEventListener("click", closeModal);
  modal.addEventListener("click", e => { if (e.target === modal) closeModal(); });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !modal.hidden) closeModal(); });
  $("#modalTg").addEventListener("click", () => { copy(orderText); });

  // ---------- quick form -> Telegram ----------
  const form = $("#orderForm");
  const field = n => form.elements.namedItem(n);
  const msg = $("#formMsg");
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const name = field("name").value.trim();
    const phone = field("phone").value.trim();
    field("name").classList.toggle("is-invalid", !name);
    field("phone").classList.toggle("is-invalid", phone.replace(/\D/g, "").length < 9);
    if (!name || phone.replace(/\D/g, "").length < 9) {
      msg.textContent = "Iltimos, ism va telefon raqamini to'g'ri kiriting.";
      msg.classList.add("is-error");
      return;
    }
    const product = field("product").value || "Maslahat kerak";
    const note = field("note").value.trim();
    const text = `Assalomu alaykum! Saytdan ariza.\nIsm: ${name}\nTelefon: ${phone}\nTrenajyor: ${product}` + (note ? `\nIzoh: ${note}` : "");
    const ok = await copy(text);
    msg.classList.remove("is-error");
    msg.textContent = ok
      ? "Xabar nusxalandi! Telegram ochilmoqda — chatga joylashtiring (Paste) va yuboring."
      : "Telegram ochilmoqda — ma'lumotlaringizni yozib yuboring.";
    window.open(TG, "_blank", "noopener");
  });

  // ---------- reveal on scroll ----------
  const targets = $$(".section__head, .feature, .choose__card, .steps li, .faq details, .ccard, .form");
  if ("IntersectionObserver" in window) {
    targets.forEach(t => t.classList.add("reveal"));
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
    }), { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    targets.forEach(t => io.observe(t));
  }

  $("#year").textContent = new Date().getFullYear();
})();
