# 📘 Final Project Documentation: AI Auto Form Filler (Genius Mode)

เอกสารฉบับนี้สรุปโครงสร้างการทำงานทั้งหมดของโปรเจกต์ **AI Brain Auto Forms** เพื่อให้เข้าใจระบบตั้งแต่ต้นจบจบ เหมาะสำหรับการทบทวนและการพัฒนาต่อยอด

---

## 🏗️ 1. ภาพรวมโครงสร้างโปรเจกต์ (System Architecture)

ระบบถูกออกแบบเป็น **Layered Architecture** แยกส่วนการทำงานชัดเจนดังนี้:

1.  **Presentation Layer (UI)**: ส่วนติดต่อผู้ใช้ (`ui.py`, `main.py`) หน้าที่คือรับคำสั่งและแสดงผล
2.  **Logic Layer (Bot)**: ส่วนทำงานหลัก (`bot.py`) ควบคุม Browser และการกรอกข้อมูล
3.  **Brain Layer (Intelligence)**: สมองของ AI (`brain.py`, `learning_core.py`) ตัดสินใจเลือกคำตอบ
4.  **Data Layer (Persistence)**: จัดการข้อมูล (`data.py`, `personas.json`, `config.json`)

---

## 📂 2. อธิบายเจาะลึกรายไฟล์ (File Breakdown)

### 📌 1. `main.py` (Entry Point)
**หน้าที่:** เป็นจุดเริ่มต้นของโปรแกรม
- **Code:** สร้าง instance ของ `App` จาก `ui.py` และเรียก `mainloop()` เพื่อเริ่มหน้าจอโปรแกรม
- **ความสำคัญ:** เรียบง่ายที่สุด แต่ถ้าไม่มีไฟล์นี้ โปรแกรมก็เริ่มไม่ได้

### 📌 2. `ui.py` (User Interface)
**หน้าที่:** สร้างหน้าต่างโปรแกรม (GUI) ด้วย `customtkinter`
- **Class `App`**:
    - **`start_engine()`**: ฟังก์ชันสำคัญที่สุด รับค่าจากผู้ใช้ (URL, Loop) บันทึก Config และสั่งเริ่ม Thread ของบอท (`run_bot_thread`)
    - **Threading**: สังเกตการใช้ `threading.Thread` เพื่อรันบอทแยกจากหน้าจอหลัก ทำให้โปรแกรมไม่ค้างขณะบอททำงาน
    - **Pause/Resume**: (ล่าสุดถูกถอดออกเพื่อความเสถียร แต่เคยอยู่ในนี้)
- **Class `PersonaCard`**: แสดงการ์ดข้อมูลของบอทแต่ละตัว (ชื่อ, อาชีพ, เลเวล) มีการใช้สีแยกตาม Level
- **Class `GroupFilterDialog`**: หน้าต่าง Popup สำหรับเลือก Filter กลุ่มอาชีพ

### 📌 3. `bot.py` (The Worker)
**หน้าที่:** ควบคุม Google Chrome ผ่าน Selenium
- **Class `FormBot`**:
    - **`run()`**: ลูปการทำงานหลัก
        1. สุ่ม Persona จาก `DATA_MANAGER` (ตาม Filter ที่เลือก)
        2. เข้าเว็บ Google Form
        3. สแกนหาคำถาม (`find_elements`)
        4. ส่งคำถามให้ `brain.decide_answer` ตัดสินใจ
        5. คลิกคำตอบและกด Submit
    - **Human Simulation**: ฟังก์ชัน `_human_delay`, `_human_scroll`, `_human_mouse` ทำให้การกระทำเหมือนคนจริง ป้องกันการถูกจับได้

### 📌 4. `brain.py` (The Decision Maker)
**หน้าที่:** ตัดสินใจเลือกคำตอบ (หัวใจสำคัญของ AI)
- **Functions สำคัญ**:
    - **`decide_answer(question, options, persona)`**: ฟังก์ชันพระเอก
        1. **Context Detection**: ดูว่าคำถามเกี่ยวกับอะไร (งาน, ไลฟ์สไตล์, เงิน)
        2. **Scoring**: ให้คะแนนแต่ละตัวเลือก
            - +3 คะแนน ถ้าตรงกับ **Interests** (ความสนใจ)
            - +2 คะแนน ถ้าตรงกับ **Traits** (นิสัย)
            - +1 คะแนน ตาม **Role** (ทางการ/ไม่ทางการ)
        3. **Boosting**: ถ้าคำตอบตรงกับ **Values** ของ Persona จะเพิ่มคะแนนพิเศษ (Scale Logic)
        4. **Selection**: เลือกตัวเลือกที่มีคะแนนสูงสุด (แบบสุ่มถ่วงน้ำหนัก เพื่อความหลากหลาย)
    - **`decide_text_input()`**: ตัดสินใจเวลาเจอช่องเติมคำ ใช้ `Faker` สร้างชื่อ/เบอร์โทร หรือใช้ `Gemini API` (ถ้ามี Key) ตอบคำถามปลายเปิด

