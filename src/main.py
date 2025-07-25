import os
import sys

src_root = os.path.dirname(os.path.abspath(__file__))
if src_root not in sys.path:
    sys.path.insert(0, src_root)
    
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_config
from util import log, log_init
from database import db_init


@asynccontextmanager
async def lifespan(app: FastAPI):
    #  启动阶段
    start_time = time.time()
    log_init(clear=True)
    db_init()
    end_time = time.time()
    log.info(f"应用程序初始化完成，耗时:{end_time - start_time:.2f}秒")

    yield
    # 关闭阶段
    log.info("🛑 应用关闭中......")
    log.info("✅ 应用成功关闭")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn

    CONFIG = get_config("dev")
    uvicorn.run("main:app", host=CONFIG.HOST, port=CONFIG.PORT, reload=CONFIG.RELOAD)
