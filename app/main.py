from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from .models import Base
from .schemas import UserCreate, UserResponse, TicketCreate, TicketResponse
from .crud import (
    get_user,
    get_user_by_username,
    create_user,
    create_ticket,
    get_tickets_by_owner,
    update_ticket_status,
    delete_ticket,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Support System API", version="1.0")

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_new_ticket(ticket: TicketCreate, owner_id: int, db: Session = Depends(get_db)):
    owner = get_user(db, owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")
    return create_ticket(db, ticket, owner_id)

@app.get("/tickets/owner/{owner_id}", response_model=List[TicketResponse])
def list_tickets_for_owner(owner_id: int, db: Session = Depends(get_db)):
    return get_tickets_by_owner(db, owner_id)

@app.patch("/tickets/{ticket_id}/status")
def change_ticket_status(ticket_id: int, new_status: str, db: Session = Depends(get_db)):
    allowed_statuses = {"new", "in_progress", "closed"}
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed_statuses}")
    updated = update_ticket_status(db, ticket_id, new_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"id": updated.id, "status": updated.status}

@app.delete("/tickets/{ticket_id}")
def remove_ticket(ticket_id: int, db: Session = Depends(get_db)):
    deleted = delete_ticket(db, ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Ticket deleted"}