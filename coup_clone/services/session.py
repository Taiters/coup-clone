from uuid import uuid4

from flask import session


def get_current_session_id() -> str:
    if "session_id" not in session:
        session["session_id"] = str(uuid4())
    return session["session_id"]
