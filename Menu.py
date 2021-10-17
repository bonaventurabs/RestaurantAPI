import json
from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel

# Open and read menu.json file
with open('menu.json', 'r') as read_file: 
    data = json.load(read_file)

app = FastAPI() 

# Create Item and UpdateItem class
class Item(BaseModel):
    id: int
    name: str
    price: int
class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None

# Read Base Path
@app.get('/')
async def root():
    return {"Restaurant": "Indonesian Food"}

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
@app.put('/menu/{item_id}', tags=['menu'])
async def update_menu(item_id: int, item: UpdateItem):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
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
@app.post('/menu/{item_id}', tags=['menu'])
async def add_menu(item_id: int, item: Item):
    if item_id != item.id:
        raise HTTPException(
            status_code=406, detail=f"Not acceptable"
        )

    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            raise HTTPException(
                status_code=405, detail=f"Method not allowed"
            )
    data['menu'].append({
        "id": item.id,
        "name": f"{item.name}",
        "price": item.price
    })
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