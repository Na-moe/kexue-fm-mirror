# Kexue FM Blog Mirror - Claude Code Edition

使用 Claude Code Action 自动从科学松鼠会 (https://kexue.fm/) 爬取最新博客并翻译成英文的 GitHub Actions 工作流。

## 🌟 新特性

- 🤖 **完全由 Claude 驱动**: 无需 Python 脚本，所有工作都由 Claude Code Action 完成
- 🔄 **智能内容提取**: 利用 Claude 的理解能力，自动适应网站结构变化
- 📝 **高质量翻译**: 使用 Claude 进行专业的中英翻译
- ⚡ **零维护**: 无需更新爬虫代码，Claude 会自动处理网站变化

## 功能特性

- 🕷️ **智能爬取**: 使用 web-reader MCP 工具获取最新博客
- 🔄 **增量更新**: 只处理新增文章，避免重复工作
- 📁 **文件组织**:
  - `kexue_fm_zh_cn/`: 存储原始中文博客
  - `kexue_fm_en_us/`: 存储翻译后的英文博客
- ⏰ **定时任务**: 每8小时自动运行
- 🚀 **手动触发**: 支持 GitHub Actions 手动触发
- 📊 **详细报告**: 完整的处理摘要和统计

## 项目结构

```
kexue_fm_en_mirror_actions/
├── .github/workflows/
│   └── scrape-and-translate.yml       # GitHub Actions 工作流（Claude Code 版本）
├── kexue_fm_zh_cn/                    # 中文博客存储目录
├── kexue_fm_en_us/                    # 英文博客存储目录
├── tmp/                               # 临时文件目录
│   ├── latest_ids.md                  # 最新文章ID列表
│   └── missing_ids.md                 # 待处理文章ID列表
└── README.md                          # 项目说明
```

## 设置步骤

### 1. 配置 GitHub Secrets

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加：

- `ANTHROPIC_API_KEY`: 你的 Anthropic API 密钥

### 2. 启用 GitHub Actions

- 确保仓库的 Actions 功能已启用
- 工作流会在每8小时自动运行
- 也可以通过 Actions 页面手动触发

## 工作原理

### 自动化流程

1. **获取文章列表**:
   - Claude 使用 web-reader MCP 工具访问 https://kexue.fm/
   - 提取最新20篇文章的ID
   - 保存到 `tmp/latest_ids.md`

2. **检查新增文章**:
   - 对比已有文件，识别缺失的文章
   - 生成待处理列表 `tmp/missing_ids.md`

3. **爬取文章内容**:
   - 访问 https://kexue.fm/archives/{id}
   - 提取并保存文章到 `kexue_fm_zh_cn/{id}.md`

4. **翻译成英文**:
   - Claude 将中文文章翻译成专业英文
   - 保持 markdown 格式和技术术语准确性
   - 保存到 `kexue_fm_en_us/{id}.md`

### 文件格式

#### 中文文件格式
```markdown
# 文章标题

**原文链接**: https://kexue.fm/archives/12345
**爬取时间**: 2025-12-05 20:11:00

---

文章正文内容...
```

#### 英文文件格式
```markdown
# (Translated from Chinese)

**Original ID**: 12345
**Original URL**: https://kexue.fm/archives/12345
**Translation Date**: 2025-12-05 20:11:00

---

Translated article content...
```

## 本地运行

虽然这个项目设计为在 GitHub Actions 中运行，但你也可以使用 Claude Code 本地运行：

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/kexue_fm_en_mirror_actions.git
cd kexue_fm_en_mirror_actions

# 2. 配置环境变量
export ANTHROPIC_API_KEY=your_api_key

# 3. 使用 Claude Code 执行提示词
# 参考 .github/workflows/scrape-and-translate.yml 中的各个步骤
```

## 优势对比

### 旧方案（Python脚本）
- ❌ 需要维护复杂的爬虫代码
- ❌ 网站结构变化会导致爬虫失效
- ❌ 翻译质量依赖第三方服务
- ❌ 需要管理依赖和环境

### 新方案（Claude Code）
- ✅ 无需编程，Claude 自动处理
- ✅ 智能适应网站结构变化
- ✅ 高质量的 Claude 翻译
- ✅ 零依赖，零维护

## 注意事项

1. **API 成本**: 使用 Anthropic API 会产生费用，请控制使用频率
2. **爬取礼貌**: 工作流已配置合理的运行间隔，避免对目标网站造成压力
3. **翻译质量**: Claude 的翻译质量很高，但建议重要内容人工校对
4. **存储空间**: 长期运行会积累大量文章，注意仓库大小限制

## 故障排除

### 工作流不运行
- 确认 Actions 功能已启用
- 检查 `ANTHROPIC_API_KEY` 是否正确配置
- 查看 Actions 页面的运行日志

### 没有获取到文章
- 检查 https://kexue.fm/ 是否可正常访问
- 查看工作流日志中的错误信息
- 可能需要调整提示词以适应网站变化

### 翻译失败
- 确认 API 密钥有效且有足够额度
- 检查是否有网络连接问题
- 查看具体的错误日志

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License