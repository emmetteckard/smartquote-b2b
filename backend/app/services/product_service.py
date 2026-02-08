from sqlalchemy.orm import Session
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_products(self, skip: int = 0, limit: int = 100):
        return self.db.query(Product).offset(skip).limit(limit).all()

    def get_product(self, product_id: int):
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_sku(self, sku: str):
        return self.db.query(Product).filter(Product.sku == sku).first()

    def create_product(self, product: ProductCreate):
        db_product = Product(**product.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update_product(self, product_id: int, product: ProductUpdate):
        db_product = self.get_product(product_id)
        if not db_product:
            return None
        
        update_data = product.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
            
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
