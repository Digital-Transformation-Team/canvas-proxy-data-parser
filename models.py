import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class Image:
    SEP = ":::"
    WHITENOISE = "<<<<<<<"
    name: str
    origin_name: str
    id: str

    def to_str(self):
        return f"{self.name}{self.SEP}{self.origin_name}{self.SEP}{self.id}{self.SEP}{self.WHITENOISE}"

    @classmethod
    def from_str(cls, item: str):
        name, origin_name, id, _ = item.split(sep=cls.SEP)
        return cls(name=name, origin_name=origin_name, id=id)


@dataclass
class Student:
    name: str
    origin_name: str
    canvas_name: str
    canvas_login: str
    canvas_id: int
    image_id: Optional[str] = None
    image_vector: Optional[np.ndarray] = None

    def __repr__(self):
        return f"Student {self.canvas_id}: {self.name} {self.image_vector}"

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    @classmethod
    def from_excel_row(cls, row: dict):
        return cls(
            name=row["Origin Name"],
            origin_name=row["Origin Name"],
            canvas_name=row["Canvas Name"],
            canvas_login=row["Canvas Login"],
            canvas_id=row["Canvas ID"],
            image_id=row["Image ID"],
            image_vector=row["Image Vector"],
        )
