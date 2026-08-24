/**
 * LUMA — Shared layout loader
 * -------------------------------------------------------------------------
 * โหลด partials/nav.html มาใส่ทุกหน้า เพื่อให้ layout กลาง (เมนู) เหมือนกัน
 * ทุกหน้า โดยไม่ต้องพึ่ง server-side templating เพราะ frontend เป็น static
 * file ล้วน (ดู services/frontend/README.md)
 *
 * วิธีใช้: ใส่ <div id="app-nav-slot"></div> ไว้ใน <header> ของหน้า
 * แล้วโหลดสคริปต์นี้ท้าย body — initLayout() รันเองตอน DOMContentLoaded
 *
 * อ่าน API base URL จาก window.LUMA_CONFIG เสมอ ห้าม hardcode
 * localhost/IP ในไฟล์นี้หรือไฟล์อื่น (CONTRIBUTING.md)
 */

const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "";

async function initLayout() {
  const slot = document.getElementById("app-nav-slot");
  if (!slot) return; // หน้าไหนไม่มี slot ก็ข้าม ไม่ throw ให้ทั้งหน้าพัง

  try {
    const res = await fetch("../partials/nav.html");
    if (!res.ok) {
      throw new Error(`โหลด nav.html ไม่สำเร็จ (HTTP ${res.status})`);
    }
    slot.innerHTML = await res.text();
    markCurrentPage();
    setupMobileToggle();
  } catch (err) {
    // โหลดเมนูไม่สำเร็จไม่ควรทำให้ทั้งหน้าเว็บใช้งานไม่ได้
    // แค่รายงานใน console แล้วปล่อยให้เนื้อหาหลัก (main) ยังใช้ได้ต่อ
    console.error("[layout] โหลดเมนูไม่สำเร็จ:", err);
  }
}

/** ใส่ aria-current="page" ให้ลิงก์เมนูของหน้าปัจจุบัน (ผูกจาก body[data-page]) */
function markCurrentPage() {
  const current = document.body.dataset.page;
  if (!current) return;
  document.querySelectorAll(".app-nav__link").forEach((link) => {
    if (link.dataset.page === current) {
      link.setAttribute("aria-current", "page");
    }
  });
}

/** ปุ่ม hamburger กาง/ยุบเมนูบนจอมือถือ ด้วย class .is-open (ไม่ใช้ [hidden]) */
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