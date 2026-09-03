/**
 * LUMA — Shared layout loader
 */

async function initLayout() {
  const slot = document.getElementById("app-nav-slot");
  if (!slot) return;

  try {
    const res = await fetch("../partials/nav.html");
    if (!res.ok) {
      throw new Error(`โหลด nav.html ไม่สำเร็จ (HTTP ${res.status})`);
    }
    slot.innerHTML = await res.text();
    markCurrentPage();
    setupMobileToggle();
  } catch (err) {
    console.error("[layout] โหลดเมนูไม่สำเร็จ:", err);
  }
}

function markCurrentPage() {
  const current = document.body.dataset.page;
  if (!current) return;
  document.querySelectorAll(".app-nav__link").forEach((link) => {
    if (link.dataset.page === current) {
      link.setAttribute("aria-current", "page");
    }
  });
}

function setupMobileToggle() {
  const toggle = document.querySelector(".app-header__toggle");
  const nav = document.querySelector(".app-nav");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

document.addEventListener("DOMContentLoaded", initLayout);
