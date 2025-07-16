# 贡献指南 / Contributing Guide

感谢您对 JsonTreeRAG 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

Thank you for your interest in the JsonTreeRAG project! We welcome all forms of contributions, including but not limited to:

## 🤝 贡献方式 / Ways to Contribute

### 🐛 报告问题 / Report Issues
- 发现 Bug？请提交 [Issue](https://github.com/oidahdsah0/JsonTreeRAG/issues)
- Found a bug? Please submit an [Issue](https://github.com/oidahdsah0/JsonTreeRAG/issues)

### 💡 提出建议 / Suggest Improvements
- 有新功能想法？创建 Feature Request
- Have a feature idea? Create a Feature Request

### 📝 改进文档 / Improve Documentation
- 修复文档错误或添加示例
- Fix documentation errors or add examples

### 🔧 提交代码 / Submit Code
- 修复Bug、添加功能或优化性能
- Fix bugs, add features, or optimize performance

## 🚀 开发流程 / Development Process

### 1. 准备环境 / Environment Setup

```bash
# Fork 项目并克隆到本地
git clone https://github.com/YOUR_USERNAME/JsonTreeRAG.git
cd JsonTreeRAG

# 安装依赖
pip install -r requirements.txt

# 创建开发分支
git checkout -b feature/your-feature-name
```

### 2. 开发与测试 / Development & Testing

```bash
# 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 21145

# 运行测试（如果有）
pytest tests/

# 检查代码格式
black app/ scripts/
flake8 app/ scripts/
```

### 3. 提交代码 / Submit Code

```bash
# 提交更改
git add .
git commit -m "feat: add amazing feature"

# 推送到你的Fork
git push origin feature/your-feature-name

# 创建 Pull Request
```

## 📋 代码规范 / Code Standards

### Python 代码风格 / Python Code Style

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 风格指南
- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 使用 [flake8](https://flake8.pycqa.org/) 进行代码检查

### 提交信息规范 / Commit Message Convention

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
type(scope): description

Types:
- feat: 新功能 / new feature
- fix: 修复Bug / bug fix
- docs: 文档更改 / documentation changes
- style: 代码格式 / code style changes
- refactor: 重构 / refactoring
- test: 测试相关 / test-related
- chore: 构建/工具链 / build/toolchain
```

示例 / Examples:
```
feat(api): add streaming response support
fix(retrieval): resolve multi-root node path issue
docs(readme): update installation instructions
```

## 🔍 Pull Request 指南 / Pull Request Guidelines

### 提交前检查 / Pre-submission Checklist

- [ ] 代码遵循项目风格规范
- [ ] 已添加必要的测试
- [ ] 所有测试通过
- [ ] 文档已更新（如果需要）
- [ ] 提交信息符合规范

### PR 描述模板 / PR Description Template

```markdown
## 📝 变更描述 / Change Description

简要描述本次变更的内容和原因。
Brief description of the changes and reasons.

## 🔧 变更类型 / Type of Change

- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📝 Documentation update
- [ ] 🔧 Code refactoring
- [ ] ⚡ Performance improvement

## 🧪 测试 / Testing

描述如何测试这些变更。
Describe how to test these changes.

## 📸 截图 / Screenshots

如果适用，请添加截图来说明变更。
If applicable, add screenshots to demonstrate changes.

## 📋 检查清单 / Checklist

- [ ] 代码遵循项目风格规范
- [ ] 自我审查代码
- [ ] 添加了必要的注释
- [ ] 相关文档已更新
- [ ] 变更不会破坏现有功能
```

## 🏷️ 标签系统 / Label System

我们使用以下标签来分类Issue和PR：

- `bug` - 程序错误
- `enhancement` - 功能增强
- `documentation` - 文档相关
- `good first issue` - 适合新手的问题
- `help wanted` - 需要帮助
- `question` - 疑问讨论

## 🎯 开发重点 / Development Focus

当前我们特别欢迎以下方面的贡献：

Currently, we especially welcome contributions in the following areas:

### 🔥 高优先级 / High Priority
- 性能优化 / Performance optimization
- 错误处理改进 / Error handling improvements
- 测试覆盖率提升 / Test coverage improvements
- 文档完善 / Documentation improvements

### 🚀 新功能 / New Features
- 支持更多向量数据库 / Support for more vector databases
- 增强的缓存机制 / Enhanced caching mechanisms
- 监控和日志功能 / Monitoring and logging features
- 多语言支持 / Multi-language support

### 🐛 已知问题 / Known Issues
- 查看 [Issues](https://github.com/oidahdsah0/JsonTreeRAG/issues) 获取当前问题列表
- Check [Issues](https://github.com/oidahdsah0/JsonTreeRAG/issues) for current issue list

## 📞 联系我们 / Contact Us

如果您在贡献过程中遇到任何问题，请随时联系我们：

If you encounter any issues during the contribution process, please feel free to contact us:

- 📧 创建 Issue: [GitHub Issues](https://github.com/oidahdsah0/JsonTreeRAG/issues)
- 💬 讨论区: [GitHub Discussions](https://github.com/oidahdsah0/JsonTreeRAG/discussions)

## 🙏 致谢 / Acknowledgments

感谢所有为 JsonTreeRAG 项目做出贡献的开发者！

Thanks to all developers who contribute to the JsonTreeRAG project!

## 📜 行为准则 / Code of Conduct

请注意，本项目采用贡献者公约。参与此项目即表示您同意遵守其条款。

Please note that this project is governed by the Contributor Covenant. By participating in this project, you agree to abide by its terms.

---

💡 **记住：没有贡献太小，每个改进都有价值！**  
💡 **Remember: No contribution is too small, every improvement has value!**
