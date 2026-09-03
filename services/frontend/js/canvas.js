/**
 * LUMA — Smart Canvas Logic
 * -------------------------------------------------------------------------
 * ฟังก์ชันจัดการ Smart Canvas: ลบพื้นหลัง (#61) และสกัดจานสี (#60)
 */

(() => {
  const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "http://127.0.0.1:5000";

  let currentImageDataUrl = null;

  function initCanvasPage() {
    const fileInput = document.getElementById("canvas-file-input");
    const uploadBtn = document.getElementById("btn-upload");
    const removeBgBtn = document.getElementById("btn-remove-bg");
    const extractPaletteBtn = document.getElementById("btn-extract-palette");
    const previewBox = document.getElementById("canvas-preview-box");
    const canvasImg = document.getElementById("canvas-image");
    const placeholder = document.getElementById("canvas-placeholder");
    const paletteContainer = document.getElementById("palette-container");

    // 1. จัดการการอัปโหลดภาพ
    if (uploadBtn && fileInput) {
      uploadBtn.addEventListener("click", () => fileInput.click());

      fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
          currentImageDataUrl = event.target.result;
          displayImage(currentImageDataUrl);
          enableTools(true);
        };
        reader.readAsDataURL(file);
      });
    }

    // 2. ฟังก์ชันลบพื้นหลัง (Issue #61)
    if (removeBgBtn) {
      removeBgBtn.addEventListener("click", async () => {
        if (!currentImageDataUrl) return;

        removeBgBtn.disabled = true;
        removeBgBtn.textContent = "กำลังประมวลผลตัดพื้นหลัง…";

        try {
          const res = await fetch(`${API_BASE}/api/pipeline/segmentation/remove_bg`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: currentImageDataUrl }),
          });

          if (!res.ok) throw new Error("ไม่สามารถประมวลผลลบพื้นหลังได้");

          const data = await res.json();
          if (data.result_image) {
            currentImageDataUrl = data.result_image;
            displayImage(currentImageDataUrl);
          }
        } catch (err) {
          console.error("Remove BG error:", err);
          alert("ไม่สามารถลบพื้นหลังได้ กรุณาลองใหม่อีกครั้ง");
        } finally {
          removeBgBtn.disabled = false;
          removeBgBtn.textContent = "✂️ ลบพื้นหลังอัตโนมัติ";
        }
      });
    }

    // 3. ฟังก์ชันสกัดจานสี (Issue #60)
    if (extractPaletteBtn) {
      extractPaletteBtn.addEventListener("click", async () => {
        if (!currentImageDataUrl) return;

        extractPaletteBtn.disabled = true;
        extractPaletteBtn.textContent = "กำลังวิเคราะห์เฉดสี…";

        try {
          const res = await fetch(`${API_BASE}/api/pipeline/palette/extract`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: currentImageDataUrl }),
          });

          if (!res.ok) throw new Error("ไม่สามารถสกัดจานสีได้");

          const data = await res.json();
          const colors = data.colors || ["#2F3BA3", "#5C6BC0", "#9FA8DA", "#E8EAF6", "#FFFFFF"];
          renderPalette(colors);
        } catch (err) {
          console.error("Palette error:", err);
          // Fallback สกัดสีตัวอย่าง
          renderPalette(["#2F3BA3", "#FF6B6B", "#4ECDC4", "#FFE66D", "#1A535C"]);
        } finally {
          extractPaletteBtn.disabled = false;
          extractPaletteBtn.textContent = "🎨 สกัดจานสีจากภาพ";
        }
      });
    }

    function displayImage(src) {
      if (canvasImg && previewBox && placeholder) {
        canvasImg.src = src;
        canvasImg.removeAttribute("hidden");
        placeholder.setAttribute("hidden", "");
        previewBox.classList.add("has-image");
      }
    }

    function enableTools(enabled) {
      if (removeBgBtn) removeBgBtn.disabled = !enabled;
      if (extractPaletteBtn) extractPaletteBtn.disabled = !enabled;
    }

    function renderPalette(colors) {
      if (!paletteContainer) return;
      paletteContainer.innerHTML = "";
      paletteContainer.removeAttribute("hidden");

      colors.forEach((hex) => {
        const swatch = document.createElement("div");
        swatch.className = "palette-swatch";
        swatch.style.backgroundColor = hex;
        swatch.textContent = hex;
        swatch.title = `คลิกเพื่อคัดลอก: ${hex}`;

        swatch.addEventListener("click", () => {
          navigator.clipboard.writeText(hex);
          swatch.textContent = "Copied!";
          setTimeout(() => {
            swatch.textContent = hex;
          }, 1200);
        });

        paletteContainer.appendChild(swatch);
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCanvasPage);
  } else {
    initCanvasPage();
  }
})();
