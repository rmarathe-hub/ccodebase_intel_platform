"""Service with nested classes, async, decorators, relative imports, and calls."""

from fastapi import APIRouter
from .sub.helpers import util
from .models import Point

router = APIRouter()


class Outer:
    """Outer container."""

    class Inner:
        def method(self) -> int:
            return util(1)

    def run(self) -> int:
        return self.Inner().method()


async def fetch() -> dict:
    """Async fetch."""
    return {"ok": True}


@router.get("/ping")
def ping() -> str:
    p = Point(1, 2)
    return str(p.x)


def entry() -> int:
    svc = Outer()
    return svc.run()
