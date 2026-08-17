# tools/ — สคริปต์ช่วยงาน

สคริปต์ที่ใช้พัฒนา/ตรวจงาน ไม่ใช่ส่วนของระบบที่ deploy

ตัวอย่างที่น่าจะต้องมี:
- mock Forge AI server — ทดสอบ backend โดยไม่ต้องเปิด Stable Diffusion จริง
- สคริปต์ตรวจว่าไม่มี secret / ไฟล์ `.db` หลุดขึ้น git
- สคริปต์รวม test ทุก service
- สคริปต์ตรวจว่า `requirements.txt` เป็น ASCII ล้วน
  (คอมเมนต์ไทยทำให้ `pip install -r` พังบนเครื่อง locale ไทย — ดู `archive/ARCHITECTURE_v1.md` ปัญหา B)
