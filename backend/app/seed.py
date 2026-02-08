"""Seed initial data for SmartQuote database."""
from datetime import date, datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    Role, User, Client, Product, BasePrice, ClientPrice, Inventory
)

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def seed_roles(db: Session):
    """Seed default roles."""
    print("Seeding roles...")
    roles_data = [
        {"name": "super_admin", "description": "Super Administrator with full system access"},
        {"name": "admin", "description": "Administrator with management access"},
        {"name": "sales", "description": "Sales representative"},
        {"name": "client", "description": "Client user with limited access"},
    ]
    
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    print("✓ Roles seeded")


def seed_users(db: Session):
    """Seed default users."""
    print("Seeding users...")
    
    # Get roles
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    sales_role = db.query(Role).filter(Role.name == "sales").first()
    
    users_data = [
        {
            "email": "admin@smartquote.com",
            "password": "admin123",  # Change in production!
            "full_name": "System Administrator",
            "role_id": super_admin_role.id,
        },
        {
            "email": "manager@smartquote.com",
            "password": "manager123",
            "full_name": "Sales Manager",
            "role_id": admin_role.id,
        },
        {
            "email": "sales@smartquote.com",
            "password": "sales123",
            "full_name": "Sales Representative",
            "role_id": sales_role.id,
        },
        {
            "email": "client@acme.com",
            "password": "client123",
            "full_name": "John Client (Acme)",
            "role_id": db.query(Role).filter(Role.name == "client").first().id,
        },
    ]
    
    for user_data in users_data:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            password = user_data.pop("password")
            user = User(
                **user_data,
                password_hash=pwd_context.hash(password)
            )
            db.add(user)
    
    db.commit()
    print("✓ Users seeded")


def seed_clients(db: Session):
    """Seed sample clients."""
    print("Seeding clients...")
    
    clients_data = [
        {
            "company_name": "Acme Corporation",
            "contact_person": "John Smith",
            "email": "john@acme.com",
            "phone": "+1-555-0100",
            "address": "123 Business St, New York, NY 10001",
            "tax_id": "TAX-001",
            "payment_terms": 30,
            "credit_limit": 50000.00,
        },
        {
            "company_name": "Global Trading Ltd",
            "contact_person": "Jane Doe",
            "email": "jane@globaltrading.com",
            "phone": "+1-555-0200",
            "address": "456 Commerce Ave, Los Angeles, CA 90001",
            "tax_id": "TAX-002",
            "payment_terms": 45,
            "credit_limit": 100000.00,
        },
    ]
    
    sales_user = db.query(User).filter(User.email == "sales@smartquote.com").first()
    
    for client_data in clients_data:
        existing = db.query(Client).filter(Client.company_name == client_data["company_name"]).first()
        if not existing:
            # Assign Acme to Sales Rep
            if client_data["company_name"] == "Acme Corporation" and sales_user:
                client_data["sales_rep_id"] = sales_user.id
            
            client = Client(**client_data)
            db.add(client)
            db.flush() # Flush to get ID
            
            # Link client user to Acme
            if client.company_name == "Acme Corporation":
                client_user = db.query(User).filter(User.email == "client@acme.com").first()
                if client_user:
                    client_user.client_id = client.id
                    db.add(client_user)
    
    db.commit()
    print("✓ Clients seeded")


def seed_products(db: Session):
    """Seed sample products."""
    print("Seeding products...")
    
    products_data = [
        {
            "sku": "PROD-001",
            "name": "Premium Widget A",
            "description": "High-quality widget for industrial use",
            "category": "Widgets",
            "unit": "pcs",
            "min_order_qty": 100,
            "lingxing_product_id": "LX-WIDGET-A",
        },
        {
            "sku": "PROD-002",
            "name": "Standard Widget B",
            "description": "Standard widget for general applications",
            "category": "Widgets",
            "unit": "pcs",
            "min_order_qty": 50,
            "lingxing_product_id": "LX-WIDGET-B",
        },
        {
            "sku": "PROD-003",
            "name": "Connector Kit",
            "description": "Universal connector kit with 20 pieces",
            "category": "Accessories",
            "unit": "kit",
            "min_order_qty": 10,
            "lingxing_product_id": "LX-CONN-KIT",
        },
    ]
    
    for product_data in products_data:
        existing = db.query(Product).filter(Product.sku == product_data["sku"]).first()
        if not existing:
            product = Product(**product_data)
            db.add(product)
    
    db.commit()
    print("✓ Products seeded")


def seed_base_prices(db: Session):
    """Seed base prices for products."""
    print("Seeding base prices...")
    
    admin_user = db.query(User).filter(User.email == "admin@smartquote.com").first()
    products = db.query(Product).all()
    
    # Base prices for each tier
    tier_multipliers = {
        "X": 1.0,    # Premium tier
        "S": 0.85,   # Standard tier
        "A": 0.70,   # Economy tier
    }
    
    base_prices_map = {
        "PROD-001": 100.00,
        "PROD-002": 75.00,
        "PROD-003": 50.00,
    }
    
    today = date.today()
    
    for product in products:
        base_price = base_prices_map.get(product.sku, 100.00)
        
        for tier, multiplier in tier_multipliers.items():
            existing = db.query(BasePrice).filter(
                BasePrice.product_id == product.id,
                BasePrice.tier == tier,
                BasePrice.effective_to.is_(None)
            ).first()
            
            if not existing:
                price = BasePrice(
                    product_id=product.id,
                    tier=tier,
                    price=base_price * multiplier,
                    effective_from=today,
                    created_by=admin_user.id if admin_user else None,
                )
                db.add(price)
    
    db.commit()
    print("✓ Base prices seeded")


def seed_inventory(db: Session):
    """Seed inventory data."""
    print("Seeding inventory...")
    
    products = db.query(Product).all()
    warehouses = ["WH-001", "WH-002"]
    
    for product in products:
        for warehouse in warehouses:
            existing = db.query(Inventory).filter(
                Inventory.product_id == product.id,
                Inventory.warehouse_code == warehouse
            ).first()
            
            if not existing:
                inventory = Inventory(
                    product_id=product.id,
                    warehouse_code=warehouse,
                    available_qty=1000,
                    reserved_qty=0,
                    last_sync_at=datetime.now(),
                    lingxing_warehouse_id=f"LX-{warehouse}",
                )
                db.add(inventory)
    
    db.commit()
    print("✓ Inventory seeded")


def main():
    """Run all seed functions."""
    print("\n" + "="*50)
    print("SmartQuote Database Seeding")
    print("="*50 + "\n")
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Seed data in order
        seed_roles(db)
        seed_users(db)
        seed_clients(db)
        seed_products(db)
        seed_base_prices(db)
        seed_inventory(db)
        
        print("\n" + "="*50)
        print("✓ Database seeding completed successfully!")
        print("="*50)
        print("\nDefault credentials:")
        print("  Super Admin: admin@smartquote.com / admin123")
        print("  Admin: manager@smartquote.com / manager123")
        print("  Sales: sales@smartquote.com / sales123")
        print("  Client: client@acme.com / client123")
        print("\n⚠️  Remember to change these passwords in production!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
