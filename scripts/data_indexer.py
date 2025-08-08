# 用于执行一次性数据索引的脚本

import json
import chromadb
import sys
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 将项目根目录添加到 sys.path
# /Users/lirenjie/Documents/CodeCraft/LevelRAG/JsonTreeRAG/scripts/data_indexer.py
# -> /Users/lirenjie/Documents/CodeCraft/LevelRAG/JsonTreeRAG
# scripts -> ..
# JsonTreeRAG -> ..
# /Users/lirenjie/Documents/CodeCraft/LevelRAG
# BASE_DIR = Path(__file__).resolve().parent.parent
# sys.path.append(str(BASE_DIR))
# print(f"Added {BASE_DIR} to sys.path")
# print(sys.path)
# from app.core import config

# 修正路径问题，直接导入
try:
    from app.core import config
except ImportError:
    # 如果上述导入失败，可能是因为脚本是从其所在目录直接运行的
    # 我们需要手动将项目的根目录添加到Python路径中
    # /Users/lirenjie/Documents/CodeCraft/LevelRAG/JsonTreeRAG/scripts/data_indexer.py
    # -> /Users/lirenjie/Documents/CodeCraft/LevelRAG/JsonTreeRAG
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    from app.core import config

# --- 关键改动 ---
# 在配置加载（补丁已生效）之后，再导入OpenAI客户端
from openai import OpenAI


def get_embedding_client():
    """根据配置初始化并返回用于Embedding的OpenAI客户端。"""
    logging.info(f"[Embedding Client] Initializing with base_url: {config.EMBEDDING_API_BASE_URL}")
    return OpenAI(
        api_key=config.EMBEDDING_API_KEY,
        base_url=config.EMBEDDING_API_BASE_URL
    )

def get_chroma_client():
    """初始化并返回ChromaDB客户端和集合。"""
    client = chromadb.PersistentClient(path=str(config.CHROMADB_PATH))
    collection = client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
    )
    return collection

def load_knowledge_base():
    """加载JSON知识库文件。"""
    if not config.KNOWLEDGE_BASE_FILE.exists():
        logging.error(f"知识库文件未找到: {config.KNOWLEDGE_BASE_FILE}")
        return None
    with open(config.KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def traverse_and_prepare_data(data):
    """
    递归遍历JSON树，为每个节点准备要索引的数据。

    返回:
        - documents (list): 用于Embedding的文本文档列表。
        - metadatas (list): 每个文档对应的元数据列表，包含路径ID。
        - ids (list): 每个文档的唯一ID列表（这里也使用路径ID）。
    """
    documents = []
    metadatas = []
    
    def _traverse(nodes, path_parts):
        if not isinstance(nodes, list):
            logging.warning(f"期望节点列表，但得到: {type(nodes).__name__}")
            return
        for node in nodes:
            if not isinstance(node, dict):
                logging.warning("跳过非字典节点")
                continue
            name = node.get('name')
            if not name:
                logging.warning("跳过缺少 'name' 的节点")
                continue
            current_path_parts = path_parts + [name]
            path_id = '>'.join(current_path_parts)
            
            # 组合 name 和 desc 作为索引内容
            desc = node.get('desc', '')
            content = f"{name}\n{desc}".strip()
            
            documents.append(content)
            metadatas.append({'path_id': path_id})
            
            children = node.get('child')
            if isinstance(children, list) and children:
                _traverse(children, current_path_parts)

    _traverse(data, [])
    
    # 使用 path_id 作为 ChromaDB 的唯一 ID
    ids = [meta['path_id'] for meta in metadatas]
    
    return documents, metadatas, ids

def embed_documents(documents, openai_client):
    """使用OpenAI API为文档批量生成Embeddings。"""
    if not documents:
        return []
    try:
        logging.info(f"[Embedding] Sending {len(documents)} document(s) to embedding service.")
        logging.info(f"[Embedding] Model: {config.EMBEDDING_MODEL}")
        
        response = openai_client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=documents
        )
        
        logging.info(f"[Embedding] Received {len(response.data)} embedding(s).")
        embeddings = []
        for item in response.data:
            vector = getattr(item, 'embedding', None)
            if vector is None and isinstance(item, dict):
                vector = item.get('embedding')
            embeddings.append(vector)
        return embeddings
    
    except Exception as e:
        logging.error(f"[Embedding] An error occurred: {e}", exc_info=True)
        # 打印更详细的请求信息，如果可能的话
        if hasattr(e, 'request'):
            logging.error(f"[Embedding] Request URL: {e.request.url}")
            logging.error(f"[Embedding] Request Method: {e.request.method}")
            # logging.error(f"[Embedding] Request Headers: {e.request.headers}")
            # content = e.request.content.decode('utf-8') if e.request.content else ''
            # logging.error(f"[Embedding] Request Content: {content[:500]}...") # 打印前500个字符
        return None


def main():
    """主函数，执行整个索引流程。"""
    logging.info("开始执行数据索引流程...")

    # 1. 加载知识库
    knowledge_data = load_knowledge_base()
    if knowledge_data is None:
        return
    logging.info(f"成功加载知识库: {config.KNOWLEDGE_BASE_FILE}")

    # 2. 初始化客户端
    try:
        embedding_client = get_embedding_client()
        chroma_collection = get_chroma_client()
        logging.info(f"成功连接到ChromaDB，集合: '{config.CHROMA_COLLECTION_NAME}'")
    except Exception as e:
        logging.error(f"初始化客户端时失败: {e}")
        return

    # 3. 遍历和准备数据
    documents, metadatas, ids = traverse_and_prepare_data(knowledge_data)
    logging.info(f"数据准备完成，共找到 {len(documents)} 个节点需要索引。")

    if not documents:
        logging.warning("没有找到可索引的文档，脚本结束。")
        return

    # 4. 生成Embeddings
    logging.info(f"正在为文档生成Embeddings，使用模型: {config.EMBEDDING_MODEL}...")
    embeddings = embed_documents(documents, embedding_client)
    if embeddings is None:
        logging.error("无法生成Embeddings，索引流程中断。")
        return
    logging.info("Embeddings生成成功。")

    # 4.1 过滤无效的向量，保持与文档/元数据/ID一一对应
    original_len = len(documents)
    if len(embeddings) != original_len:
        logging.warning(
            f"Embedding 数量({len(embeddings)})与文档数量({original_len})不一致，将按就地对齐并过滤无效项。"
        )
    filtered = [
        (e, d, m, i)
        for e, d, m, i in zip(embeddings, documents, metadatas, ids)
        if e is not None
    ]
    if not filtered:
        logging.error("所有向量均无效，无法写入 ChromaDB。")
        return
    embeddings, documents, metadatas, ids = (
        [x[0] for x in filtered],
        [x[1] for x in filtered],
        [x[2] for x in filtered],
        [x[3] for x in filtered],
    )
    dropped_count = original_len - len(filtered)
    if dropped_count:
        logging.warning(f"因无效向量被丢弃的条目数: {dropped_count}")

    # 5. 存入ChromaDB
    try:
        logging.info("正在将数据批量存入ChromaDB...")
        # ChromaDB的add方法是upsert逻辑，如果ID已存在则会更新
        chroma_collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logging.info(f"成功将 {len(ids)} 条数据存入ChromaDB。")
        logging.info("数据索引流程全部完成！")
    except Exception as e:
        logging.error(f"存入ChromaDB时出错: {e}")

if __name__ == "__main__":
    main()
