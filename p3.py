from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, SecretStr
from typing import List, Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Modelos Pydantic
class Product(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: float
    category: str
    image_url: Optional[str] = None  # URL de la imagen del producto

class User(BaseModel):
    id: int = Field(gt=0)
    lastname: str
    name: str
    email: EmailStr
    password: SecretStr = Field(min_length=8)
    country: str
    city: str
    address: str
    phone: int
    rol: str = Field(title='Rol del user', description='Debe ingresar "Cliente" o "Administrador"', pattern='Cliente|Administrador')
    profile_picture: Optional[str] = None  # URL de la imagen del usuario

class Category(BaseModel):
    id: int = Field(gt=0)
    description: str

class Sale(BaseModel):
    id: int = Field(gt=0)
    id_user: int = Field(gt=0)
    id_product: int = Field(gt=0)
    quantity: int
    date: str
    dispatched: Optional[str] = 'No despachado'

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str
    image_url: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    lastname: str
    name: str
    email: EmailStr
    country: str
    city: str
    address: str
    phone: int
    rol: str
    profile_picture: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    id_user: int
    id_product: int
    quantity: int
    date: str
    dispatched: Optional[str] = 'No despachado'

# Configuración de JWT
SECRET_KEY = "your-secret-key"  # Cambiar a una clave secreta fuerte
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Inicialización de FastAPI
app = FastAPI()

# Almacenamiento en memoria (debe reemplazarse por una base de datos en producción)
products = []
sales = []
categories = []
users = []

# Autenticación de usuario (simulación de login)
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Aquí debes verificar el usuario en la base de datos
    user = {"sub": form_data.username}  # Simulación de usuario
    access_token = create_access_token(data={"sub": user["sub"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Cargar y descargar fotos
@app.post("/upload-product-image/{product_id}")
async def upload_product_image(product_id: int, file: UploadFile = File(...)):
    file_location = f"images/products/{product_id}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return {"file_url": file_location}

@app.get("/download-product-image/{product_id}")
async def download_product_image(product_id: int):
    # Aquí se debería implementar la lógica para servir archivos
    return {"file_url": f"images/products/{product_id}_image.jpg"}

@app.post("/upload-user-profile-picture/{user_id}")
async def upload_user_profile_picture(user_id: int, file: UploadFile = File(...)):
    file_location = f"images/users/{user_id}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return {"file_url": file_location}

@app.get("/download-user-profile-picture/{user_id}")
async def download_user_profile_picture(user_id: int):
    # Aquí se debería implementar la lógica para servir archivos
    return {"file_url": f"images/users/{user_id}_profile.jpg"}

# Endpoints protegidos con JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)

@app.get("/products", response_model=List[ProductResponse])
async def get_products(current_user: dict = Depends(get_current_user)):
    return products

@app.get("/products/{id}", response_model=ProductResponse)
async def get_product_by_id(id: int, current_user: dict = Depends(get_current_user)):
    for product in products:
        if product["id"] == id:
            return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

@app.post("/products", response_model=List[ProductResponse])
async def create_product(product: Product, current_user: dict = Depends(get_current_user)):
    products.append(product.model_dump())
    return products

@app.put("/products/{id}", response_model=List[ProductResponse])
async def update_product(id: int, product: Product, current_user: dict = Depends(get_current_user)):
    for p in products:
        if p["id"] == id:
            p.update(product.model_dump())
            return products
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

@app.delete("/products/{id}", response_model=List[ProductResponse])
async def delete_product(id: int, current_user: dict = Depends(get_current_user)):
    global products
    products = [p for p in products if p["id"] != id]
    return products

@app.get("/sales", response_model=List[SaleResponse])
async def get_sales(current_user: dict = Depends(get_current_user)):
    return sales

@app.post("/sales", response_model=List[SaleResponse])
async def reg_sale(sale: Sale, current_user: dict = Depends(get_current_user)):
    sales.append(sale.model_dump())
    return sales

@app.put("/sales/{id}", response_model=List[SaleResponse])
async def reg_sale_dispatched(id: int, dispatched: str, current_user: dict = Depends(get_current_user)):
    for sale in sales:
        if sale["id"] == id:
            sale["dispatched"] = dispatched
            return sales
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

@app.get("/categories", response_model=List[Category])
async def get_categories(current_user: dict = Depends(get_current_user)):
    return categories

@app.post("/categories", response_model=List[Category])
async def reg_category(category: Category, current_user: dict = Depends(get_current_user)):
    categories.append(category.model_dump())
    return categories

@app.put("/categories/{id}", response_model=List[Category])
async def modify_category(id: int, description: str, current_user: dict = Depends(get_current_user)):
    for cat in categories:
        if cat["id"] == id:
            cat["description"] = description
            return categories
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

@app.get("/users", response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    return users

@app.post("/users", response_model=List[UserResponse])
async def reg_user(user: User, current_user: dict = Depends(get_current_user)):
    users.append(user.model_dump())
    return users

@app.put("/users/{id}", response_model=UserResponse)
async def modify_user(id: int, user: User, current_user: dict = Depends(get_current_user)):
    for u in users:
        if u["id"] == id:
            u.update(user.model_dump())
            return u
    raise HTTPException(status_code=status.HTTP)
