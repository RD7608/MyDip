from fastapi import FastAPI , HTTPException , Request , Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session


from backend.db_depends import get_db
from models import Product
from routers import order , user , sprav, cart
from config import templates

app = FastAPI ()

app.mount ( "/static" , StaticFiles ( directory="static" ) , name="static" )

@app.get ( "/" , response_class=HTMLResponse )
async def home(request: Request , db: Session = Depends ( get_db )):
    query = select ( Product ).where ( Product.is_available == True )
    result = db.execute ( query )  # Выполняем запрос
    products = result.scalars ().all ()  # Получаем все доступные продукты
    return templates.TemplateResponse ( 'home.html' , {"request": request , "products": products} )


@app.get ( "/news" , response_class=HTMLResponse )
async def news():
    return templates.TemplateResponse ( 'news.html' , {"request": {}} )


@app.get ( "/about" , response_class=HTMLResponse )
async def about():
    return templates.TemplateResponse ( 'about.html' , {"request": {}} )


app.include_router ( order.router )
app.include_router(cart.router)
app.include_router ( user.router )
app.include_router ( sprav.router )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run ( "main:app" , host="127.0.0.1" , port=8001 , log_level="debug" )
