from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from ..models.quotation import Quotation, QuotationItem
from ..models.product import Product
from ..models.pricing import BasePrice, ClientPrice
from ..models.client import Client
from ..schemas.quotation import QuotationCreate, QuotationUpdate
from typing import Optional


class QuoteService:
    def __init__(self, db: Session):
        self.db = db

    def _get_active_price(self, client_id: int, product_id: int) -> float:
        """
        Calculate the active price for a product and client.
        Priority:
        1. Client-specific price (ClientPrice)
        2. Tier-based base price (BasePrice)
        """
        today = date.today()
        
        # 1. Check for client-specific price
        client_price = self.db.query(ClientPrice).filter(
            ClientPrice.client_id == client_id,
            ClientPrice.product_id == product_id,
            ClientPrice.effective_from <= today,
            (ClientPrice.effective_to.is_(None) | (ClientPrice.effective_to >= today))
        ).order_by(desc(ClientPrice.effective_from)).first()
        
        if client_price:
            return float(client_price.price)
            
        # 2. Check for base price based on client tier
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return 0.0 # Should probably raise error
            
        tier = client.tier or "A" # Default to A if not set
        
        base_price = self.db.query(BasePrice).filter(
            BasePrice.product_id == product_id,
            BasePrice.tier == tier,
            BasePrice.effective_from <= today,
            (BasePrice.effective_to.is_(None) | (BasePrice.effective_to >= today))
        ).order_by(desc(BasePrice.effective_from)).first()
        
        if base_price:
            return float(base_price.price)
            
        # 3. Fallback: Check for bundle components
        # If no explicit price, sum up component prices * quantity
        if product_id:
             # Need to fetch product to check components
             # Optimization: Join components eagerly? 
             # For now, lazy load is fine as depth is usually 1.
             product = self.db.query(Product).filter(Product.id == product_id).first()
             if product and product.components:
                 bundle_price = 0.0
                 for component in product.components:
                     # Recursive call for each child
                     child_price = self._get_active_price(client_id, component.child_product_id)
                     bundle_price += child_price * component.quantity
                 
                 if bundle_price > 0:
                     return bundle_price
            
        return 0.0

    def create_quotation(self, quote_in: QuotationCreate, user_id: int) -> Quotation:
        # Create quote record
        # Generate generic quote number for now (should be better logic)
        import uuid
        quote_number = f"Q-{uuid.uuid4().hex[:8].upper()}"
        
        db_quote = Quotation(
            quotation_number=quote_number,
            client_id=quote_in.client_id,
            valid_until=quote_in.valid_until,
            notes=quote_in.notes,
            currency=quote_in.currency,
            created_by=user_id,
            status="draft"
        )
        self.db.add(db_quote)
        self.db.flush() # Flush to get ID
        
        total_amount = 0.0
        
        for item_in in quote_in.items:
            # Calculate price
            unit_price = self._get_active_price(quote_in.client_id, item_in.product_id)
            
            # Override if provided (business decision: do we allow sales to override?)
            # For now, let's assume the service calculates it, 
            # but if the schema allows passing price, we might use it. 
            # The schema QuotationItemCreate actually asks for unit_price. 
            # If the user provides it, we use it. If 0/null, we fetch it?
            # Creating schema required unit_price.
            # Let's assume the frontend might ask for a price check first, OR 
            # we respect the submitted price but validate it.
            # For this implementation, I will trust the submitted price if > 0, else calculate.
            
            final_unit_price = float(item_in.unit_price)
            if final_unit_price <= 0:
                final_unit_price = unit_price
            
            db_item = QuotationItem(
                quotation_id=db_quote.id,
                product_id=item_in.product_id,
                quantity=item_in.quantity,
                unit_price=final_unit_price,
                discount_percent=item_in.discount_percent,
                notes=item_in.notes
            )
            self.db.add(db_item)
            
            # Calculate line total
            line_total = float(item_in.quantity) * final_unit_price * (1 - float(item_in.discount_percent) / 100)
            total_amount += line_total
            
        db_quote.total_amount = total_amount
        self.db.commit()
        self.db.refresh(db_quote)
        return db_quote

    def get_quotations(self, skip: int = 0, limit: int = 100, client_id: Optional[int] = None, sales_rep_id: Optional[int] = None):
        query = self.db.query(Quotation)
        
        if client_id:
            query = query.filter(Quotation.client_id == client_id)
            
        if sales_rep_id:
            query = query.join(Client).filter(Client.sales_rep_id == sales_rep_id)
            
        return query.offset(skip).limit(limit).all()

    def get_quotation(self, quotation_id: int):
        return self.db.query(Quotation).filter(Quotation.id == quotation_id).first()
