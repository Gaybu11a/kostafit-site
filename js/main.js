// ---------- nav ----------
const nav = document.getElementById("nav");
const burger = document.getElementById("burger");
const navLinks = document.getElementById("navLinks");

addEventListener("scroll", () => nav.classList.toggle("is-scrolled", scrollY > 40), { passive: true });

burger.addEventListener("click", () => {
  const open = navLinks.classList.toggle("is-open");
  burger.setAttribute("aria-expanded", open);
  document.body.style.overflow = open ? "hidden" : "";
});
navLinks.querySelectorAll("a").forEach((a) =>
  a.addEventListener("click", () => {
    navLinks.classList.remove("is-open");
    burger.setAttribute("aria-expanded", false);
    document.body.style.overflow = "";
  })
);

// ---------- hero video: fall back to poster image if no source loads ----------
const heroVideo = document.getElementById("heroVideo");
const heroSources = heroVideo.querySelectorAll("source");
heroSources[heroSources.length - 1].addEventListener("error", () => {
  heroVideo.removeAttribute("autoplay");
});

// ---------- reveal on scroll + counters ----------
const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("is-in");
      const num = e.target.querySelector("[data-count]");
      if (num) countUp(num);
      io.unobserve(e.target);
    });
  },
  { threshold: 0.15 }
);
document.querySelectorAll(".reveal").forEach((el, i) => {
  el.style.transitionDelay = `${(i % 4) * 80}ms`;
  io.observe(el);
});

