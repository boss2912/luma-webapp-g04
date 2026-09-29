/**
 * LUMA — PNG Info
 * -------------------------------------------------------------------------
 * ใส่ไฟล์ PNG แล้วอ่าน prompt/ค่าที่ใช้สร้างภาพที่อาจฝังอยู่ในไฟล์ (chunk "parameters"
 * มาตรฐานของ Stable Diffusion WebUI/Forge) — ใช้ได้กับ PNG จากที่ไหนก็ได้ ไม่ใช่แค่
 * ภาพในคลังผลงานของแอปนี้
 *
 * POST /api/pipeline/png-info (docs/API_CONTRACT.md) · ห้าม hardcode localhost/IP
 */

(() => {
  const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "";

  function initPngInfo() {
    const upload = document.getElementById("pi-upload");
    if (!upload) return;

    const submitBtn = document.getElementById("pi-submit");
    const errorBox = document.getElementById("pi-error");
    const previewContainer = document.getElementById("pi-preview-container");
    const previewImg = document.getElementById("pi-preview-img");
    const placeholder = document.getElementById("pi-placeholder");
    const result = document.getElementById("pi-result");
    const resultTitle = document.getElementById("pi-result-title");
    const parametersBox = document.getElementById("pi-parameters");

    let currentDataUrl = null;

    function showError(message) {
      errorBox.textContent = message;
      errorBox.removeAttribute("hidden");
    }

    function clearError() {
      errorBox.textContent = "";
      errorBox.setAttribute("hidden", "");
    }

    function hideResult() {
      result.setAttribute("hidden", "");
      resultTitle.textContent = "";
      parametersBox.textContent = "";
    }

    upload.addEventListener("change", () => {
      const file = upload.files && upload.files[0];
      clearError();
      hideResult();
      currentDataUrl = null;
      submitBtn.disabled = true;
      if (!file) return;

      if (file.type !== "image/png") {
        showError("กรุณาเลือกไฟล์ .png เท่านั้น");
        upload.value = "";
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        currentDataUrl = reader.result;
        previewImg.src = currentDataUrl;
        previewImg.removeAttribute("hidden");
        placeholder.setAttribute("hidden", "");
        previewContainer.classList.add("has-image");
        submitBtn.disabled = false;
      };
      reader.onerror = () => showError("อ่านไฟล์ไม่สำเร็จ");
      reader.readAsDataURL(file);
    });

    submitBtn.addEventListener("click", async () => {
      if (!currentDataUrl) return;
      clearError();
      hideResult();
      submitBtn.disabled = true;
      const label = submitBtn.textContent;
      submitBtn.textContent = "กำลังอ่าน...";

      try {
        const res = await fetch(`${API_BASE}/api/pipeline/png-info`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...window.csrfHeaders() },
          body: JSON.stringify({ image: currentDataUrl }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data.error || `อ่านข้อมูลไม่สำเร็จ (HTTP ${res.status})`);
        }

        if (data.found) {
          resultTitle.textContent = "พบข้อมูลที่ฝังอยู่ในภาพนี้";
          parametersBox.textContent = data.parameters;
        } else {
          resultTitle.textContent = "ไม่พบข้อมูลที่ฝังอยู่ในภาพนี้";
          parametersBox.textContent = "";
        }
        result.removeAttribute("hidden");
      } catch (err) {
        showError(err.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = label;
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPngInfo);
  } else {
    initPngInfo();
  }
})();
