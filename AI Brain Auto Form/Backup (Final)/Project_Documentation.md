# AI Brain Project Documentation
# เอกสารสรุปโครงการ AI Brain (AI Form Auto-Filler Pro)

---

## 1. Executive Summary (บทสรุปผู้บริหาร)
**English:**
The **AI Brain** project is a sophisticated automation tool designed to simulate human behavior in completing online forms (specifically Google Forms). Unlike standard bots that perform repetitive, identical actions, AI Brain utilizes a "Persona-based" architecture combined with Unsupervised Learning AI to generate diverse, realistic, and context-aware responses. The project has evolved from a simple script into a production-grade desktop application capable of multi-threaded execution and standalone deployment.

**Thai:**
โครงการ **AI Brain** คือเครื่องมืออัตโนมัติขั้นสูงที่ออกแบบมาเพื่อจำลองพฤติกรรมมนุษย์ในการกรอกแบบฟอร์มออนไลน์ (โดยเฉพาะ Google Forms) ซึ่งต่างจากการใช้บอททั่วไปที่มักจะทำงานซ้ำๆ ด้วยข้อมูลเดิม AI Brain ใช้สถาปัตยกรรมแบบ "Persona-based" (อิงบุคลิกภาพ) ผสานกับ AI แบบ Unsupervised Learning เพื่อสร้างคำตอบที่หลากหลาย สมจริง และเข้ากับบริบทของคำถาม โครงการนี้ได้พัฒนาจากสคริปต์ธรรมดาจนกลายเป็นแอปพลิเคชันเดสก์ท็อปที่รองรับการทำงานแบบหลายเธรด (Multi-thread) และสามารถนำไปใช้งานจริงได้ทันที

---

## 2. Project Objectives (วัตถุประสงค์)
**English:**
1.  **Simulation & Testing:** To stress-test forms and survey logic by generating thousands of unique entries.
2.  **Dataset Generation:** To create synthetic datasets representing diverse user demographics (Age, Gender, Interests).
3.  **Human Invulnerability:** To bypass simple bot detection mechanisms by mimicing human interaction speed, typing patterns, and hesitation.
4.  **Scalability:** To allow deployment on any Windows machine without requiring a Python environment (Standalone EXE).

**Thai:**
1.  **การจำลองและทดสอบระบบ:** เพื่อทดสอบความทนทาน (Stress-test) และตรรกะของแบบฟอร์มด้วยการสร้างข้อมูลนับพันรายการที่ไม่ซ้ำกัน
2.  **การสร้างชุดข้อมูลสังเคราะห์:** เพื่อสร้าง Dataset ที่เป็นตัวแทนของกลุ่มประชากรที่หลากหลาย (อายุ, เพศ, ความสนใจ)
3.  **ความแนบเนียนเหมือนมนุษย์:** เพื่อหลบเลี่ยงการตรวจจับบอทแบบพื้นฐาน โดยการเลียนแบบความเร็วในการพิมพ์, จังหวะการหยุดคิด, และการเลื่อนหน้าจอของมนุษย์
4.  **ความสามารถในการขยายผล:** เพื่อให้สามารถนำไปรันบนคอมพิวเตอร์ Windows เครื่องใดก็ได้โดยไม่ต้องติดตั้ง Python (Standalone EXE)

---

## 3. Technology Stack (เทคโนโลยีที่ใช้)
**English:**
*   **Core Logic:** Python 3.13
*   **User Interface (UI):** CustomTkinter (Modern, Dark-mode aware GUI)
*   **Automation Driver:** Selenium WebDriver (Chrome)
*   **AI & Logic:**
    *   *Scikit-learn:* K-Means Clustering for Unsupervised Learning (Context grouping).
    *   *Faker:* For generating realistic PII (Name, Email, Address) based on Thai locale.
    *   *Heuristic Engine:* Weighted probability logic for decision making based on Persona Traits.
*   **Packaging:** PyInstaller (Onefile EXE generation) & Git for version control.

**Thai:**
*   **ภาษาหลัก:** Python 3.13
*   **ส่วนติดต่อผู้ใช้ (UI):** CustomTkinter (GUI ทันสมัย รองรับ Dark Mode)
*   **ระบบควบคุมเบราว์เซอร์:** Selenium WebDriver (Chrome)
*   **ระบบ AI และตรรกะ:**
    *   *Scikit-learn:* ใช้ K-Means Clustering สำหรับการเรียนรู้แบบไม่มีผู้สอน (จัดกลุ่มบริบทคำตอบ)
    *   *Faker:* สำหรับสร้างข้อมูลระบุตัวตน (PII) เช่น ชื่อ, อีเมล, ที่อยู่ ที่สมจริงเป็นภาษาไทย
    *   *Heuristic Engine:* ระบบตัดสินใจแบบถ่วงน้ำหนักตามคุณลักษณะของ Persona
