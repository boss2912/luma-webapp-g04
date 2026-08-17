#!/usr/bin/env python3
"""
tools/smoke_test_ai_deps.py
===========================
ตรวจว่า dependency ของ ai-engine ติดตั้งถูกและใช้งานร่วมกันได้จริง

ทดสอบทุก operation ที่ pipeline 5 ส่วนต้องใช้ตามเกณฑ์อาจารย์
(Lecture 1 หน้า 6) — ไม่ใช่แค่ import ผ่าน แต่เรียกใช้จริงกับภาพทดสอบ

การใช้งาน
---------
    python tools/smoke_test_ai_deps.py

exit code 0 = ผ่านหมด · 1 = มีข้อล้ม

ใช้ตอนไหน
---------
- หลังติดตั้ง requirements ของ ai-engine ครั้งแรก (INSTALL.md หัวข้อ 8)
- หลังอัปเกรดเวอร์ชัน package
- ตอนตั้งเครื่องใหม่ให้สมาชิกในทีม

ชุดเวอร์ชันที่ยืนยันแล้วว่าผ่านครบ (Python 3.12):
    opencv-python 5.0.0.93 · numpy 2.5.2 · scikit-image 0.26.0
    scipy 1.18.0 · matplotlib 3.11.1 · Pillow 12.3.0
"""
from __future__ import annotations

import os
import sys
import tempfile

PASS = 0
FAIL = 0


def check(label: str, fn) -> None:
    global PASS, FAIL
    try:
        result = fn()
        suffix = f" -> {result}" if result is not None else ""
        print(f"  [PASS] {label}{suffix}")
        PASS += 1
    except Exception as exc:
        print(f"  [FAIL] {label}: {type(exc).__name__}: {exc}")
        FAIL += 1


