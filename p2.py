from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr, field_validator, Field, SecretStr
from typing import List

class Product(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: float
    category: str

class User(BaseModel):
    id: int = Field(gt=0)
    lastname: str
    name: str
    email: EmailStr
    password : SecretStr = Field(min_length=8)
    @field_validator("password")
    def validacion_psw(cls, password: SecretStr) -> str:
        # Obtener el valor de la contraseña
        password_value = password.get_secret_value()
        # Verificar si hay al menos una letra mayúscula
        if not any(caracter.isupper() for caracter in password_value):
            raise ValueError("¡Debe contener una mayúscula como mínimo!")
        return password_value
    country: str
    city: str
    address: str
    phone: int
    rol: str = Field(title= 'Rol del user', description= 'Debe Ingresar "Cliente" o "Administrador"', pattern= 'Cliente' or 'Administrador')

class Category(BaseModel):
    id: int = Field(gt=0)
    description: str

class Sale(BaseModel):
    id: int = Field(gt= 0)
    id_user: int = Field(gt= 0)
    id_product: int = Field(gt= 0)
    quantity: int
    date: str
    dispatched: str | None = 'No despachado'

app = FastAPI()

#: List[Product] = []
products = [
    {'id' : 1, 'name' : 'smart-tv', 'price' : 700, 'category' : 'home appliances'},
    {'id' : 2, 'name' : 'home-theater', 'price' : 600, 'category' : 'home appliances'},
    {'id' : 3, 'name' : 'playstation 5', 'price' : 1500, 'category' : 'home appliances'},    
    {'id' : 4, 'name' : 'hammer', 'price' : 8, 'category' : 'tools'},
    {'id' : 5, 'name' : 'electric drill', 'price' : 120, 'category' : 'tools'}
]

sales = []
categories = []
users = []

#Mensaje Bienvenida
@app.get('/', tags=['home'])
def home():
    return PlainTextResponse(content='Bienvenidos A Mi Primera API')

#Mostrar productos
@app.get('/products', tags=['products'])
def get_products():
    return products

#Parámetros por Path
@app.get('/products/{id}', tags=['products'])
def get_product_by_id(id: int):
    for product in products:
        if product['id'] == id:
            return product
    return []

@app.post('/products', tags=['products'])
def create_product(product: Product):
    if product.category not in categories:
        raise ValueError('Categoría inválida.')
    products.append({
        'id' : product.id,
        'name' : product.name,
        'price' : product.price,
        'category' : product.category
    })
    return products

@app.put('/products/{id}', tags=['products'])
def update_product(id: int, product: Product):
    if product.category not in categories:
        raise ValueError('Categoría inválida.')
    for product in products:
        if product['id'] == id:
            product['name'] = product.name
            product['price'] = product.price
            product['category'] = product.category
            return products
        
@app.delete('/products/{id}', tags=['products'])
def delete_product(id: int):
    for product in products:
        if product['id'] == id:
            products.remove(product)
            return products

@app.get('/sales', tags=['sales'])
def get_sales():
    return sales

@app.post('/sales', tags=['sales'])
def reg_sale(sale: Sale):
    sale = Sale.model_dump()
    if sale.id_user not in sales:
        raise ValueError('Id de usuario no encontrado.')
    if sale.id_product not in sales:
        raise ValueError('Id de producto no encontrado.')
    for product in products:
        if product['id'] == sale['id_product']:
            for user in users:
                if user['id'] == sale['id_user']:
                    sales.append(sale)
    return sales

@app.put('/sales/{id}', tags=['sales'])
def reg_sale_dispatched(id: int, dispatched: str):
    if not id in sales:
            raise ValueError('Id de venta no encontrado.')
    if dispatched == 'Despachado' or 'No despachado':
        for sale in sales:
            if sale['id'] == id:
                sale['dispatched'] = dispatched
                return sales
    else:
        return dispatched
    ValueError('Ingresar Despachado o No despachado.')
 
@app.get('/categories', tags=['categories'])
def get_categories():
    return categories   
    
@app.post('/categories', tags=['categories'])
def reg_category(category: Category):
    categories.append(category.model_dump())
    
@app.put('/categories', tags=['categories'])
def modify_category(id: int, description: str):
    for cat in categories:
        if cat['id'] == id:
            cat['description'] = description
            return categories
        
@app.get('/users', tags=['users'])
def get_users():
    return users

@app.post('/users', tags=['users'])
def reg_user(user: User):
    users.append(user.model_dump())
    
@app.put('/users', tags=['users'])
def modify_user(id: int, user: User):
    if user not in users:
        raise ValueError('Usuario no encontrado.')
    for user in users:
        if user['id'] == id:
            user['name'] = user.name
            user['lastname'] = user.lastname
            user['email'] = user.email
            user['country'] = user.country
            user['city'] = user.city
            user['address'] = user.address
            user['phone'] = user.phone
            if not any(caracter.isupper() for caracter in user.password):
                raise ValueError("¡Debe contener una mayúscula como mínimo!")
        return user.password
    return users

