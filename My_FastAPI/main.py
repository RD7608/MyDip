from fastapi import FastAPI
from fastapi.responses import HTMLResponse


from routers import order, user, sprav


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def welcome():
    return """
    <html>
        <head>
            <title>Доставка воды</title>
        </head>
        <body>
            <h1>Добро пожаловать в службу доставки воды!</h1>
            <p>Для оформления заказа, используйте соответствующие маршруты API.</p>
            
            
        </body>
    </html>
    """

app.include_router(order.router)
#app.include_router(cart.router)
app.include_router(user.router)
app.include_router(sprav.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)