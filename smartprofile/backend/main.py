from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import student

app = FastAPI(title="SmartProfile API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(student.router)

@app.get("/")
def read_root():
    """根路径"""
    return {"message": "SmartProfile API is running"}