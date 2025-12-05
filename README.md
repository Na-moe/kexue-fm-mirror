# Kexue FM Blog Mirror

自动从科学松鼠会 (https://kexue.fm/) 爬取最新博客并翻译成英文的 GitHub Actions 工作流。

## 功能特性

- 🕷️ **自动爬取**: 定时从科学松鼠会网站爬取最新博客文章
- 🔄 **自动翻译**: 使用 claude-code-actions 将中文博客翻译成英文
- 📁 **文件组织**:
  - `kexue_fm_zh_cn/`: 存储原始中文博客
  - `kexue_fm_en_us/`: 存储翻译后的英文博客
- ⏰ **定时任务**: 每天 UTC 10:00 (北京时间 18:00) 自动运行
- 🚀 **手动触发**: 支持 GitHub Actions 手动触发
- 📝 **详细日志**: 完整的爬取和翻译日志记录

## 项目结构

```
kexue_fm_en_mirror_actions/
├── .github/workflows/
│   └── scrape-and-translate.yml    # GitHub Actions 工作流配置
├── kexue_fm_zh_cn/                # 中文博客存储目录
├── kexue_fm_en_us/                # 英文博客存储目录
├── scrape_kexue.py               # 博客爬取脚本
├── translate_posts.py            # claude-code-actions 翻译脚本
├── translate_with_github_api.py  # GitHub API 备用翻译脚本
├── requirements.txt              # Python 依赖
└── README.md                     # 项目说明
```

## 设置步骤

### 1. Fork 或克隆此仓库

```bash
git clone https://github.com/your-username/kexue_fm_en_mirror_actions.git
cd kexue_fm_en_mirror_actions
```

### 2. 配置 Secrets (可选)

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加：

- `ANTHROPIC_API_KEY`: Anthropic API 密钥（用于 claude-code-actions）
- `GITHUB_TOKEN`: GitHub token（用于备用翻译方案，通常会自动提供）

### 3. 启用 GitHub Actions

- 确保仓库的 Actions 功能已启用
- 工作流会在每日 UTC 10:00 自动运行
- 也可以通过 Actions 页面手动触发

## 工作流程

1. **爬取阶段**:
   - 从 https://kexue.fm/ 获取最新文章列表
   - 逐个爬取文章内容
   - 保存为 Markdown 文件到 `kexue_fm_zh_cn/` 目录
   - 使用 `scraped_posts.json` 记录已爬取的文章

2. **翻译阶段**:
   - 检测新增的中文文章
   - 使用 claude-code-actions 进行翻译
   - 如果翻译失败，使用 GitHub API 作为备用方案
   - 保存翻译结果到 `kexue_fm_en_us/` 目录

3. **提交阶段**:
   - 自动提交所有更改到仓库
   - 生成运行摘要报告

## 文件命名规则

文章文件以文章ID命名：`{blog_id}.md`

例如：
- `12345.md` (中文原文)
- `12345.md` (英文翻译，在 `kexue_fm_en_us/` 目录下)

## 本地运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 安装 claude-code-actions

```bash
npm install -g @anthropic-ai/claude-code-actions
```

### 运行爬虫

```bash
python scrape_kexue.py
```

### 运行翻译

```bash
python translate_posts.py
```

## 注意事项

1. **访问频率**: 爬虫设置了2秒的延迟，避免对目标网站造成过大压力
2. **翻译质量**: 自动翻译可能存在误差，建议人工校对重要内容
3. **存储空间**: 长期运行会积累大量文章，注意仓库大小限制
4. **版权**: 请遵守目标网站的版权政策和使用条款

## 故障排除

### 爬取失败
- 检查网络连接
- 确认 https://kexue.fm/ 网站可正常访问
- 查看日志了解具体错误

### 翻译失败
- 确认 API 密钥配置正确
- 检查 claude-code-actions 是否正确安装
- 查看翻译脚本的错误日志

### GitHub Actions 不运行
- 确认 Actions 功能已启用
- 检查工作流文件语法是否正确
- 查看 Actions 页面的运行日志

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License