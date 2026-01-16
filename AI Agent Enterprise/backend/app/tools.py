import json
import os
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv

load_dotenv()

HR_PATH = os.getenv("HR_PATH", "data/hr.json")


def _load_hr_data() -> Dict[str, Any]:
    if not os.path.exists(HR_PATH):
        raise FileNotFoundError(f"HR data not found at {HR_PATH}")
    with open(HR_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_employee(employee_id: str) -> Optional[Dict[str, Any]]:
    data = _load_hr_data()
    for emp in data.get("employees", []):
        if emp.get("employee_id") == employee_id:
            return emp
    return None


def find_employee_by_name(name: str) -> Optional[Dict[str, Any]]:
    name_l = name.lower()
    data = _load_hr_data()
    for emp in data.get("employees", []):
        if emp.get("name", "").lower() == name_l:
            return emp
    return None


def list_by_department(department: str) -> List[Dict[str, Any]]:
    dept_l = department.lower()
    data = _load_hr_data()
    return [e for e in data.get("employees", []) if e.get("department", "").lower() == dept_l]


def list_by_manager(manager_id: str) -> List[Dict[str, Any]]:
    data = _load_hr_data()
    return [e for e in data.get("employees", []) if e.get("manager_id") == manager_id]


def list_by_location(location: str) -> List[Dict[str, Any]]:
    loc_l = location.lower()
    data = _load_hr_data()
    return [e for e in data.get("employees", []) if e.get("location", "").lower() == loc_l]


def list_by_employment_type(employment_type: str) -> List[Dict[str, Any]]:
    typ_l = employment_type.lower()
    data = _load_hr_data()
    return [
        e for e in data.get("employees", [])
        if e.get("employment_type", "").lower() == typ_l
    ]


def get_leave_balance(employee_id: str) -> Dict[str, Any]:
    emp = get_employee(employee_id)
    if not emp:
        return {
            "found": False,
            "message": f"Employee ID not found: {employee_id}",
        }
    return {
        "found": True,
        "employee_id": emp["employee_id"],
        "name": emp["name"],
        "department": emp["department"],
        "leave_balance_days": emp["leave_balance_days"],
        "leave_used_days": emp["leave_used_days"],
        "sick_days_remaining": emp["sick_days_remaining"],
    }
