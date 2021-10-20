from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    password: str

# Create Item 
class Item(BaseModel):
    id: int
    name: Optional[str] = None
    price: Optional[int] = None
    
