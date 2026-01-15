# 🤖 AI Recruiter: ระบบคัดกรองเรซูเม่และผู้สมัครอัจฉริยะ

## 📌 ภาพรวมโปรเจกต์ (Project Overview)
**AI Recruiter** คือระบบช่วยตัดสินใจสำหรับฝ่ายทรัพยากรบุคคล (HR) ที่นำเทคโนโลยี **Generative AI** มาใช้ในการวิเคราะห์ คัดกรอง และเปรียบเทียบผู้สมัครงานโดยอัตโนมัติ ช่วยลดเวลาในการอ่านเรซูเม่นับร้อยฉบับ และเพิ่มความแม่นยำในการค้นหาคนที่ "ใช่" ที่สุดสำหรับองค์กร

## 🚀 ฟีเจอร์หลัก (Key Features)

### 1. 🧠 AI & Rule-Based Engines (Dual High-Performance Engines)
ระบบมาพร้อมกับ 2 กลไกการทำงานให้เลือกตามความเหมาะสม:
- **Gemini LLM (Advanced)**: ใช้ปัญญาประดิษฐ์ขั้นสูง (Google Gemini Pro) ในการ "อ่าน" และ "ทำความเข้าใจ" บริบทของประสบการณ์ทำงาน ไม่ใช่แค่หาคำเหมือน แต่เข้าใจความหมาย (Semantic Understanding) เพื่อวิเคราะห์จุดแข็ง จุดอ่อน และประเมินคะแนนความเหมาะสม
- **Rule-Based (Speed)**: โหมดวิเคราะห์รวดเร็วโดยไม่ต้องใช้อินเทอร์เน็ต ใช้การจับคู่ Keyword และ Algorithms ทางสถิติ เหมาะสำหรับการคัดกรองเบื้องต้นปริมาณมาก

### 2. ⚖️ Blind Hiring Mode (โหมดคัดเลือกโปร่งใส)
ส่งเสริมความเท่าเทียมโดยการ **ปิดบังชื่อและข้อมูลส่วนตัว** ของผู้สมัครในขณะพิจารณา ช่วยให้ HR โฟกัสที่ "ทักษะ" และ "ประสบการณ์" ล้วนๆ ลดอคติ (Unconscious Bias) ในการจ้างงาน

### 3. ⚔️ Candidate Battle Arena (ระบบเปรียบเทียบผู้สมัคร)
หน้าจอ Dashboard ที่ให้คุณนำผู้สมัคร 2 คนมา "ประชัน" กันแบบ Head-to-Head โดยแสดงกราฟเปรียบเทียบคะแนนและสกิลให้เห็นชัดเจนว่าใครเหนือกว่าในด้านไหน

### 4. 🎯 Smart Analysis & Insights
- **Match Score**: คำนวณคะแนนความเข้ากันได้เป็น %
- **Skill Gap Analysis**: ระบุทักษะที่ขาดหายไปเทียบกับ Job Description
- **Interview Generator**: AI ช่วยสร้าง "คำถามสัมภาษณ์" เฉพาะบุคคลตามจุดอ่อนหรือจุดที่น่าสนใจในเรซูเม่

---

## 🤖 เจาะลึกส่วนสำคัญ: การนำ AI มาใช้ (AI Implementation)

หัวใจสำคัญของโปรเจกต์นี้คือการใช้ **Large Language Model (LLM)** ผ่าน Google Gemini API เข้ามาทำหน้าที่เสมือน Recruiter ผู้เชี่ยวชาญ

### กระบวนการทำงานของ AI (AI Workflow):
1.  **Contextual Parsing**: AI รับข้อมูล Job Description (JD) และเนื้อหาใน Resume ทั้งหมด
2.  **Semantic Mapping**: AI จะไม่ทำแค่ Keyword Matching (เช่น "Python" ตรงกับ "Python") แต่จะเข้าใจบริบท เช่น หาก JD ต้องการ "Manage Cloud Infrastructure" และผู้สมัครเขียนว่า "Experience with AWS & Terraform" -> **AI จะเข้าใจว่าตรงกันและให้คะแนน** แม้จะใช้คำไม่เหมือนกัน
3.  **Reasoning & Scoring**: AI ประมวลผลและให้เหตุผลว่าทำไมผู้สมัครคนนี้ถึงได้คะแนนเท่านี้ พร้อมทำนายระดับ Seniority (Junior, Senior, Manager) จากภาษาที่ใช้
4.  **Generative Output**: สร้างคำสรุป (Candidate Summary) และคำถามสัมภาษณ์ (Tailored Questions) ให้อัตโนมัติ

> **ความแตกต่าง:** ระบบเดิมๆ อาจคัดคนเก่งทิ้งเพียงเพราะเรซูเม่เขียนคำไม่ตรง keyword แต่ **AI Recruiter** เข้าใจศักยภาพที่แท้จริงของผู้สมัคร

---

## 🛠️ เทคโนโลยีที่ใช้ (Tech Stack)
- **Core**: Python 3.9+
- **Frontend**: Streamlit (พร้อม Custom CSS Design System แนวนีออน/Glassmorphism)
- **AI Model**: Google Gemini Pro (via `google.generativeai`)
- **Data Visualization**: Plotly Express, Pandas
- **Database**: JSON/Local Storage (Lightweight)

## 💼 ประโยชน์ทางธุรกิจ (Business Impact)
- **ลดเวลา Screening ลง 80%**: จากการอ่านทีละใบ เป็นการดู Dashboard สรุปผล
- **เพิ่มคุณภาพการจ้างงาน**: ได้คนที่ตรงกับงานจริงๆ ด้วยการวิเคราะห์เชิงลึก
- **ลดอคติ**: สร้างมาตรฐานการจ้างงานที่เป็นธรรมและตรวจสอบได้
- **User Experience**: หน้าตาโปรแกรมทันสมัย ใช้งานง่าย ไม่ซับซ้อน (No-Code Friendly)
