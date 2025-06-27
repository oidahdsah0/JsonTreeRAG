import json
from openai import AsyncOpenAI
import logging
from functools import lru_cache

from app.core import config

# --- 客户端初始化 ---
@lru_cache(maxsize=1)
def get_llm_client():
    """根据配置初始化并返回用于LLM的OpenAI客户端。"""
    return AsyncOpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_API_BASE_URL
    )

# --- 提示词模板 ---
PROMPT_TEMPLATE = """
### 系统指令
你是一个专业的汽车故障诊断助手。请根据下面提供的“知识路径”和“相关知识子树”内容，结合用户的具体问题，给出一个严谨、详细的回答。请严格依据提供的上下文作答，不要编造信息。
注意1：你需要在回答里完整呈现“知识路径”及“相关知识子树”的内容作为解决方案的依据，且必须以Markdown格式呈现，不可遗漏！相当重要！
注意2：回答仅由3部分组成：1. **知识路径**：直接引用“知识路径”内容；2. **解决方案**：直接引用“相关知识子树”内容，不可遗漏；3. **推荐问题**：基于用户问题，推荐一个相关的后续问题。

### 知识路径
{retrieved_path}

### 相关知识子树
```json
{retrieved_subtree_json_string}
```

### 用户问题
{user_question}

### 你的回答
"""

def build_prompt(retrieved_path: str, retrieved_subtree: dict, user_question: str) -> str:
    """
    根据检索到的上下文和用户问题，构建最终的提示词。
    """
    # 将子树JSON对象格式化为美观的字符串
    retrieved_subtree_json_string = json.dumps(retrieved_subtree, indent=2, ensure_ascii=False)
    
    prompt = PROMPT_TEMPLATE.format(
        retrieved_path=retrieved_path,
        retrieved_subtree_json_string=retrieved_subtree_json_string,
        user_question=user_question
    )
    return prompt

async def get_llm_stream(prompt: str):
    """
    调用LLM并以流式方式返回响应。

    Yields:
        str: 从LLM返回的响应内容块。
    """
    client = get_llm_client()
    try:
        stream = await client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "system", "content": prompt}],
            stream=True,
            temperature=0.7, # 可以根据需要调整
            max_tokens=20000, # 限制最大输出长度
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False  # 启用思考模式
                }
            }
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        logging.error(f"调用LLM API失败: {e}")
        # 在流中产生一个错误信息，以便客户端可以优雅地处理
        yield f"Error: Could not connect to the language model. Details: {e}"
