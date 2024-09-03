from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr, SecretStr, Field, field_validator
from typing import List

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str

class ProductUpdate(BaseModel):
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
    rol: str = Field(title= 'Rol', description= 'Debe Ingresar "Cliente" o "Administrador"', pattern= 'Cliente' or 'Administrador')

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
    
products: List[Product] = []
    # {'id' : 1, 'name' : 'smart-tv', 'price' : 700, 'category' : 'home appliances'},
    # {'id' : 2, 'name' : 'home-theater', 'price' : 600, 'category' : 'home appliances'},
    # {'id' : 3, 'name' : 'playstation 5', 'price' : 1500, 'category' : 'home appliances'},    
    # {'id' : 4, 'name' : 'hammer', 'price' : 8, 'category' : 'tools'},
    # {'id' : 5, 'name' : 'electric drill', 'price' : 120, 'category' : 'tools'}

#Mensaje Bienvenida
@app.get('/', tags=['home'])
def home():
    return PlainTextResponse(content='Bienvenidos A Mi Primera API')

#Mostrar productos
@app.get('/products', tags=['products'])#, response_description= 'Todo bien campeón')
def get_products() -> List[Product]:
    return [product.model_dump() for product in products]

#Parámetros por Path
@app.get('/products/{id}', tags=['products'])
def get_product_by_id(id: int) -> Product:
    for product in products:
        if product.id == id: 
            return product.model_dump()
    
#Parámetros por Query
@app.get('/products/', tags=['products'])
def get_product_by_category(category: str) -> List[Product]:
    return [product.model_dump() for product in products if product.category == category]

#Parámetros por Body
#Indiqué que --> products es una lista de objetos(products) arriba 
#y ahora devuelvo una lista de esos objetos convertidos a diccionario par que no sea al reves
@app.post('/products', tags=['products'])
def create_products(product: Product) -> List[Product]:
    products.append(product)
    return [product.model_dump() for product in products]

#Parámetros por Path y Body
@app.put('/products/{id}', tags=['products'])
def update_products(id: int, product: ProductUpdate) -> List[Product]:
    for item in products:
        if item.id == id:
            item.name = product.name 
            item.price = product.price
            item.category = product.category
    return [product.model_dump() for product in products]

#Parámetros por Path
@app.delete('/products/{id}', tags=['products'])
def delete_product(id: int) -> List[Product]:
    for product in products:
        if product.id == id:
            products.remove(product)
    return [product.model_dump() for product in products]        
   #return [products.remove(product) for product in products if product.id == id]
