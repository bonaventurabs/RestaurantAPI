import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, oauth2

from schema import Token, User, Item, TokenData
from auth import UserHandler

# Open and read menu.json file
with open('menu.json', 'r') as read_file: 
    data = json.load(read_file)

app = FastAPI() 

user_handler = UserHandler()

# Read Base Path
@app.get('/')
async def root():
    return {"Restaurant": "Indonesian Food"}

# Request token 
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_handler.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=user_handler.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_handler.create_access_token(
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
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Item not found"
    )

# Update Specific Item Menu
@app.put('/menu', tags=['menu'])
async def update_menu(item: Item, current_user: User = Depends(user_handler.get_current_user)):
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
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item not found"
    )

# Add New Item Menu
@app.post('/menu', tags=['menu'])
async def add_menu(item: Item, current_user: User = Depends(user_handler.get_current_user)):
    for menu_item in data['menu']:
        if menu_item['id'] == item.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Conflict"
            )
    data['menu'].append(item.dict())
    # Write JSON Object on JSON file
    json_object = json.dumps(data, indent='\t')
    with open('menu.json', 'w') as rewrite_file:
        rewrite_file.write(json_object)
    return data['menu'][-1]

#Delete Spesific Item Menu
@app.delete('/menu/{item_id}', tags=['menu'])
async def delete_menu(item_id: int, current_user: User = Depends(user_handler.get_current_user)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            # Write JSON Object on JSON file
            json_object = json.dumps(data, indent='\t')
            with open('menu.json', 'w') as rewrite_file:
                rewrite_file.write(json_object)
            return{"detail": "Item deleted successfully"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'Item not found'
    )