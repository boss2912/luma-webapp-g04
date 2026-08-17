# pipeline/ — Image Processing 5 ส่วนตามเกณฑ์อาจารย์

👤 คนที่ 3 — AI + Image Processing Engine

## ทำไมต้องแบ่งเป็น 5 โฟลเดอร์แบบนี้

**Lecture 1 หน้า 6** — อาจารย์ระบุตรงๆ ว่า:

> "โครงงานแบ่งการออกแบบระบบการประมวลผลภาพเป็นส่วนย่อย
> 1. การเก็บข้อมูลภาพ (Image Acquisition)
> 2. การตรวจสอบคุณภาพและปรับปรุงคุณภาพของภาพ (Quality Assessment & Enhancement)
> 3. การตรวจจับบริเวณของวัตถุที่ต้องการ (Segmentation)
> 4. การสกัดคุณลักษณะสำคัญ (Feature Extraction) → คัดแยก (Classification) / วิเคราะห์ (Analysis)
> 5. การวัดประสิทธิภาพการทำงานของโครงงาน (Evaluation)"

**โครงงาน = 40% ของคะแนนวิชา** และ 5 ข้อนี้คือโครงที่อาจารย์ใช้ตรวจ
โฟลเดอร์จึงตั้งชื่อ 1:1 กับตารางนั้น เพื่อให้ตอนนำเสนอชี้ได้ทันทีว่าแต่ละข้ออยู่ไหน

## Pipeline ภาพรวม (Lecture 1 หน้า 7)

```
Visual Problem Domain → Image Acquisition → Image Enhancement
    → Feature Extraction → Object Recognition → Image Understanding
```

## กฎการเขียนโค้ดในโฟลเดอร์นี้

1. **แต่ละโมดูลรับ/คืน NumPy array** ไม่รับ path ไม่รับ Flask request
   → test ได้ง่าย และเอาไปใช้ที่อื่นได้
2. **ห้าม import Flask** ในโฟลเดอร์นี้ — เป็น pure image processing
   ตัวเชื่อมกับเว็บอยู่ที่ `backend/app/services/`
3. ทุกโมดูลต้องมี **ภาพตัวอย่าง before/after** ใน `../samples/output/`
   ใช้ประกอบรายงานและการนำเสนอ
4. เขียน docstring บอกว่า **มาจากสไลด์หน้าไหน** — ตอนทำรายงานจะอ้างอิงได้เลย

## ข้อ 5 คือข้อที่มักถูกลืม

`05_evaluation/` ต้องมี **ตัวเลขวัดผลจริง** ไม่ใช่แค่ "ทำงานได้"
เป็นข้อที่อาจารย์ระบุไว้ชัดแต่ทีมมักข้าม

## ของที่มีอยู่แล้วและหยิบมาใช้ได้ทันที

| ที่มา | ใช้กับ |
|---|---|
| `Assignment/#4-Your Camera/` — ข้อมูลกล้อง + ภาพถ่าย | `01_acquisition` |
| `Assignment/#5-Filtering_and_Color_Models/Assignment5_1_Convolution.py` | `02_enhancement` |
| `Assignment/#5-Filtering_and_Color_Models/Assignment5_2_Color_Hue.py` | `03_segmentation` |

> รายละเอียดว่าโค้ดเดิมทำอะไรถูกไว้แล้ว ดู `docs/COURSE_REQUIREMENTS.md` ข้อ 8
