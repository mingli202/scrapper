from pydantic import BaseModel


class Section(BaseModel):
    program: str = ""
    count: int = 0
    section: str = ""
    course: str = ""
    code: str = ""
    lecture: dict[str, str] = {}
    lab: dict[str, str] = {}
    more: str = ""


class Rating(BaseModel):
    score: int = 0
    avg: float = 0
    nRating: int = 0
    takeAgain: float = 0
    difficulty: float = 0
    status: str = "foundn't"
