import json
import chromadb
from openai import OpenAI
from functools import lru_cache
import logging

from app.core import config

# --- 客户端初始化 ---

@lru_cache(maxsize=1)
def get_embedding_client():
    """根据配置初始化并返回用于Embedding的OpenAI客户端。"""
    return OpenAI(
        api_key=config.EMBEDDING_API_KEY,
        base_url=config.EMBEDDING_API_BASE_URL
    )

@lru_cache(maxsize=1)
def get_chroma_collection():
    """初始化并返回ChromaDB集合（带缓存）。"""
    client = chromadb.PersistentClient(path=str(config.CHROMADB_PATH))
    return client.get_collection(name=config.CHROMA_COLLECTION_NAME)

@lru_cache(maxsize=1)
def get_knowledge_base():
    """加载并缓存JSON知识库文件。"""
    with open(config.KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 检索功能 ---

def embed_query(query_text: str):
    """将用户查询文本转换为向量。"""
    client = get_embedding_client()
    try:
        response = client.embeddings.create(
            input=[query_text],
            model=config.EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        logging.error(f"查询向量化失败: {e}")
        return None

def search_knowledge_base(query_vector: list[float]):
    """在ChromaDB中执行相似度搜索。"""
    collection = get_chroma_collection()
    try:
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=config.TOP_K_RESULTS
        )
        return results
    except Exception as e:
        logging.error(f"知识库检索失败: {e}")
        return None

# --- 上下文提取 ---

def find_node_by_path(path_id: str):
    """
    根据路径ID在JSON知识库中查找并返回对应的节点。

    Args:
        path_id (str): 形如 'A>B>C' 的路径ID。

    Returns:
        dict: 找到的节点对象，如果未找到则返回None。
    """
    path_parts = path_id.split('>')
    current_level = get_knowledge_base()
    
    for part in path_parts:
        found_node = None
        # 在当前层级的节点中查找匹配的name
        for node in current_level:
            if node.get('name') == part:
                found_node = node
                # 如果不是最后一个部分，就进入下一层child
                if part != path_parts[-1]:
                    current_level = node.get('child', [])
                break
        
        if found_node is None:
            logging.warning(f"路径 '{path_id}' 在 '{part}' 部分中断，未找到节点。")
            return None
            
    # 循环结束后，found_node 应该是目标节点
    # 但我们需要确认它是否是路径的终点
    if found_node and found_node.get('name') == path_parts[-1]:
        return found_node
    else:
        logging.error(f"路径 '{path_id}' 解析逻辑出现意外错误。")
        return None

def get_context_from_retrieval(query: str):
    """
    完整的检索和上下文提取流程。

    1.  将查询向量化。
    2.  在向量数据库中搜索。
    3.  获取Top 1结果的路径ID。
    4.  根据路径ID在JSON中找到节点。
    5.  提取路径和子树作为上下文。

    Returns:
        tuple[str, dict] | tuple[None, None]: (知识路径, 知识子树) 或 (None, None)
    """
    query_vector = embed_query(query)
    if not query_vector:
        return None, None

    search_results = search_knowledge_base(query_vector)

    # --- 增强的命中日志 ---
    if search_results and search_results.get('ids') and search_results['ids'][0]:
        # 使用json.dumps美化输出，方便阅读
        pretty_results = {
            "ids": search_results['ids'][0],
            "distances": [round(d, 4) for d in search_results['distances'][0]],
            "documents": [doc.replace('\n', ' ') for doc in search_results['documents'][0]]
        }
        logging.info(f"知识库命中! 查询: '{query}'. 检索结果: {json.dumps(pretty_results, ensure_ascii=False, indent=2)}")
    else:
        logging.info(f"在知识库中未找到与查询 '{query}' 相关的内容。")
        return None, None
    # --- 日志结束 ---

    # 取最相关的结果
    top_result_id = search_results['ids'][0][0]
    logging.info(f"检索到的最相关路径ID: {top_result_id}")

    # 格式化路径信息
    retrieved_path = top_result_id.replace('>', ' -> ')

    # 查找节点并获取子树
    retrieved_subtree = find_node_by_path(top_result_id)

    if not retrieved_subtree:
        logging.error(f"根据ID '{top_result_id}' 未能从JSON文件中找到节点。")
        return None, None

    return retrieved_path, retrieved_subtree