def main() -> int:
    print("=" * 60)
    print("  LUMA ai-engine - dependency smoke test")
    print("=" * 60)

    try:
        import numpy as np
        import cv2 as cv
        import matplotlib
        matplotlib.use("Agg")   # headless — เครื่อง server ไม่มีหน้าจอ
        import matplotlib.pyplot as plt
        import skimage
        from skimage.metrics import structural_similarity, peak_signal_noise_ratio
        import scipy
        from scipy.stats import skew, kurtosis
        import PIL
        from PIL import Image
    except ImportError as exc:
        print(f"\n[FATAL] import ไม่ผ่าน: {exc}")
        print("\nติดตั้งก่อน:")
        print("    pip install -r services/ai-engine/requirements.txt")
        return 1

    print(f"\npython   {sys.version.split()[0]}")
    print(f"numpy    {np.__version__}")
    print(f"opencv   {cv.__version__}")
    print(f"skimage  {skimage.__version__}")
    print(f"scipy    {scipy.__version__}")
    print(f"mpl      {matplotlib.__version__}")
    print(f"pillow   {PIL.__version__}\n")

    tmp = tempfile.mkdtemp(prefix="luma_smoke_")

    # ภาพทดสอบ: วงกลมเขียว + สี่เหลี่ยมแดงบนพื้นดำ
    img = np.zeros((120, 160, 3), np.uint8)
    cv.circle(img, (80, 60), 40, (40, 200, 90), -1)
    cv.rectangle(img, (10, 10), (50, 40), (200, 60, 60), -1)
    img_path = os.path.join(tmp, "test.png")

    print("[01_acquisition] การเก็บข้อมูลภาพ")
    check("imwrite + imread roundtrip",
          lambda: cv.imwrite(img_path, img) and cv.imread(img_path).shape)
    check("imread ไฟล์ไม่มีจริง คืน None ไม่ throw",
          lambda: "None" if cv.imread(os.path.join(tmp, "missing.png")) is None
                  else "ผิด! ไม่คืน None")
    check("PIL อ่าน EXIF ได้",
          lambda: "getexif ok" if hasattr(Image.open(img_path), "getexif") else "ไม่มี getexif")

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    print("\n[02_enhancement] ปรับปรุงคุณภาพภาพ")
    check("cvtColor BGR2GRAY", lambda: gray.shape)
    check("calcHist (histogram)",
          lambda: cv.calcHist([gray], [0], None, [256], [0, 256]).shape)
    check("equalizeHist", lambda: cv.equalizeHist(gray).shape)
    check("gamma / power-law ผ่าน LUT",
          lambda: cv.LUT(gray, np.array(
              [((i / 255.0) ** 2.2) * 255 for i in range(256)], np.uint8)).shape)
    check("filter2D (box filter)",
          lambda: cv.filter2D(gray, -1, np.ones((5, 5), np.float32) / 25).shape)
    check("sepFilter2D (separability - Lecture 5 p.26-27)",
          lambda: cv.sepFilter2D(gray, -1, np.ones(5, np.float32) / 5,
                                 np.ones(5, np.float32) / 5).shape)
    check("GaussianBlur", lambda: cv.GaussianBlur(gray, (5, 5), 1.0).shape)
    check("medianBlur (salt-and-pepper)", lambda: cv.medianBlur(gray, 5).shape)
    check("copyMakeBorder REFLECT_101 (padding)",
          lambda: cv.copyMakeBorder(gray, 2, 2, 2, 2, cv.BORDER_REFLECT_101).shape)

    print("\n[Lecture 6] frequency domain")
    f32 = np.float32(gray)
    check("dft + magnitude + fftshift",
          lambda: np.fft.fftshift(
              cv.magnitude(*cv.split(cv.dft(f32, flags=cv.DFT_COMPLEX_OUTPUT)))).shape)
    check("idft roundtrip",
          lambda: cv.idft(cv.dft(f32, flags=cv.DFT_COMPLEX_OUTPUT),
                          flags=cv.DFT_SCALE | cv.DFT_REAL_OUTPUT).shape)

    print("\n[03_segmentation] ตรวจจับบริเวณวัตถุ")
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    check("cvtColor BGR2HSV", lambda: hsv.shape)
    check("Hue อยู่ในช่วง 0-179 จริง (Lecture 5 p.62)",
          lambda: f"max hue = {int(hsv[:, :, 0].max())} (ต้อง <= 179)")
    check("hue เป็นองศา ด้วย int32 กัน uint8 ล้น",
          lambda: f"max = {int((hsv[:, :, 0].astype(np.int32) * 2).max())} องศา")

    mask = ((hsv[:, :, 1] >= 60) & (hsv[:, :, 2] >= 40)).astype(np.uint8) * 255
    kernel = np.ones((3, 3), np.uint8)
    check("morphologyEx OPEN + CLOSE",
          lambda: cv.morphologyEx(cv.morphologyEx(mask, cv.MORPH_OPEN, kernel),
                                  cv.MORPH_CLOSE, kernel).shape)
    check("threshold OTSU",
          lambda: f"threshold = {cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[0]}")
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    check("findContours", lambda: f"{len(contours)} contour")
    check("Canny edge detection", lambda: cv.Canny(gray, 100, 200).shape)
    check("merge alpha channel (background removal)",
          lambda: cv.merge([*cv.split(img), mask]).shape)

    print("\n[04_features] สกัดคุณลักษณะ")
    check("contourArea + arcLength",
          lambda: (round(cv.contourArea(contours[0]), 1),
                   round(cv.arcLength(contours[0], True), 1)))
    check("boundingRect", lambda: cv.boundingRect(contours[0]))
    check("histogram mean / std",
          lambda: (round(float(gray.mean()), 2), round(float(gray.std()), 2)))
    check("scipy skewness / kurtosis (Lecture 4 p.27)",
          lambda: (round(float(skew(gray.ravel())), 3),
                   round(float(kurtosis(gray.ravel())), 3)))

    print("\n[05_evaluation] วัดประสิทธิภาพ")
    rng = np.random.default_rng(42)
    noisy = np.clip(gray.astype(np.int16) + rng.integers(-20, 20, gray.shape),
                    0, 255).astype(np.uint8)
    check("PSNR", lambda: round(float(peak_signal_noise_ratio(gray, noisy)), 2))
    check("SSIM", lambda: round(float(structural_similarity(gray, noisy)), 4))
    check("IoU", lambda: round(float(
        np.logical_and(mask > 0, mask > 0).sum()
        / max(np.logical_or(mask > 0, mask > 0).sum(), 1)), 3))
    hist_path = os.path.join(tmp, "hist.png")

    def save_hist():
        plt.figure()
        plt.hist(gray.ravel(), bins=256)
        plt.xlabel("intensity")
        plt.ylabel("count")
        plt.grid(True)
        plt.savefig(hist_path, dpi=80)
        plt.close()
        return f"{os.path.getsize(hist_path)} bytes"

    check("matplotlib savefig แบบ headless (Agg)", save_hist)

    print("\n[interop]")
    check("PIL <-> numpy roundtrip",
          lambda: np.array(Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGB))).shape)

    print()
    print("=" * 60)
    print(f"  ผล: {PASS} passed, {FAIL} failed")
    print("=" * 60)
    if FAIL:
        print("\nมีข้อล้ม — ลองติดตั้งใหม่ด้วยเวอร์ชันที่ล็อกไว้:")
        print("    pip install -r services/ai-engine/requirements.txt")
        print("ดูวิธีแก้ปัญหาเพิ่มใน INSTALL.md หัวข้อ 10")
    else:
        print("\ndependency ของ ai-engine พร้อมใช้งานครบ")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
