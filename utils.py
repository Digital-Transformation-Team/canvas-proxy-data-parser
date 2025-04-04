import pandas as pd

from constants import MATCHED_DATA_FILE, NO_GF_DATA_FILE
from models import Student


def replace_kazakh_chars(text: str) -> str:
    replacements = {
        "Ә": "А",
        "ә": "а",
        "Ғ": "Г",
        "ғ": "г",
        "Қ": "К",
        "қ": "к",
        "Ң": "Н",
        "ң": "н",
        "Ө": "О",
        "ө": "о",
        "Ұ": "У",
        "ұ": "у",
        "Ү": "У",
        "ү": "у",
        "Һ": "Х",
        "һ": "х",
        "І": "И",
        "і": "и",
    }

    return "".join(replacements.get(char, char) for char in text)


def save_unmatched_to_excel(no_gf_images, no_gf_students):
    """Сохраняет ненайденные изображения и студентов в один Excel-файл на разные листы"""

    df_images = pd.DataFrame({"Image Name": no_gf_images})
    df_students = pd.DataFrame({"Student Name": list(no_gf_students)})

    with pd.ExcelWriter(NO_GF_DATA_FILE, engine="xlsxwriter") as writer:
        df_images.to_excel(writer, sheet_name="no gf images", index=False)
        df_students.to_excel(writer, sheet_name="no gf students", index=False)


def save_matched_to_excel(students: list[Student]):
    """Сохраняет ненайденные изображения и студентов в один Excel-файл на разные листы"""

    df_students = pd.DataFrame(
        {
            "Origin Name": [student.origin_name for student in students],
            "Image ID": [student.image_id for student in students],
            "Canvas Name": [student.canvas_name for student in students],
            "Canvas Login": [student.canvas_login for student in students],
            "Canvas ID": [student.canvas_id for student in students],
        }
    )

    with pd.ExcelWriter(MATCHED_DATA_FILE, engine="xlsxwriter") as writer:
        df_students.to_excel(writer, sheet_name="Student data", index=False)
