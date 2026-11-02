from typing import TYPE_CHECKING

from app.db import Base

if TYPE_CHECKING:
    from app.core import run


class User(Base):
    pass
