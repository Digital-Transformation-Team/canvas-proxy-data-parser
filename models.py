from dataclasses import dataclass
from typing import Optional


@dataclass
class Image:
    SEP = ":::"
    name: str
    origin_name: str
    id: str

    def to_str(self):
        return f"{self.name}{self.SEP}{self.origin_name}{self.SEP}{self.id}"

    @classmethod
    def from_str(cls, item: str):
        name, origin_name, id = item.split(sep=cls.SEP)
        return cls(name=name, origin_name=origin_name, id=id)


@dataclass
class Student:
    name: str
    origin_name: str
    canvas_name: str
    canvas_login: str
    canvas_id: int
    image_id: Optional[str] = None

    def __repr__(self):
        return f"Student {self.canvas_id}: {self.name}"

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)