function countUp(el) {
  const target = +el.dataset.count;
  const start = performance.now();
  const dur = 1600;
  const tick = (now) => {
    const p = Math.min((now - start) / dur, 1);
    el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString("ru-RU");
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

// ---------- video modal ----------
const modal = document.getElementById("modal");
const modalVideo = document.getElementById("modalVideo");
const closeModal = () => {
  modalVideo.pause();
  modalVideo.removeAttribute("src");
  modalVideo.load();
  modal.hidden = true;
  document.body.style.overflow = "";
};
document.querySelectorAll("[data-video]").forEach((btn) =>
  btn.addEventListener("click", () => {
    modalVideo.src = btn.dataset.video;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    modalVideo.play().catch(() => {});
  })
);
document.getElementById("modalClose").addEventListener("click", closeModal);
modal.addEventListener("click", (e) => e.target === modal && closeModal());
addEventListener("keydown", (e) => e.key === "Escape" && !modal.hidden && closeModal());

// ---------- BMI ----------
document.getElementById("bmiForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const h = +document.getElementById("height").value / 100;
  const w = +document.getElementById("weight").value;
  if (!h || !w) return;
  const bmi = w / (h * h);
  const [label] = [
    [18.5, "Vazn yetishmaydi — massa oshirish dasturi tavsiya etiladi"],
    [25, "Normal vazn — zo'r! Formani saqlab qolamiz"],
    [30, "Ortiqcha vazn — HIIT va ovqatlanish rejasi yordam beradi"],
    [Infinity, "Semizlik — murabbiy bilan individual reja tuzamiz"],
  ].find(([max]) => bmi < max).slice(1);
  document.getElementById("bmiValue").textContent = bmi.toFixed(1);
  document.getElementById("bmiLabel").textContent = label;
  const pointer = document.getElementById("bmiPointer");
  // bar scale: 15 → 40
  pointer.style.left = `${Math.min(Math.max((bmi - 15) / 25, 0), 1) * 100}%`;
  pointer.style.opacity = 1;
});

// ---------- schedule ----------
const schedule = {
  Dush: [["07:00", "Morning HIIT", "Malika R.", "Barcha"], ["12:30", "Yoga Flow", "Dilnoza U.", "Boshlang'ich"], ["18:00", "Powerlifting", "Jasur K.", "O'rta"], ["20:00", "Boks", "Bekzod A.", "Barcha"]],
  Sesh: [["08:00", "Stretching", "Dilnoza U.", "Barcha"], ["17:30", "Funksional", "Malika R.", "O'rta"], ["19:30", "Kikboks", "Bekzod A.", "Yuqori"]],
  Chor: [["07:00", "Morning HIIT", "Malika R.", "Barcha"], ["13:00", "Core & Abs", "Jasur K.", "Barcha"], ["18:00", "Powerlifting", "Jasur K.", "Yuqori"], ["20:00", "Yoga Calm", "Dilnoza U.", "Barcha"]],
  Pay: [["08:00", "Mobility", "Dilnoza U.", "Barcha"], ["18:30", "CrossFit WOD", "Malika R.", "Yuqori"], ["20:00", "Boks", "Bekzod A.", "Barcha"]],
  Juma: [["07:00", "Morning HIIT", "Malika R.", "Barcha"], ["17:00", "Full Body", "Jasur K.", "O'rta"], ["19:00", "Sparring", "Bekzod A.", "Yuqori"]],
  Shan: [["10:00", "Bootcamp", "Malika R.", "Barcha"], ["12:00", "Yoga Flow", "Dilnoza U.", "Barcha"]],
  Yak: [["11:00", "Family Fit", "Jasur K.", "Barcha"], ["17:00", "Stretching", "Dilnoza U.", "Barcha"]],
};
const dayTabs = document.getElementById("dayTabs");
const scheduleList = document.getElementById("scheduleList");
const days = Object.keys(schedule);

function renderDay(day) {
  dayTabs.querySelectorAll(".tab").forEach((t) => {
    const on = t.textContent === day;
    t.classList.toggle("is-active", on);
    t.setAttribute("aria-selected", on);
  });
  scheduleList.innerHTML = schedule[day]
    .map(
      ([time, name, coach, lvl], i) => `
      <div class="row" style="animation-delay:${i * 70}ms">
        <span class="row__time">${time}</span>
        <span class="row__name">${name}</span>
        <span class="row__coach">${coach}</span>
        <span class="row__lvl">${lvl}</span>
      </div>`
    )
    .join("");
}
days.forEach((day) => {
  const b = document.createElement("button");
  b.className = "tab";
  b.setAttribute("role", "tab");
  b.textContent = day;
  b.addEventListener("click", () => renderDay(day));
  dayTabs.appendChild(b);
});
// open on today's weekday (Mon=0)
renderDay(days[(new Date().getDay() + 6) % 7]);

// ---------- pricing toggle ----------
const billingSwitch = document.getElementById("billingSwitch");
billingSwitch.addEventListener("click", () => {
  const yearly = billingSwitch.getAttribute("aria-pressed") !== "true";
  billingSwitch.setAttribute("aria-pressed", yearly);
  document.querySelectorAll(".plan__price b").forEach((b) => {
    b.textContent = yearly ? b.dataset.year : b.dataset.month;
  });
});

// ---------- testimonials slider ----------
const slides = [...document.querySelectorAll(".slide")];
const dots = document.getElementById("sliderDots");
let current = 0;
let timer;
function go(i) {
  slides[current].classList.remove("is-active");
  dots.children[current].classList.remove("is-active");
  current = (i + slides.length) % slides.length;
  slides[current].classList.add("is-active");
  dots.children[current].classList.add("is-active");
  clearInterval(timer);
  timer = setInterval(() => go(current + 1), 6000);
}
slides.forEach((_, i) => {
  const d = document.createElement("button");
  d.setAttribute("aria-label", `${i + 1}-fikr`);
  d.addEventListener("click", () => go(i));
  dots.appendChild(d);
});
go(0);

// ---------- lead form ----------
document.getElementById("leadForm").addEventListener("submit", (e) => {
  e.preventDefault();
  // TODO: arizani Telegram bot yoki backendga yuborish shu yerda ulanadi
  e.target.reset();
  document.getElementById("formOk").hidden = false;
});

document.getElementById("year").textContent = new Date().getFullYear();
