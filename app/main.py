# FastAPI 主应用和 API 端点
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import logging
import uuid
import time
from typing import Literal, Optional, List
import asyncio

from app.services.retrieval import get_context_from_retrieval
from app.services.llm_handler import build_prompt, get_llm_stream
from app.core import config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="OpenAI-Compatible RAG API",
    description="一个基于树形JSON知识库的、符合OpenAI标准的RAG问答系统",
    version="1.1.0",
)

# --- OpenAI 兼容的 Pydantic 模型 ---

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    stream: bool = Field(default=False, description="是否以流式方式返回响应")
    # 可以根据需要添加其他OpenAI参数，如 temperature, max_tokens 等

class Delta(BaseModel):
    content: Optional[str] = None

class ChoiceDelta(BaseModel):
    delta: Delta
    index: int = 0
    finish_reason: Optional[str] = None

class StreamingChatCompletion(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChoiceDelta]


@app.get("/")
def read_root():
    return {"message": "Welcome to the OpenAI-Compatible RAG API. Visit /docs for documentation."}

async def stream_generator(retrieved_path, retrieved_subtree, user_question, model_name: str):
    """生成器函数，用于处理并以OpenAI兼容格式流式传输LLM的响应。"""
    # 1. 构建提示
    prompt = build_prompt(retrieved_path, retrieved_subtree, user_question)
    logging.info(f"构建的提示: \n{prompt}")
    
    # 2. 获取LLM流
    llm_response_stream = get_llm_stream(prompt, model=model_name)
    
    # 3. 迭代流并yield OpenAI兼容的数据块
    async for chunk in llm_response_stream:
        if chunk: # 确保内容不为空
            response_chunk = StreamingChatCompletion(
                model=model_name,
                choices=[ChoiceDelta(delta=Delta(content=chunk))]
            )
            # 兼容 pydantic v1/v2 的 JSON 序列化（优先使用 v2 的 model_dump_json）
            json_str = response_chunk.model_dump_json() if hasattr(response_chunk, 'model_dump_json') else response_chunk.json()
            yield f"data: {json_str}\n\n"
    
    # 4. 发送带有 finish_reason 的最后一个数据块
    final_chunk = StreamingChatCompletion(
        model=model_name,
        choices=[ChoiceDelta(delta=Delta(), finish_reason="stop")]
    )
    json_str = final_chunk.model_dump_json() if hasattr(final_chunk, 'model_dump_json') else final_chunk.json()
    yield f"data: {json_str}\n\n"
    
    # 5. 发送流结束标志
    yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    接收符合OpenAI标准的聊天请求，检索相关知识，并以流式方式返回LLM的回答。
    """
    # 只处理流式请求
    if not request.stream:
        raise HTTPException(status_code=400, detail="This endpoint only supports streaming requests. Please set 'stream: true'.")

    # 从消息列表中提取最后一个用户问题
    user_question = next((msg.content for msg in reversed(request.messages) if msg.role == 'user'), None)
    
    if not user_question:
        raise HTTPException(status_code=400, detail="No user message found in the request.")
        
    logging.info(f"收到问题: {user_question}")

    # 1. 确定模型名（请求优先，否则使用默认配置）
    model_name = request.model or config.LLM_MODEL

    # 2. 检索上下文（在线程池中运行以避免阻塞事件循环）
    loop = asyncio.get_running_loop()
    retrieved_path, retrieved_subtree = await loop.run_in_executor(
        None, lambda: get_context_from_retrieval(user_question)
    )

    # 3. 如果没有找到上下文，返回特定的流式消息
    if not retrieved_path or not retrieved_subtree:
        logging.warning("未能从知识库中检索到相关上下文。")
        async def not_found_stream():
            error_message = "抱歉，我无法在知识库中找到与您问题相关的信息。请尝试换一种问法。"
            # 发送错误消息块
            response_chunk = StreamingChatCompletion(
                model=model_name,
                choices=[ChoiceDelta(delta=Delta(content=error_message))]
            )
            json_str = response_chunk.model_dump_json() if hasattr(response_chunk, 'model_dump_json') else response_chunk.json()
            yield f"data: {json_str}\n\n"
            # 发送结束块
            final_chunk = StreamingChatCompletion(
                model=model_name,
                choices=[ChoiceDelta(delta=Delta(), finish_reason="stop")]
            )
            json_str = final_chunk.model_dump_json() if hasattr(final_chunk, 'model_dump_json') else final_chunk.json()
            yield f"data: {json_str}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(not_found_stream(), media_type="text/event-stream")

    logging.info(f"成功检索到上下文路径: {retrieved_path}")

    # 4. 创建并返回流式响应
    return StreamingResponse(
        stream_generator(retrieved_path, retrieved_subtree, user_question, model_name),
        media_type="text/event-stream"
    )

# 添加一个用于开发时快速启动的命令
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
