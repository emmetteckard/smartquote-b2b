from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.quote_service import QuoteService
from ..schemas.quotation import QuotationCreate, QuotationResponse
from ..middleware.deps import get_current_user
from ..models.user import User

router = APIRouter()

@router.post("/", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    quote_in: QuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quote_service = QuoteService(db)
    return quote_service.create_quotation(quote_in, current_user.id)

@router.get("/", response_model=List[QuotationResponse])
async def list_quotations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quote_service = QuoteService(db)
    
    filter_client_id = None
    filter_sales_rep_id = None
    
    if current_user.role.name == "client":
        filter_client_id = current_user.client_id
    elif current_user.role.name == "sales":
        filter_sales_rep_id = current_user.id
        
    return quote_service.get_quotations(
        skip=skip, 
        limit=limit, 
        client_id=filter_client_id, 
        sales_rep_id=filter_sales_rep_id
    )

@router.get("/{quote_id}", response_model=QuotationResponse)
async def get_quotation(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quote_service = QuoteService(db)
    quote = quote_service.get_quotation(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quote
