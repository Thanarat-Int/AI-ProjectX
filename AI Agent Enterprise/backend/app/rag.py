import json
import os
import re
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

from .tools import (
    get_leave_balance,
    find_employee_by_name,
    get_employee,
    list_by_department,
    list_by_manager,
    list_by_location,
    list_by_employment_type,
)

load_dotenv()

INDEX_PATH = os.getenv("INDEX_PATH", "storage/index.jsonl")


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _load_index() -> Tuple[List[str], List[str]]:
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            f"Index not found at {INDEX_PATH}. Run scripts/ingest.py first."
        )
    texts = []
    sources = []
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            texts.append(item["text"])
            sources.append(item["source"])
    if not texts:
        raise ValueError("Index is empty. Add documents and re-run ingest.")
    return texts, sources


def retrieve_context(question: str, top_k: int = 4) -> List[Dict[str, Any]]:
    texts, sources = _load_index()
    tokenized_corpus = [_tokenize(t) for t in texts]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(_tokenize(question))

    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    contexts = []
    for idx in ranked:
        contexts.append({"text": texts[idx], "source": sources[idx]})
    return contexts


def _format_retrieval_only(contexts: List[Dict[str, Any]]) -> str:
    lines = [
        "No-LLM mode: returning top retrieved passages.",
        "",
    ]
    for idx, ctx in enumerate(contexts, start=1):
        lines.append(f"[{idx}] source: {ctx['source']}")
        lines.append(ctx["text"])
        lines.append("")
    return "\n".join(lines).strip()


def _extract_employee_id(text: str) -> str:
    match = re.search(r"\bE\d{4}\b", text)
    return match.group(0) if match else ""


def _extract_department(text: str) -> str:
    departments = [
        "Finance", "Engineering", "Operations", "HR", "Risk",
        "Compliance", "Product", "Security", "Marketing",
        "Legal", "Data", "Customer Support",
        "การเงิน", "วิศวกรรม", "ปฏิบัติการ", "ทรัพยากรบุคคล",
        "ความเสี่ยง", "กำกับดูแล", "ผลิตภัณฑ์", "ความปลอดภัย",
        "การตลาด", "กฎหมาย", "ข้อมูล", "บริการลูกค้า",
    ]
    text_l = text.lower()
    for dept in departments:
        if dept.lower() in text_l:
            return dept
    return ""


def _extract_location(text: str) -> str:
    locations = ["Bangkok", "Chiang Mai", "กรุงเทพ", "เชียงใหม่"]
    text_l = text.lower()
    for loc in locations:
        if loc.lower() in text_l:
            return loc
    return ""


def _format_employee_list(employees: List[Dict[str, Any]]) -> str:
    if not employees:
        return "No matching employees found."
    lines = []
    for emp in employees:
        lines.append(f"{emp['employee_id']} - {emp['name']} ({emp['department']}, {emp['role']})")
    return "\n".join(lines)


