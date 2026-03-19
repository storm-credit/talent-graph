"""CSV/Excel import for employee data.

Parses minimal employee data (name, position, department, hire_date)
and generates Person objects with Dreyfus-prior skill initialization.
"""

from __future__ import annotations

import csv
import io
from datetime import date
from uuid import UUID

from pydantic import BaseModel


class EmployeeImportRow(BaseModel):
    """A single row from an imported CSV/Excel file."""

    name: str
    position: str
    department: str
    hire_date: date


class ImportResult(BaseModel):
    """Result of a CSV import operation."""

    imported: list[EmployeeImportRow] = []
    errors: list[str] = []
    warnings: list[str] = []

    @property
    def imported_count(self) -> int:
        return len(self.imported)


def parse_csv(content: str) -> ImportResult:
    """Parse CSV content into employee import rows.

    Expected columns (flexible header matching):
    - name / 이름 / 성명
    - position / 직급 / 직책 / 직위
    - department / 부서 / 소속
    - hire_date / 입사일 / 입사년월일

    Returns ImportResult with parsed rows + any errors.
    """
    result = ImportResult()
    reader = csv.DictReader(io.StringIO(content))

    if not reader.fieldnames:
        result.errors.append("CSV 파일에 헤더가 없습니다")
        return result

    # Flexible column name mapping
    col_map = _map_columns(reader.fieldnames)
    if not col_map:
        result.errors.append(
            f"필수 컬럼을 찾을 수 없습니다. 현재 헤더: {reader.fieldnames}. "
            "필요: name/이름, position/직급, department/부서, hire_date/입사일"
        )
        return result

    for i, row in enumerate(reader, start=2):  # start=2 (header is row 1)
        try:
            name = row.get(col_map["name"], "").strip()
            position = row.get(col_map["position"], "").strip()
            department = row.get(col_map["department"], "").strip()
            hire_date_str = row.get(col_map["hire_date"], "").strip()

            if not name:
                result.errors.append(f"행 {i}: 이름이 비어있습니다")
                continue

            if not position:
                result.warnings.append(f"행 {i}: {name}의 직급이 비어있어 '사원'으로 설정됩니다")
                position = "사원"

            if not department:
                result.warnings.append(f"행 {i}: {name}의 부서가 비어있어 '미배정'으로 설정됩니다")
                department = "미배정"

            hire_date = _parse_date(hire_date_str) if hire_date_str else date.today()

            result.imported.append(
                EmployeeImportRow(
                    name=name,
                    position=position,
                    department=department,
                    hire_date=hire_date,
                )
            )
        except Exception as e:
            result.errors.append(f"행 {i}: {e}")

    return result


def _map_columns(fieldnames: list[str]) -> dict[str, str] | None:
    """Map flexible column names to standard field names."""
    mapping: dict[str, str] = {}

    name_variants = {"name", "이름", "성명", "직원명"}
    position_variants = {"position", "직급", "직책", "직위", "title", "job_title"}
    department_variants = {"department", "부서", "소속", "dept"}
    hire_date_variants = {"hire_date", "입사일", "입사년월일", "입사_일자", "start_date"}

    for field in fieldnames:
        normed = field.strip().lower()
        if normed in name_variants:
            mapping["name"] = field
        elif normed in position_variants:
            mapping["position"] = field
        elif normed in department_variants:
            mapping["department"] = field
        elif normed in hire_date_variants:
            mapping["hire_date"] = field

    # All required fields found?
    if all(k in mapping for k in ("name", "position", "department", "hire_date")):
        return mapping

    # Try with just name (others optional)
    if "name" in mapping:
        mapping.setdefault("position", mapping.get("position", ""))
        mapping.setdefault("department", mapping.get("department", ""))
        mapping.setdefault("hire_date", mapping.get("hire_date", ""))
        return mapping

    return None


def _parse_date(s: str) -> date:
    """Parse various date formats."""
    # Try common formats
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"날짜 형식을 인식할 수 없습니다: {s}")
