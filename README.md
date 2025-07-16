# JsonTreeRAG 🌳

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Stars](https://img.shields.io/github/stars/oidahdsah0/JsonTreeRAG?style=social)](https://github.com/oidahdsah0/JsonTreeRAG/stargazers)

> 🚀 **A JSON-based Tree RAG (Retrieval-Augmented Generation) system for private knowledge base Q&A**

基于本地私有知识库的RAG问答系统，专为层级化JSON格式知识库设计，通过向量化检索与上下文子树提取，为本地大语言模型提供精准的背景知识。

[English](#english-version) | [中文文档](#中文文档)

## ✨ 核心特性

🔒 **私有化部署** - 所有组件均可本地部署，确保数据安全  
🌳 **层级知识库** - 专为树状JSON结构优化，支持精准路径定位  
🔌 **OpenAI兼容** - 标准API接口，支持流式响应  
🐳 **容器化部署** - Docker一键启动，简化部署流程  
⚙️ **高度可配置** - 灵活的配置管理，支持多种LLM服务  

## 🚀 快速开始

### 一键启动

```bash
# 1. 克隆项目
git clone https://github.com/oidahdsah0/JsonTreeRAG.git
cd JsonTreeRAG

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置你的API端点和密钥

# 3. 启动服务
docker-compose up -d

# 4. 索引知识库
docker-compose run --rm app python scripts/data_indexer.py
```

### 测试API

```bash
curl -N -X POST http://localhost:21145/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "messages": [{"role": "user", "content": "请介绍一下AIGC技术"}],
    "stream": true
  }'
```

## 📋 系统要求

- Docker & Docker Compose
- Python 3.8+ (开发环境)
- 本地LLM服务 (如 vLLM)
- 本地Embedding服务

## 🏗️ 架构设计

```
用户查询 → FastAPI → 检索服务 → Embedding & ChromaDB → 上下文提取 → LLM → 流式响应
```

### 核心组件

- **FastAPI应用** - REST API服务
- **ChromaDB** - 向量数据库
- **检索服务** - 语义搜索与上下文提取
- **LLM处理器** - 大语言模型接口

## 📖 详细文档

### 环境配置

| 环境变量 | 描述 | 示例 |
|---------|------|------|
| `EMBEDDING_API_BASE_URL` | Embedding服务地址 | `http://localhost:8000` |
| `EMBEDDING_MODEL` | Embedding模型名称 | `text-embedding-3-small` |
| `LLM_API_BASE_URL` | LLM服务地址 | `http://localhost:8001` |
| `LLM_MODEL` | LLM模型名称 | `Qwen3-32B` |

### 知识库格式

系统支持层级化JSON格式的知识库：

```json
{
  "01": {
    "name": "技术概述",
    "content": "技术内容...",
    "children": {
      "01": {
        "name": "子章节",
        "content": "详细内容..."
      }
    }
  }
}
```

### API接口

#### POST `/v1/chat/completions`

OpenAI兼容的聊天完成接口，支持流式和非流式响应。

**请求参数：**
- `model` - 模型名称
- `messages` - 消息数组
- `stream` - 是否流式响应（可选）

## 🔧 开发指南

### 本地开发

```bash
# 克隆项目
git clone https://github.com/oidahdsah0/JsonTreeRAG.git
cd JsonTreeRAG

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 21145
```

### 项目结构

```
JsonTreeRAG/
├── app/                    # FastAPI应用
│   ├── main.py            # API入口
│   ├── services/          # 业务逻辑
│   └── core/              # 核心配置
├── scripts/               # 工具脚本
├── data/                  # 知识库数据
├── docker-compose.yml     # Docker编排
└── requirements.txt       # Python依赖
```

## 📈 版本历史

### v1.1.0 (2025-06-30) 🎉

- ✅ 修复多根节点路径查找Bug
- ⭐ 改善流式传输效果
- 🔧 增强缓存管理功能
- 📝 添加详细调试日志

### v1.0.0 (2025-06-01)

- 🎯 首个正式版本发布
- 🔌 OpenAI兼容API
- 🐳 Docker容器化部署
- 🌳 层级知识库支持

## 🤝 贡献指南

我们欢迎各种形式的贡献！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🌟 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Web框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [OpenAI](https://openai.com/) - API标准参考

## 📞 联系方式

- GitHub: [@oidahdsah0](https://github.com/oidahdsah0)
- Issues: [GitHub Issues](https://github.com/oidahdsah0/JsonTreeRAG/issues)

---

# English Version

## JsonTreeRAG 🌳

> 🚀 **A Private Knowledge Base RAG Q&A System Based on Hierarchical JSON Structure**

A retrieval-augmented generation system designed for hierarchical JSON knowledge bases, providing precise context extraction through vectorized retrieval and tree-based context building for local Large Language Models.

## ✨ Key Features

🔒 **Private Deployment** - All components can be deployed locally for data security  
🌳 **Hierarchical Knowledge Base** - Optimized for tree-structured JSON with precise path positioning  
🔌 **OpenAI Compatible** - Standard API interface with streaming support  
🐳 **Containerized Deployment** - One-click Docker deployment  
⚙️ **Highly Configurable** - Flexible configuration management supporting various LLM services  

## 🚀 Quick Start

### One-Click Launch

```bash
# 1. Clone the project
git clone https://github.com/oidahdsah0/JsonTreeRAG.git
cd JsonTreeRAG

# 2. Configure environment variables
cp .env.example .env
# Edit .env file to configure your API endpoints and keys

# 3. Start services
docker-compose up -d

# 4. Index knowledge base
docker-compose run --rm app python scripts/data_indexer.py
```

### Test API

```bash
curl -N -X POST http://localhost:21145/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "messages": [{"role": "user", "content": "Tell me about AIGC technology"}],
    "stream": true
  }'
```

## 📋 System Requirements

- Docker & Docker Compose
- Python 3.8+ (development environment)
- Local LLM service (e.g., vLLM)
- Local Embedding service

## 🏗️ Architecture

```
User Query → FastAPI → Retrieval Service → Embedding & ChromaDB → Context Extraction → LLM → Streaming Response
```

### Core Components

- **FastAPI Application** - REST API service
- **ChromaDB** - Vector database
- **Retrieval Service** - Semantic search and context extraction
- **LLM Handler** - Large Language Model interface

## 📖 Documentation

### Environment Configuration

| Environment Variable | Description | Example |
|---------------------|-------------|---------|
| `EMBEDDING_API_BASE_URL` | Embedding service URL | `http://localhost:8000` |
| `EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `LLM_API_BASE_URL` | LLM service URL | `http://localhost:8001` |
| `LLM_MODEL` | LLM model name | `Qwen3-32B` |

### Knowledge Base Format

The system supports hierarchical JSON knowledge bases:

```json
{
  "01": {
    "name": "Technical Overview",
    "content": "Technical content...",
    "children": {
      "01": {
        "name": "Sub-section",
        "content": "Detailed content..."
      }
    }
  }
}
```

### API Interface

#### POST `/v1/chat/completions`

OpenAI-compatible chat completion interface supporting both streaming and non-streaming responses.

**Request Parameters:**
- `model` - Model name
- `messages` - Message array
- `stream` - Whether to use streaming response (optional)

## 🔧 Development Guide

### Local Development

```bash
# Clone the project
git clone https://github.com/oidahdsah0/JsonTreeRAG.git
cd JsonTreeRAG

# Install dependencies
pip install -r requirements.txt

# Start development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 21145
```

### Project Structure

```
JsonTreeRAG/
├── app/                    # FastAPI application
│   ├── main.py            # API entry point
│   ├── services/          # Business logic
│   └── core/              # Core configuration
├── scripts/               # Utility scripts
├── data/                  # Knowledge base data
├── docker-compose.yml     # Docker orchestration
└── requirements.txt       # Python dependencies
```

## 📈 Version History

### v1.1.0 (2025-06-30) 🎉

- ✅ Fixed multi-root node path finding bug
- ⭐ Improved streaming transmission effect
- 🔧 Enhanced cache management functionality
- 📝 Added detailed debug logging

### v1.0.0 (2025-06-01)

- 🎯 First official release
- 🔌 OpenAI-compatible API
- 🐳 Docker containerized deployment
- 🌳 Hierarchical knowledge base support

## 🤝 Contributing

We welcome all forms of contributions!

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI](https://openai.com/) - API standard reference

## 📞 Contact

- GitHub: [@oidahdsah0](https://github.com/oidahdsah0)
- Issues: [GitHub Issues](https://github.com/oidahdsah0/JsonTreeRAG/issues)

---

⭐ **如果这个项目对你有帮助，请给我们一个星标！**  
⭐ **If this project helps you, please give us a star!**
