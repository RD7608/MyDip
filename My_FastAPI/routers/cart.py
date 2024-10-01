from fastapi import APIRouter
from sqlalchemy.orm import Session
from backend.db_depends import get_db
#from models import Cart

router = APIRouter ( prefix="/cart" , tags=["cart"] )


@app.post ( "/cart/" )
async def create_cart(cart: Cart , db: Session = Depends ( get_db )):
    db.add ( cart )
    db.commit ()
    db.refresh ( cart )
    return cart