def _answer_hr_question(question: str) -> Dict[str, Any]:
    question_l = question.lower()
    employee_id = _extract_employee_id(question)

    if (
        "leave" in question_l
        or "vacation" in question_l
        or "วันลา" in question
        or "ลาพักร้อน" in question
        or "ลา" in question
    ):
        if not employee_id:
            return {
                "answer": "กรุณาระบุรหัสพนักงาน (เช่น E1001) สำหรับข้อมูลวันลา",
                "sources": ["tool:hr:get_leave_balance"],
            }
        result = get_leave_balance(employee_id)
        if not result["found"]:
            return {"answer": result["message"], "sources": ["tool:hr:get_leave_balance"]}
        answer = (
            f"{result['name']} ({result['employee_id']}) "
            f"เหลือวันลา {result['leave_balance_days']} วัน, "
            f"ใช้ไป {result['leave_used_days']} วัน, "
            f"และเหลือวันลาป่วย {result['sick_days_remaining']} วัน"
        )
        return {"answer": answer, "sources": ["tool:hr:get_leave_balance"]}

    if ("role" in question_l or "ตำแหน่ง" in question) and employee_id:
        emp = get_employee(employee_id)
        if not emp:
            return {"answer": f"Employee ID not found: {employee_id}", "sources": ["tool:hr:get_employee"]}
        return {
            "answer": f"{emp['employee_id']} - {emp['name']} เป็น {emp['role']} แผนก {emp['department']}.",
            "sources": ["tool:hr:get_employee"],
        }

    if "department" in question_l or "แผนก" in question:
        if employee_id:
            emp = get_employee(employee_id)
            if not emp:
                return {"answer": f"Employee ID not found: {employee_id}", "sources": ["tool:hr:get_employee"]}
            return {
                "answer": f"{emp['employee_id']} - {emp['name']} อยู่แผนก {emp['department']}.",
                "sources": ["tool:hr:get_employee"],
            }
        dept = _extract_department(question)
        if dept and (
            "list" in question_l
            or "which" in question_l
            or "show" in question_l
            or "รายชื่อ" in question
            or "แสดง" in question
        ):
            employees = list_by_department(dept)
            return {"answer": _format_employee_list(employees), "sources": ["tool:hr:list_by_department"]}

    if "manager" in question_l or "report" in question_l or "หัวหน้า" in question:
        if employee_id and ("manager" in question_l or "หัวหน้า" in question):
            emp = get_employee(employee_id)
            if not emp:
                return {"answer": f"Employee ID not found: {employee_id}", "sources": ["tool:hr:get_employee"]}
            return {
                "answer": f"{emp['employee_id']} - {emp['name']} มีหัวหน้าเป็น {emp['manager_id']}.",
                "sources": ["tool:hr:get_employee"],
            }
        manager_id = _extract_employee_id(question)
        if manager_id:
            employees = list_by_manager(manager_id)
            return {"answer": _format_employee_list(employees), "sources": ["tool:hr:list_by_manager"]}

    if "location" in question_l or "located" in question_l or "อยู่ที่" in question:
        loc = _extract_location(question)
        if loc:
            employees = list_by_location(loc)
            return {"answer": _format_employee_list(employees), "sources": ["tool:hr:list_by_location"]}

    if "part-time" in question_l or "part time" in question_l or "พาร์ทไทม์" in question:
        employees = list_by_employment_type("Part-time")
        return {"answer": _format_employee_list(employees), "sources": ["tool:hr:list_by_employment_type"]}

    if "full-time" in question_l or "full time" in question_l or "ฟูลไทม์" in question:
        employees = list_by_employment_type("Full-time")
        return {"answer": _format_employee_list(employees), "sources": ["tool:hr:list_by_employment_type"]}

    if "find employee by name" in question_l or "by name" in question_l or "ค้นหาพนักงานชื่อ" in question:
        name = question.split(":")[-1].strip()
        emp = find_employee_by_name(name)
        if not emp:
            return {"answer": "ไม่พบพนักงานตามชื่อนี้", "sources": ["tool:hr:find_employee_by_name"]}
        return {
            "answer": f"{emp['employee_id']} - {emp['name']} ({emp['department']}, {emp['role']})",
            "sources": ["tool:hr:find_employee_by_name"],
        }

    return {}

def answer_question(
    question: str,
    llm_provider: str,
    llm_model: str,
    top_k: int = 4,
) -> Dict[str, Any]:
    hr_answer = _answer_hr_question(question)
    if hr_answer:
        return hr_answer

    contexts = retrieve_context(question, top_k=top_k)

    llm_provider = llm_provider.lower()
    if llm_provider != "none":
        raise ValueError(
            "LLM providers are disabled in free mode. "
            "Set ENABLE_LLM=true and add provider code/deps to enable."
        )

    answer = _format_retrieval_only(contexts)
    return {
        "answer": answer,
        "sources": [c["source"] for c in contexts],
    }


def answer_question_with_employee(
    question: str,
    employee_id: str,
    llm_provider: str,
    llm_model: str,
    top_k: int = 4,
) -> Dict[str, Any]:
    if employee_id and employee_id not in question:
        question = f"{question} {employee_id}"
    return answer_question(question, llm_provider, llm_model, top_k=top_k)
