from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from apis.auth import router as auth_router
from apis.user import router as user_router
from apis.article import router as article_router
from apis.wechat import router as wechat_router

app = FastAPI(
    title="WeRSS API",
    description="微信公众号RSS生成服务",
    version="1.0.0"
)

# 集成路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(article_router)
app.include_router(wechat_router)

# 静态文件服务
app.mount("/", StaticFiles(directory="static", html=True), name="static")