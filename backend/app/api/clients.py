from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Client, User, Role
from ..schemas.client import ClientCreate, ClientResponse, ClientUpdate
from ..middleware.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Client)
    
    # RBAC Logic
    if current_user.role.name == "sales":
        query = query.filter(Client.sales_rep_id == current_user.id)
    elif current_user.role.name == "client":
        # Clients shouldn't see list of other clients
        # Maybe return their own if they really call this
        query = query.filter(Client.id == current_user.client_id)
    
    clients = query.offset(skip).limit(limit).all()
    return clients

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check permissions
    if current_user.role.name == "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clients cannot create new client accounts"
        )

    if client_in.email:
        existing_client = db.query(Client).filter(Client.email == client_in.email).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already exists"
            )
    
    client_data = client_in.model_dump()
    
    # RBAC: Sales reps auto-assigned to themselves
    if current_user.role.name == "sales":
        client_data["sales_rep_id"] = current_user.id
        # Sales cannot set Tier (default to 'A')
        client_data["tier"] = "A" 
    
    new_client = Client(**client_data)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # RBAC Check
    if current_user.role.name == "sales" and client.sales_rep_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this client")
    if current_user.role.name == "client" and client.id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this client")
        
    return client

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # RBAC Check
    if current_user.role.name == "sales" and client.sales_rep_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this client")
    if current_user.role.name == "client":
         raise HTTPException(status_code=403, detail="Clients cannot update their own profile directly")

    update_data = client_in.model_dump(exclude_unset=True)
    
    # RBAC: Prevent sales from changing sensitive fields
    if current_user.role.name == "sales":
        update_data.pop("tier", None)
        update_data.pop("sales_rep_id", None)
        update_data.pop("credit_limit", None)
        update_data.pop("payment_terms", None)

    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client
