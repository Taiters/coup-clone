from attr import dataclass

from coup_clone.models import Session


@dataclass
class Request:
    sid: str
    session: Session