*   **การแพ็คเกจ:** PyInstaller (สร้างไฟล์ EXE ไฟล์เดียว) และ Git สำหรับจัดการเวอร์ชัน

---

## 4. Key Features (ฟีเจอร์หลัก)
**English:**
*   **🧠 Unsupervised Learning Core:** The bot reads form options and "learns" to cluster related concepts, improving its understanding of new forms over time.
*   **🎭 Dynamic Persona Engine:** Users can create Agents with specific roles (e.g., "Tech Lover", "Conservative Elder") which directly influence answer selection.
*   **⚡ Multi-Threaded Execution:** Capable of running multiple agents simultaneously in parallel browser windows.
*   **🛑 Human-Like Stealth:** Implements random delays, smooth scrolling, and "typing" simulation to behave like a real user.
*   **📦 Portable Deployment:** Compiles into a single `.exe` file with internal dependencies and configuration, ready for distribution.

**Thai:**
*   **🧠 สมองกลเรียนรู้ด้วยตนเอง:** บอทสามารถอ่านตัวเลือกในฟอร์มและ "เรียนรู้" ที่จะจัดกลุ่มคำที่เกี่ยวข้องกัน ทำให้เข้าใจบริบทของฟอร์มใหม่ๆ ได้ดีขึ้น
*   **🎭 ระบบ Persona อัจฉริยะ:** ผู้ใช้สามารถสร้าง Agent ที่มีบทบาทเฉพาะ (เช่น "คนชอบไอที", "ผู้สูงวัยหัวอนุรักษ์") ซึ่งจะส่งผลโดยตรงต่อการเลือกคำตอบ
*   **⚡ การทำงานแบบขนาน (Multi-Threading):** รองรับการรัน Agent หลายตัวพร้อมกันในหน้าต่างเบราว์เซอร์แยกอิสระ
*   **🛑 ความแนบเนียน (Stealth):** มีระบบหน่วงเวลาแบบสุ่ม, การเลื่อนหน้าจอที่นุ่มนวล, และการพิมพ์ทีละตัวอักษรเพื่อเลียนแบบคนจริง
*   **📦 ติดตั้งง่ายพกพาสะดวก:** รวมโค้ดทั้งหมดเป็นไฟล์ `.exe` เดียว พร้อมใช้งานได้ทันทีโดยไม่ต้องลงโปรแกรมเสริม

---

## 5. Project Results (ผลลัพธ์ที่ได้)
**English:**
The project successfully delivered a **Production-Ready Application** named `AIBrain_Genius.exe`.
*   **Performance:** Capable of continuously filling forms without crashing (verified loop stability).
*   **Usability:** A user-friendly Dashboard allowing non-technical users to configure URLs, Loops, and Personas.
*   **Intelligence:** The bot demonstrates context awareness (e.g., a "Tech" persona prefers "Online Banking" over "Cash").
*   **Reliability:** Fixed critical issues regarding data persistence and file locking during the build process.

**Thai:**
โครงการประสบความสำเร็จในการส่งมอบ **แอปพลิเคชันพร้อมใช้งาน (Production-Ready)** ในชื่อ `AIBrain_Genius.exe`
*   **ประสิทธิภาพ:** สามารถกรอกฟอร์มต่อเนื่องได้โดยไม่ล่ม (ผ่านการทดสอบ Loop Stability)
*   **การใช้งาน:** มีหน้า Dashboard ที่ใช้งานง่าย ผู้ใช้ทั่วไปสามารถตั้งค่า URL, จำนวนรอบ, และเลือก Persona ได้เอง
*   **ความฉลาด:** บอทแสดงให้เห็นถึงความเข้าใจบริบท (เช่น Persona สายไอที จะเลือก "ธนาคารออนไลน์" มากกว่า "เงินสด")
*   **ความเสถียร:** แก้ไขปัญหาใหญ่เรื่องข้อมูลหาย (Data Persistence) และไฟล์ล็อคระหว่างการนำไปใช้งานจริงได้สมบูรณ์แบบ

---

## 6. Future Roadmap (แผนงานในอนาคต)
*   **Cloud Deployment:** Containerize the application (Docker) for running on Linux VPS / Cloud Run.
*   **LLM Integration:** Replace the text generation logic with API calls to Gemini/GPT-4 for fully creative text responses.
*   **Vision Capability:** Add OCR or Vision AI to bypass CAPTCHA or read image-based questions.

*(Document Created: 2026-01-12 | By: Antigravity AI Team)*
