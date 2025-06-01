
# File: server/mira/models/user_input.py
from pydantic import BaseModel

class AskRequest(BaseModel):
    session_id: str
    user_input: str

class ResetSessionRequest(BaseModel):
    session_id: str
