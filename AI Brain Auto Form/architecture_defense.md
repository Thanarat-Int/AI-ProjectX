# 🛡️ Technical Architecture & Defense Guide
**(คู่มือตอบคำถามเชิงเทคนิค: Architecture & Defense)**

This document outlines the technical core of the "AI Brain" project. Use this to address questions from Senior Developers or DevOps regarding Architecture, AI Logic, and Scalability.
(เอกสารนี้สรุปแก่นทางเทคนิคของโปรเจกต์ "AI Brain" เพื่อใช้ตอบคำถาม Senior Dev หรือ DevOps โดยเน้นอธิบาย "เหตุผล" และ "วิธีการ")

---

## 1. High-Level Architecture (ภาพรวมระบบ)

The system follows the **Separation of Concerns (SoC)** principle, ensuring distinct layers of responsibility:
(ระบบถูกออกแบบโดยใช้หลักการ **Separation of Concerns (SoC)** แยกส่วนรับผิดชอบชัดเจน:)

```mermaid
graph TD
    UI[UI Layer (ui.py)] -->|Spawns Threads| Bot[Automation Layer (bot.py)]
    Bot -->|Queries Decision| Brain[Cognitive Layer (brain.py)]
    Brain -->|Uses & Updates| Logic[Logic & Learning Logic]
    
    subgraph Logic & Learning Logic
    KW[Rule-Based (keyword_weights.py)]
    ML[Unsupervised Learning (learning_core.py)]
    end
    
    Bot -->|Reads/Writes| Data[Data Layer (data.py)]
    Data --> DB[(JSON Files)]
```

### Q: Why this architecture? (ทำไมถึงออกแบบแบบนี้?)
**EN:** We separated the UI, Logic (Brain), and Automation (Selenium) to ensure **maintainability**. Modifying the UI in `ui.py` does not break the bot's logic in `bot.py` or `brain.py`.
**TH:** เพื่อให้ดูแลรักษา (Maintain) ง่ายครับ การแยกส่วน UI, Logic, และ Automation ออกจากกันทำให้เราสามารถแก้ไขหน้าจอ `ui.py` ได้โดยไม่กระทบกับการทำงานของบอท หรือถ้าจะอัปเกรดสมอง ก็แก้แค่ `brain.py` ได้เลย

---

## 2. The "AI" Component (ส่วนที่เป็นปัญญาประดิษฐ์)

Senior devs often ask: **"Where is the actual AI?"** You can divide the answer into two parts:
(Senior มักจะเจาะลึกว่า "**มัน AI ตรงไหน?**" ให้ตอบแบ่งเป็น 2 ส่วน:)

### A. Rule-Based System (Legacy Core)
*   **Code:** `keyword_weights.py`
*   **Logic (EN):** Uses deterministic **Heuristics**. It matches keywords (e.g., "investment") to specific interest scores.
*   **Logic (TH):** ใช้กฎเกณฑ์ (Heuristics) ที่แน่นอน เช่น ถ้าเจอคำว่า "ลงทุน" ให้คะแนนหมวด Finance
*   **Why (EN):** Fast, deterministic, and works immediately without training.
*   **Why (TH):** เร็ว, ตรวจสอบผลลัพธ์ได้ง่าย, และทำงานได้ทันทีโดยไม่ต้องรอ Train

### B. Unsupervised Learning (The Genius Upgrade)
*   **Code:** `learning_core.py`
*   **Logic (EN):** Utilizes **TF-IDF** for text vectorization and **K-Means Clustering** to group similar terms automatically.
*   **Logic (TH):** ใช้ **TF-IDF** แปลงข้อความเป็นเวกเตอร์ และใช้ **K-Means Clustering** จัดกลุ่มคำศัพท์ที่คล้ายกันโดยอัตโนมัติ
*   **Function (EN):** The system "learns" new vocabulary from forms and self-organizes them into clusters without manual keyword entry.
*   **Function (TH):** ระบบจะเรียนรู้คำศัพท์ใหม่ๆ จากหน้าเว็บเอง และจัดหมวดหมู่ให้อัตโนมัติ (Self-Organizing) โดยคนไม่ต้องนั่งป้อน
*   **Why (EN):** Solves the scalability issue of rule-based systems. The bot adapts to new domains autonomously.
*   **Why (TH):** แก้ปัญหาที่ต้องมานั่งป้อน Keyword เองตลอดเวลา ทำให้ระบบรองรับเนื้อหาใหม่ๆ ได้เอง

