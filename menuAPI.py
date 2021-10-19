import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, oauth2
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from schema import Token, User, Item, TokenData

SECRET_KEY = "7fb37f84964f9eabe3898d94b5a9a0fb3131ced462886a8ce43dab60ec02d58f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20

# Open and read menu.json file
with open('menu.json', 'r') as read_file: 
    data = json.load(read_file)

# Open and read user.json file
with open('user.json', 'r') as read_file: 
    users = json.load(read_file)

app = FastAPI() 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(user_db, username: str):
    for user in user_db:
        if user["username"] == username:
            return User(**user)

def authenticate_user(user_db, username: str, password: str):
    user = get_user(user_db, username)
    if not user:
        return False
    else:
        if user.password!=password:
            return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=20)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Read Base Path
@app.get('/')
async def root():
    return {"Restaurant": "Indonesian Food"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(**{"access_token": access_token, "token_type": "bearer"})

# Read All Item Menu
@app.get('/menu', tags=['menu']) 
async def read_all_menu(): 
    return data['menu']

# Read Spesific Item Menu
@app.get('/menu/{item_id}', tags=['menu']) 
async def read_menu(item_id: int): 
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item

    raise HTTPException(
        status_code=404, detail=f"Item not found"
    )

# Update Specific Item Menu
@app.put('/menu', tags=['menu'])
async def update_menu(item: Item):
    for menu_item in data['menu']:
        if menu_item['id'] == item.id:
            if item.name != None:
                menu_item['name'] = item.name
            if item.price != None:
                menu_item['price'] = item.price

            # Write JSON Object on JSON file
            json_object = json.dumps(data, indent='\t')
            with open('menu.json', 'w') as rewrite_file:
                rewrite_file.write(json_object)
            return menu_item

    raise HTTPException(
        status_code=404, detail=f"Item not found"
    )

# Add New Item Menu
@app.post('/menu', tags=['menu'])
async def add_menu(item: Item, current_user: User = Depends(get_current_user)):
    for menu_item in data['menu']:
        if menu_item['id'] == item.id:
            raise HTTPException(
                status_code=405, detail=f"Method not allowed"
            )
    data['menu'].append(item.dict())
    # Write JSON Object on JSON file
    json_object = json.dumps(data, indent='\t')
    with open('menu.json', 'w') as rewrite_file:
        rewrite_file.write(json_object)
    return data['menu'][-1]

#Delete Spesific Item Menu
@app.delete('/menu/{item_id}', tags=['menu'])
async def delete_menu(item_id: int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            # Write JSON Object on JSON file
            json_object = json.dumps(data, indent='\t')
            with open('menu.json', 'w') as rewrite_file:
                rewrite_file.write(json_object)
            return{"detail": "Item deleted successfully"}
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )