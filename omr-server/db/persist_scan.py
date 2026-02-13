from pathlib import Path
import sqlite3
import json
from typing import Dict, Any

# omr.db is located at project root (one level above omr-server)
DB_PATH = Path(__file__).resolve().parent.parent.parent / "omr.db"

def _aggregate_review_flag(section: Dict[str, Any]) -> bool:
    """
    Returns True if ANY field in the section has review_required=True.
    """
    return any(
        field.get("review_required", False)
        for field in section.values()
        if isinstance(field, dict)
    )


def _aggregate_answers_review_flag(answers_json: Dict[str, Any]) -> bool:
    """
    Returns True if ANY question across all subjects has review_required=True.
    """
    for subject in answers_json.values():
        for q in subject.get("answers", {}).values():
            if q.get("review_required", False):
                return True
    return False


def persist_scan(
    file_path: Path,
    student_json: Dict[str, Any],
    prev_school_json: Dict[str, Any],
    curr_school_json: Dict[str, Any],
    answers_json: Dict[str, Any],
):
    """
    Persist full scan into database.

    Flow:
    1. Compute aggregated review flags
    2. Insert omr_scan
    3. Insert student
    4. Insert previous_school
    5. Insert current_school
    6. Insert student_answers (bulk style loop)
    All wrapped in a single transaction.
    """

    print( ">>>> ", DB_PATH )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        with conn:  # transaction boundary

            # -----------------------------
            # Aggregate review flags
            # -----------------------------
            student_review = _aggregate_review_flag(student_json)
            prev_review = _aggregate_review_flag(prev_school_json)
            curr_review = _aggregate_review_flag(curr_school_json)
            answers_review = _aggregate_answers_review_flag(answers_json)

            scan_review = (
                student_review
                or prev_review
                or curr_review
                or answers_review
            )

            # -----------------------------
            # Insert omr_scan (parent)
            # -----------------------------
            scan_cursor = conn.execute(
                """
                INSERT INTO omr_scan (
                    file_name,
                    file_path,
                    raw_json,
                    review_required
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    file_path.name,
                    f"bucket/{file_path.name}",
                    json.dumps({
                        "student": student_json,
                        "previous_school": prev_school_json,
                        "current_school": curr_school_json,
                        "answers": answers_json,
                    }),
                    int(scan_review),
                ),
            )

            scan_id = scan_cursor.lastrowid
            generated_scan_id = scan_id

            # -----------------------------
            # Insert student
            # -----------------------------
            conn.execute(
                """
                INSERT INTO student (
                    scan_id,
                    last_name,
                    first_name,
                    middle_initial,
                    birth_month,
                    birth_day,
                    birth_year,
                    gender,
                    lrn,
                    ssc,
                    four_ps,
                    special_classes,
                    raw_json,
                    review_required
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    student_json.get("last_name", {}).get("answer"),
                    student_json.get("first_name", {}).get("answer"),
                    student_json.get("middle_initial", {}).get("answer"),
                    student_json.get("birth_month", {}).get("answer"),
                    student_json.get("birth_day", {}).get("answer"),
                    student_json.get("birth_year", {}).get("answer"),
                    student_json.get("gender", {}).get("answer"),
                    student_json.get("lrn", {}).get("answer"),
                    student_json.get("ssc", {}).get("answer"),
                    student_json.get("four_ps", {}).get("answer"),
                    json.dumps(
                        student_json.get("special_classes", {}).get("answer")
                    ),
                    json.dumps(student_json),
                    int(student_review),
                ),
            )

            # -----------------------------
            # Insert previous school
            # -----------------------------
            conn.execute(
                """
                INSERT INTO previous_school (
                    scan_id,
                    school_id,
                    class_size,
                    school_year,
                    math_grade,
                    english_grade,
                    science_grade,
                    filipino_grade,
                    ap_grade,
                    raw_json,
                    review_required
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    prev_school_json.get("school_id", {}).get("answer"),
                    prev_school_json.get("class_size", {}).get("answer"),
                    prev_school_json.get("school_year", {}).get("answer"),
                    prev_school_json.get("final_grade", {}).get("Math", {}).get("answer"),
                    prev_school_json.get("final_grade", {}).get("English", {}).get("answer"),
                    prev_school_json.get("final_grade", {}).get("Science", {}).get("answer"),
                    prev_school_json.get("final_grade", {}).get("Filipino", {}).get("answer"),
                    prev_school_json.get("final_grade", {}).get("AP", {}).get("answer"),
                    json.dumps(prev_school_json),
                    int(prev_review),
                ),
            )

            # -----------------------------
            # Insert current school
            # -----------------------------
            conn.execute(
                """
                INSERT INTO current_school (
                    scan_id,
                    region,
                    division,
                    school_id,
                    school_type,
                    raw_json,
                    review_required
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    curr_school_json.get("region", {}).get("answer"),
                    curr_school_json.get("division", {}).get("answer"),
                    curr_school_json.get("school_id", {}).get("answer"),
                    curr_school_json.get("school_type", {}).get("answer"),
                    json.dumps(curr_school_json),
                    int(curr_review),
                ),
            )

            # -----------------------------
            # Insert answers (per question)
            # -----------------------------
            for subject_name, subject in answers_json.items():
                for question_number, q in subject.get("answers", {}).items():

                    conn.execute(
                        """
                        INSERT INTO student_answer (
                            scan_id,
                            subject,
                            question_number,
                            answer,
                            confidence,
                            raw_json,
                            review_required
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            scan_id,
                            subject_name,
                            int(question_number),
                            q.get("answer"),
                            q.get("confidence"),
                            json.dumps(q),
                            int(q.get("review_required", False)),
                        ),
                    )

        return generated_scan_id
    finally:
        conn.close()


def update_scan_status(
    scan_id: int,
    new_file_path: Path,
    status: str,
):
    """
    Update omr_scan after file has been moved.

    Args:
        scan_id: ID returned from persist_scan()
        new_file_path: Final filesystem location (success/ or error/)
        status: 'success' or 'error'
    """

    conn = sqlite3.connect(DB_PATH)

    try:
        with conn:
            conn.execute(
                """
                UPDATE omr_scan
                SET file_path = ?,
                    status = ?
                WHERE id = ?
                """,
                (
                    str(new_file_path),
                    status,
                    scan_id,
                ),
            )
    finally:
        conn.close()