---

## 3. Concurrency Model (การทำงานขนานกัน)

### Q: How do you handle multiple threads? Any Race Conditions?
(ระบบจัดการหลาย Thread ยังไง? มี Race Condition ไหม?)

**A:**
*   **Model:** We use Python's standard `threading` module. `ui.py` acts as the Main Thread, spawning Worker Threads for each bot instance.
    *   (ใช้ `threading` มาตรฐาน โดย `ui.py` เป็น Main Thread และแตก Worker Threads ไปทำงาน)
*   **UI Safety:** Since Tkinter is not thread-safe, we use **Queueing via `.after()`** to safely pass data from Worker Threads back to the UI (e.g., `update_persona_ui`), preventing crashes.
    *   (เนื่องจาก Tkinter ไม่ Thread-Safe เราจึงใช้ `.after()` เพื่อส่งข้อมูลกลับมาอัปเดตหน้าจออย่างปลอดภัย ป้องกันโปรแกรมค้าง)
*   **Data Safety:** JSON reads are handled via `DATA_MANAGER` (Singleton). Writes mostly happen on the UI thread, minimizing race conditions.
    *   (การอ่านไฟล์ผ่าน Singleton Pattern ส่วนใหญ่ปลอดภัย ส่วนการบันทึกข้อมูลจะทำที่หน้าจอหลักเป็นส่วนใหญ่)

---

## 4. DevOps & Scalability (มุมมอง DevOps)

### Q: How to deploy or scale this? (จะ Deploy หรือ Scale ยังไง?)

**A:**
*   **Dockerization:** The app can be containerized using a base image that supports Chrome/Chromium and Python.
    *   (สามารถจับใส่ Docker ได้ โดยใช้ Image ที่มี Chrome และ Python)
*   **Headless Mode:** `bot.py` supports `headless=True`, allowing it to run on servers without a GUI (e.g., Linux Cloud Servers).
    *   (รองรับโหมดไร้หน้าจอ สำหรับรันบน Server Linux ได้เลย)
*   **Limitation:** The main bottleneck is **RAM/CPU** per Chrome instance. Scaling to 100+ threads might require switching to lighter frameworks (Playwright) or a Distributed System.
    *   (ข้อจำกัดคือทรัพยากรเครื่องครับ เพราะ Chrome กิน Ram เยอะ ถ้าจะ Scale ใหญ่มากๆ อาจต้องเปลี่ยนไปใช้ Framework ที่เบากว่า หรือแยกเครื่องรันหลายๆ เครื่อง)

---

## 5. Technical Glossary (คำศัพท์เทคนิคไว้ตอบให้ดู Pro)

*   **Heuristics (ฮิวริสติก):** Simple rules or shortcuts to solve problems (used in keyword matching).
    *   (กฎง่ายๆ หรือทางลัดในการตัดสินใจ)
*   **Dependency Injection:** Passing dependencies (like `log_callback`) into objects instead of hardcoding them.
    *   (การส่งตัวช่วยต่างๆ เข้าไปในฟังก์ชัน เพื่อลดการยึดติดกันของโค้ด)
*   **Vectorization (TF-IDF):** Converting text into numbers so machines can calculate similarity.
    *   (การแปลงตัวหนังสือเป็นตัวเลข เพื่อคำนวณความเหมือน)
*   **Singleton Pattern:** ensuring a class (`DATA_MANAGER`) has only one instance.
    *   (รูปแบบการเขียนโค้ดให้มีตัวจัดการข้อมูลแค่ตัวเดียวทั้งระบบ)
