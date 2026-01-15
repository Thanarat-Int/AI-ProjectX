from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AI Resume Screening Report', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

def generate_pdf_report(filename, data):
    """Generates a PDF report for the candidate."""
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Candidate Info
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"File: {filename}", 0, 1)
    pdf.cell(0, 10, f"Match Score: {data.get('match_score', 0)}%", 0, 1)
    pdf.ln(5)
    
    # 2. Summary
    pdf.chapter_title("Candidate Summary")
    pdf.chapter_body(data.get('candidate_summary', 'N/A'))
    
    # 3. Skills
    pdf.chapter_title("Key Skills Identified")
    skills = ", ".join(data.get('key_skills', []))
    pdf.chapter_body(skills)
    
    # 4. Gaps
    pdf.chapter_title("Missing Skills / Gaps")
    gaps = ", ".join(data.get('missing_skills', []))
    if not gaps:
        gaps = "None detected."
    pdf.chapter_body(gaps)
    
    # 5. Interview Questions
    pdf.chapter_title("Suggested Interview Questions")
    questions = data.get('interview_questions', [])
    q_text = ""
    for idx, q in enumerate(questions):
        q_text += f"{idx+1}. {q}\n"
    pdf.chapter_body(q_text)
    
    # Save
    report_path = f"data/report_{filename}.pdf"
    pdf.output(report_path)
    return report_path
