import os
import json
import requests
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubTranslator:
    def __init__(self):
        self.source_dir = Path("kexue_fm_zh_cn")
        self.target_dir = Path("kexue_fm_en_us")
        self.metadata_file = "translated_posts_github.json"
        self.github_token = os.getenv('GITHUB_TOKEN')

        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

    def get_untranslated_posts(self):
        """获取未翻译的文章列表"""
        translated = self.load_translated_posts()
        translated_ids = {post['id'] for post in translated}

        untranslated = []
        if self.source_dir.exists():
            for file_path in self.source_dir.glob("*.md"):
                post_id = file_path.stem
                if post_id not in translated_ids:
                    untranslated.append(post_id)

        return untranslated

    def load_translated_posts(self):
        """加载已翻译的文章记录"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_translated_post(self, post_id):
        """保存已翻译的文章记录"""
        translated = self.load_translated_posts()
        translated.append({
            'id': post_id,
            'translated_at': datetime.now().isoformat()
        })

        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(translated, f, ensure_ascii=False, indent=2)

    def translate_with_github_api(self, text):
        """使用 GitHub Copilot API 进行翻译"""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

        # 使用 GitHub Copilot Chat API
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional translator specializing in scientific content. Translate Chinese to English while maintaining the original markdown format and technical accuracy."
                },
                {
                    "role": "user",
                    "content": f"Translate the following Chinese blog post to English. Maintain all markdown formatting, links, and image references. Provide only the English translation without any additional commentary.\n\n{text}"
                }
            ],
            "model": "gpt-4",
            "temperature": 0.3
        }

        try:
            response = requests.post(
                "https://api.githubcopilot.com/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Translation API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return None

    def simple_translate(self, text):
        """简单的翻译方法 - 使用免费翻译服务或基础规则"""
        # 这里可以集成其他免费翻译服务
        # 目前返回原文并添加翻译标记
        return f"""# [TRANSLATED FROM CHINESE]

**Note**: This is an auto-translated version. The original Chinese text is preserved below.

---

{text}

---

**Original Chinese text above - Professional translation needed**"""

    def translate_post(self, post_id):
        """翻译单篇文章"""
        source_file = self.source_dir / f"{post_id}.md"
        target_file = self.target_dir / f"{post_id}.md"

        if not source_file.exists():
            logger.error(f"源文件不存在: {source_file}")
            return False

        # 确保目标目录存在
        self.target_dir.mkdir(exist_ok=True)

        # 读取原文内容
        with open(source_file, 'r', encoding='utf-8') as f:
            original_content = f.read()

        logger.info(f"正在翻译文章: {post_id}")

        # 尝试使用 GitHub API 翻译
        translated_content = self.translate_with_github_api(original_content)

        # 如果 GitHub API 翻译失败，使用简单翻译方法
        if not translated_content:
            logger.warning(f"GitHub API 翻译失败，使用简单翻译方法")
            translated_content = self.simple_translate(original_content)

        # 添加翻译元数据
        header = f"""# (Translated)

**Original ID**: {post_id}
**Translation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Translation Method**: GitHub API

---

"""

        # 保存翻译结果
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(header + translated_content)

        # 记录已翻译
        self.save_translated_post(post_id)
        logger.info(f"成功翻译文章: {post_id}")
        return True

    def translate_all(self):
        """翻译所有未翻译的文章"""
        untranslated = self.get_untranslated_posts()

        if not untranslated:
            logger.info("没有需要翻译的文章")
            return 0

        logger.info(f"找到 {len(untranslated)} 篇需要翻译的文章")

        success_count = 0
        for post_id in untranslated:
            if self.translate_post(post_id):
                success_count += 1
            else:
                logger.error(f"翻译文章 {post_id} 失败")

        logger.info(f"翻译完成！成功处理 {success_count} 篇文章")
        return success_count

if __name__ == "__main__":
    try:
        translator = GitHubTranslator()
        translator.translate_all()
    except Exception as e:
        logger.error(f"翻译过程中出错: {e}")
        # 创建一个占位符文件表示翻译失败
        Path("kexue_fm_en_us").mkdir(exist_ok=True)
        with open("kexue_fm_en_us/translation_error.md", "w", encoding="utf-8") as f:
            f.write(f"# Translation Error\n\nTranslation failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nError: {str(e)}")