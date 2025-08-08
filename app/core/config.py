import os
from pathlib import Path
from dotenv import load_dotenv

# 在开发环境中加载 .env 文件
# Docker环境中，docker-compose会处理环境变量
load_dotenv()

# 项目根目录
# /Users/lirenjie/Documents/CodeCraft/LevelRAG/JsonTreeRAG
# app/core/config.py -> ../../..
# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# 修正路径计算
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent


# --- 文件路径 ---
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
KNOWLEDGE_BASE_FILE = DATA_DIR / "combined_output.json"
CHROMADB_PATH = DB_DIR / "chromadb"

# 确保必要目录存在
for directory in [DATA_DIR, DB_DIR, CHROMADB_PATH]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception:
        # 在只读环境或权限受限环境下忽略
        pass

# --- ChromaDB 配置 ---
CHROMA_COLLECTION_NAME = "knowledge_base"

# --- Embedding 服务配置 ---
# 注意：URL将由客户端代码确保以'/'结尾
EMBEDDING_API_BASE_URL = os.getenv("EMBEDDING_API_BASE_URL", "http://localhost:8001/v1")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "dummy-key") # 提供一个默认值
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-large-zh-v1.5")

# --- LLM (vLLM) 服务配置 ---
# 注意：URL将由客户端代码确保以'/'结尾
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:8002/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "dummy-key") # 提供一个默认值
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen1.5-14B-Chat")

# --- RAG 配置 ---
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