### 📌 5. `learning_core.py` (Machine Learning)
**หน้าที่:** ระบบเรียนรู้แบบ Unsupervised (ไม่ต้องสอนก็ฉลาดเองได้)
- **Class `SemanticLearner`**:
    - ใช้ **TF-IDF Vectorizer** แปลงข้อความเป็นตัวเลข
    - ใช้ **K-Means Clustering** จัดกลุ่มคำตอบที่คล้ายกัน
    - **ประโยชน์**: ทำให้บอท "จำ" แพทเทิร์นของคำตอบได้ เมื่อเจอคำตอบแนวเดิมๆ จะมีความมั่นใจมากขึ้น (เป็นพื้นฐานสำหรับฟีเจอร์ Genius ในอนาคต)

### 📌 6. `data.py` (Data Manager)
**หน้าที่:** จัดการข้อมูลเข้า-ออก
- **Class `DataManager`**:
    - โหลด/บันทึก `config.json` (จำค่า URL ล่าสุด)
    - โหลด/เพิ่ม `personas.json` (จัดการรายชื่อ Persona)
    - **Logic ใหม่**: `get_personas_by_groups(groups)` ทำหน้าที่กรอง Persona ตามกลุ่มอาชีพที่เลือกหน้า UI

---

## ⚙️ 3. กระบวนการทำงานแบบ End-to-End (Flow)

เพื่อให้เห็นภาพชัดเจน นี่คือสิ่งที่เกิดขึ้นเมื่อคุณกดปุ่ม "START ENGINE":

1.  **User Interface**:
    - `ui.py` ดึงค่า URL และจำนวน Loop
    - `data.py` บันทึกค่าลง config
    - `ui.py` ปล่อย Thread แยกออกไปตามจำนวน Agent ที่เลือก (1-4 ตัว)

2.  **Bot Initialization**:
    - `bot.py` เปิด Chrome Browser
    - `bot.py` ขอ Persona 1 คนจาก `data.py` (โดยเช็ค Filter Group ก่อน)

3.  **On The Page (หน้าเว็บ)**:
    - บอทสแกนเจอคำถาม "คุณชอบทานอะไร?" ตัวเลือก ["กะเพรา", "สลัด", "พิซซ่า"]
    - บอทส่งข้อมูลนี้ไปที่ `brain.py` พร้อมข้อมูล Persona (สมมติเป็น "นางสาว A สายสุขภาพ")

4.  **Brain Processing**:
    - `brain.py` เห็นคำว่า "ทาน" -> Context = Food
    - `brain.py` เช็ค Persona -> Interest = "Health", "Yoga"
    - `brain.py` ให้คะแนน:
        - "สลัด" (+3 คะแนน เพราะตรงกับ Health)
        - "พิซซ่า" (0 คะแนน)
        - "กะเพรา" (0 คะแนน)
    - ส่งคำตอบกลับไปว่า "เลือก สลัด"

5.  **Action**:
    - `bot.py` ขยับเมาส์ไปคลิก "สลัด" (หน่วงเวลาเหมือนคนลังเลนิดหน่อย)
    - กด Submit -> วนรอบต่อไป

---

## 💡 สรุปสิ่งที่ได้เรียนรู้จากโปรเจกต์นี้
- **OOP (Object Oriented Programming)**: การแยก Class (Bot, App, Brain) ทำให้โค้ดเป็นระเบียบ แก้ไขง่าย
- **Threading**: การทำงานหลายอย่างพร้อมกัน (UI ไม่ค้างขณะบอทรัน)
- **Web Automation**: การใช้ Selenium ควบคุม Browser
- **Basic AI Logic**: การใช้ Rule-based Scoring (ให้คะแนนตามกฏ) ผสมกับ Basic Machine Learning (Clustering)

หวังว่าเอกสารนี้จะช่วยให้คุณเข้าใจการทำงานของระบบทั้งหมดได้อย่างทะลุปรุโปร่งครับ! 🚀
