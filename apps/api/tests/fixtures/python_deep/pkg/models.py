from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class Point:
    x: int
    y: int


class UserModel(BaseModel):
    """Pydantic user."""

    id: int
    name: str
