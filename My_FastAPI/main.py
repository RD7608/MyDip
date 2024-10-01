from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from routers import order, user, sprav
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')


@app.get("/", response_class=HTMLResponse)
async def home():
    return templates.TemplateResponse('home.html', {"request": {}})


@app.get("/news", response_class=HTMLResponse)
async def news():
    return templates.TemplateResponse('news.html', {"request": {}})


@app.get("/about", response_class=HTMLResponse)
async def about():
    return templates.TemplateResponse('about.html', {"request": {}})


app.include_router(order.router)
# app.include_router(cart.router)
app.include_router(user.router)
app.include_router(sprav.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, log_level="debug")
