/**
 * LUMA — Gallery Page Logic
 * -------------------------------------------------------------------------
 * ดึงรายการภาพจาก GET /api/assets และแสดงผลแบบ Card Grid
 * พร้อมระบบค้นหาและแบ่งหน้า (Pagination)
 *
 * อ้างอิง: Issue #58, docs/API_CONTRACT.md
 */

(() => {
  const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "http://127.0.0.1:5000";

  let currentPage = 1;
  const perPage = 12;
  let searchQuery = "";

  async function loadGallery(page = 1, query = "") {
    const grid = document.getElementById("gallery-grid");
    const emptyState = document.getElementById("gallery-empty");
    const loadingState = document.getElementById("gallery-loading");
    const pagination = document.getElementById("gallery-pagination");
    const pageInfo = document.getElementById("page-info");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");

    if (!grid) return;

    grid.innerHTML = "";
    if (emptyState) emptyState.setAttribute("hidden", "");
    if (loadingState) loadingState.removeAttribute("hidden");
    if (pagination) pagination.setAttribute("hidden", "");

    try {
      const url = new URL(`${API_BASE}/api/assets`);
      url.searchParams.set("page", page);
      url.searchParams.set("per_page", perPage);
      if (query) url.searchParams.set("q", query);

      const res = await fetch(url.toString());
      if (!res.ok) {
        throw new Error(`ดึงข้อมูลไม่สำเร็จ (HTTP ${res.status})`);
      }

      const data = await res.json();
      const items = data.items || [];
      const total = data.total || 0;
      const totalPages = Math.ceil(total / perPage) || 1;

      currentPage = data.page || page;

      if (items.length === 0) {
        if (emptyState) emptyState.removeAttribute("hidden");
      } else {
        items.forEach((item) => {
          const card = createAssetCard(item);
          grid.appendChild(card);
        });

        if (pagination && total > perPage) {
          pagination.removeAttribute("hidden");
          if (pageInfo) pageInfo.textContent = `หน้า ${currentPage} จาก ${totalPages} (${total} ภาพ)`;
          if (prevBtn) prevBtn.disabled = currentPage <= 1;
          if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
        }
      }
    } catch (err) {
      console.error("เกิดข้อผิดพลาดในการโหลดแกลเลอรี:", err);
      if (emptyState) {
        emptyState.textContent = "ไม่สามารถเชื่อมต่อเพื่อดึงข้อมูลภาพได้ กรุณาตรวจสอบเซิร์ฟเวอร์";
        emptyState.removeAttribute("hidden");
      }
    } finally {
      if (loadingState) loadingState.setAttribute("hidden", "");
    }
  }

  function createAssetCard(item) {
    const card = document.createElement("div");
    card.className = "gallery-card";

    const imgWrap = document.createElement("div");
    imgWrap.className = "gallery-card__image-wrap";

    const img = document.createElement("img");
    img.className = "gallery-card__image";
    const fullImgUrl = item.image_url.startsWith("http")
      ? item.image_url
      : `${API_BASE}${item.image_url}`;
    img.src = fullImgUrl;
    img.alt = item.prompt || "ผลงาน AI";
    img.loading = "lazy";
    imgWrap.appendChild(img);

    const body = document.createElement("div");
    body.className = "gallery-card__body";

    const prompt = document.createElement("p");
    prompt.className = "gallery-card__prompt";
    prompt.textContent = item.prompt || "(ไม่มี prompt)";
    body.appendChild(prompt);

    const footer = document.createElement("div");
    footer.className = "gallery-card__footer";

    const idSpan = document.createElement("span");
    idSpan.textContent = `#${item.id}`;

    const dateSpan = document.createElement("span");
    if (item.created_at) {
      const d = new Date(item.created_at);
      dateSpan.textContent = d.toLocaleDateString("th-TH");
    }
    footer.appendChild(idSpan);
    footer.appendChild(dateSpan);

    body.appendChild(footer);

    card.appendChild(imgWrap);
    card.appendChild(body);

    return card;
  }

  function initGalleryPage() {
    const searchForm = document.getElementById("gallery-search-form");
    const searchInput = document.getElementById("gallery-search-input");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");

    if (searchForm && searchInput) {
      searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        searchQuery = searchInput.value.trim();
        currentPage = 1;
        loadGallery(currentPage, searchQuery);
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (currentPage > 1) {
          loadGallery(currentPage - 1, searchQuery);
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        loadGallery(currentPage + 1, searchQuery);
      });
    }

    loadGallery(1, "");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGalleryPage);
  } else {
    initGalleryPage();
  }
})();
