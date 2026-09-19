/**
 * LUMA — Mock Auth (ชั่วคราว)
 * -------------------------------------------------------------------------
 * จำลองพฤติกรรมของ backend ตาม docs/API_CONTRACT.md (#32, #49 ปิดแล้ว)
 * ไว้ทดสอบ flow ฝั่ง frontend ก่อนที่ backend ตัวจริงจะรันได้จริง
 *
 * เก็บ "ฐานข้อมูลผู้ใช้จำลอง" ไว้ใน localStorage ของเบราว์เซอร์ (คงอยู่ข้าม
 * การรีเฟรชหน้า) เพื่อให้ทดสอบ register แล้ว login ต่อได้จริงในเครื่องเดียว
 *
 * ⚠️ ของปลอมทั้งหมด ห้ามใช้ในโปรดักชันเด็ดขาด — เก็บรหัสผ่านเป็น plain
 * text ในนี้เพื่อความง่ายตอน dev เท่านั้น (backend จริงต้อง hash เสมอ)
 *
 * พอ backend จริงรันได้แล้ว (ไม่ใช่แค่ contract ปิด แต่ endpoint ทำงานจริง)
 * ให้ไปลบ TODO ใน login.js / register.js แล้วสลับไปเรียก fetch() ตรง
 * แทนไฟล์นี้ จากนั้นลบไฟล์นี้และ <script> ที่อ้างถึงมันออกจาก HTML ทุกหน้า
 */

const MOCK_STORAGE_KEY = "luma_mock_users";
const MOCK_DELAY_MS = 500;

function readMockUsers() {
  try {
    const raw = localStorage.getItem(MOCK_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeMockUsers(users) {
  localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(users));
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * จำลอง POST /api/register
 * คืนรูปแบบเดียวกับที่ fetch() จริงจะคืน { ok, status, data }
 * เพื่อให้สลับกลับไปใช้ fetch() จริงทีหลังได้ง่าย ไม่ต้องแก้โค้ดที่เรียกใช้
 */
async function mockRegister({ displayName, email, password }) {
  await delay(MOCK_DELAY_MS);
  const users = readMockUsers();

  // จำลองพฤติกรรม "กันการเดาว่ามีบัญชีอยู่จริง" ตาม #49
  // ข้อความ error ต้องเหมือนกันไม่ว่าอีเมลจะซ้ำหรือข้อมูลผิดฟอร์แมต
  const exists = users.some((u) => u.email === email);
  if (exists) {
    return {
      ok: false,
      status: 409,
      data: { message: "สมัครสมาชิกไม่สำเร็จ ตรวจสอบข้อมูลอีกครั้ง" },
    };
  }

  users.push({ displayName, email, password });
  writeMockUsers(users);
  return { ok: true, status: 201, data: { email, displayName } };
}

/** จำลอง POST /api/login */
async function mockLogin({ email, password }) {
  await delay(MOCK_DELAY_MS);
  const users = readMockUsers();
  const found = users.find(
    (u) => u.email === email && u.password === password
  );

  if (!found) {
    return {
      ok: false,
      status: 401,
      data: { message: "อีเมลหรือรหัสผ่านไม่ถูกต้อง" },
    };
  }

  return {
    ok: true,
    status: 200,
    data: { email: found.email, displayName: found.displayName },
  };
}

/** ล้างฐานข้อมูลจำลองทั้งหมด — เรียกจาก Console ตอนอยากเริ่มทดสอบใหม่ */
function resetMockUsers() {
  localStorage.removeItem(MOCK_STORAGE_KEY);
}

window.LUMA_MOCK_AUTH = { mockRegister, mockLogin, resetMockUsers };