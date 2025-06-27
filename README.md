# JsonTreeRAG: 基于本地私有知识库的RAG问答系统

本项目是一个基于私有知识库的检索增强生成（RAG）问答系统。它专门为层级化的JSON格式知识库设计，通过向量化检索与上下文子树提取，为本地大语言模型（LLM）提供精准的背景知识，从而生成高质量的回答。

所有服务组件均支持本地化部署，API设计与OpenAI标准兼容，方便与现有工具链集成。

## 核心特性

- **私有化部署**: 所有组件（Embedding服务, LLM服务, RAG应用）均可在本地环境部署，确保数据安全与私密性。
- **层级知识库支持**: 专为树状结构的JSON知识库优化，通过唯一的路径ID实现精准的上下文节点定位与检索。
- **OpenAI兼容API**: 提供与OpenAI完全兼容的 `/v1/chat/completions` 端点，支持流式响应（Server-Sent Events），可无缝对接各类标准客户端或SDK。
- **容器化部署**: 提供 `Dockerfile` 和 `docker-compose.yml`，使用 Docker 实现一键构建、配置和启动，极大简化了部署流程。
- **高度可配置**: 通过 `.env` 文件集中管理所有外部服务（Embedding, LLM）的地址、API密钥和模型名称，轻松切换配置。

## 程序架构

系统由数据层、服务层和应用层组成，通过容器化技术进行解耦和管理。

![程序架构图](https://i.imgur.com/your-architecture-diagram.png)  <!-- 您可以后续替换为真实的架构图 -->

### 组件说明

1.  **`data/`**: 存放原始知识库文件 `combined_output.json`。
2.  **`db/chromadb/`**: ChromaDB 向量数据库的持久化存储目录。通过Docker卷挂载，确保数据在容器重启后不丢失。
3.  **`app/`**: FastAPI 应用核心代码。
    -   **`main.py`**: API 入口。定义 `/v1/chat/completions` 端点，处理HTTP请求和SSE流式响应。
    -   **`services/retrieval.py`**: 检索模块。负责接收用户问题，调用Embedding服务生成向量，在ChromaDB中进行相似度搜索，并根据命中的路径ID提取知识库子树作为上下文。
    -   **`services/llm_handler.py`**: LLM处理模块。负责构建最终的Prompt（包含检索到的上下文和用户问题），调用本地vLLM服务，并以流式方式返回结果。
    -   **`core/config.py`**: 配置模块。从环境变量 (`.env`) 中加载所有服务地址、API密钥和模型名称。
4.  **`scripts/data_indexer.py`**: 数据索引脚本。用于一次性读取知识库JSON，遍历所有节点，调用Embedding服务生成向量，并将其与节点的元数据一同存入ChromaDB。
5.  **`Dockerfile` & `docker-compose.yml`**: 容器化配置文件，定义了如何构建镜像和编排服务。
6.  **`.env`**: 环境变量配置文件，用于存储敏感信息和环境特定的配置。

### 请求流程

`用户查询` -> `FastAPI (main.py)` -> `检索服务 (retrieval.py)` -> `Embedding服务` & `ChromaDB` -> `上下文子树` -> `LLM处理器 (llm_handler.py)` -> `vLLM服务` -> `流式响应` -> `用户`

## 启动方式

请按照以下步骤在您的环境中启动并运行本系统。

### 步骤 1: 环境准备

- 确保您的机器上已安装 [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
- 将本项目代码克隆到本地。

### 步骤 2: 配置环境变量

1.  在项目根目录下，将 `.env.example` 文件复制并重命名为 `.env`。
2.  打开 `.env` 文件，根据您的本地服务实际情况，修改以下配置：
    - `EMBEDDING_API_BASE_URL`: 您的本地Embedding服务的地址。
    - `EMBEDDING_API_KEY`: Embedding服务的API Key (如果需要)。
    - `EMBEDDING_MODEL`: Embedding模型名称。
    - `LLM_API_BASE_URL`: 您的本地vLLM服务的地址。
    - `LLM_API_KEY`: vLLM服务的API Key (如果需要)。
    - `LLM_MODEL`: 您希望使用的LLM模型名称。

### 步骤 3: 放置知识库文件

将您的层级化知识库文件 `combined_output.json` 放置在项目根目录的 `data/` 文件夹下。

### 步骤 4: 构建并运行服务

在项目根目录打开终端，依次执行以下命令。

1.  **构建镜像**
    此命令会根据 `Dockerfile` 创建服务镜像，安装所有Python依赖。
    ```bash
    docker-compose build
    ```

2.  **运行数据索引**
    此命令会运行索引脚本，将您的知识库向量化并存入数据库。**此步骤仅在首次运行或知识库更新后需要执行。**
    ```bash
    docker-compose run --rm app python scripts/data_indexer.py
    ```
    您将看到日志输出，显示索引过程。

3.  **启动API服务**
    此命令会在后台启动主API服务。
    ```bash
    docker-compose up -d
    ```

### 步骤 5: 测试服务

服务现在应该运行在 `http://localhost:21145` (或您在 `docker-compose.yml` 中配置的端口)。您可以使用任何HTTP客户端或Python脚本进行测试。

**使用 `curl` 测试:**
```bash
curl -N -X POST http://localhost:21145/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "Qwen3-32B",
  "messages": [
    {
      "role": "user",
      "content": "请介绍一下AIGC技术的核心概念"
    }
  ],
  "stream": true
}'
```
> **注意**: 请将 `model` 的值替换为您在 `.env` 中配置的 `LLM_MODEL`。

## 注意事项

1.  **URL协议**: 请务必确保 `.env` 文件中配置的服务地址 (`EMBEDDING_API_BASE_URL`, `LLM_API_BASE_URL`) 使用了**正确的协议** (`http` 或 `https`）。这取决于您的本地服务是否配置了SSL/TLS。这是常见的连接错误来源。
2.  **数据持久化**: ChromaDB的数据库文件通过卷挂载持久化在本地的 `db/chromadb` 目录。只要不删除此目录，向量数据就不会丢失。
3.  **更新代码**: 如果您修改了 `app/` 或 `scripts/` 目录下的Python代码，需要重新执行 `docker-compose build` 来应用更改，然后通过 `docker-compose up -d` 重启服务。
4.  **查看日志**: 使用 `docker-compose logs -f app` 可以实时查看服务运行日志，便于调试。
5.  **停止服务**: 使用 `docker-compose down` 可以停止并移除所有相关的容器和网络。
