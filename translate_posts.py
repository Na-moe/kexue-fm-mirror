import os
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostTranslator:
    def __init__(self):
        self.source_dir = Path("kexue_fm_zh_cn")
        self.target_dir = Path("kexue_fm_en_us")
        self.metadata_file = "translated_posts.json"

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

    def translate_post(self, post_id):
        """使用 claude-code-actions 翻译文章"""
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

        # 构建翻译提示
        translation_prompt = f"""请将以下中文博客文章翻译成英文。要求：
1. 保持原文的格式和结构
2. 准确翻译技术术语和科学概念
3. 保持原文的语气和风格
4. Markdown 格式保持不变
5. 保留所有链接和图片引用
6. 在开头添加翻译说明

原文内容：
{original_content}

翻译要求：
- 只返回翻译后的英文内容
- 不要包含任何解释性文字
- 保持专业的科学写作风格"""

        # 使用 claude-code-actions 进行翻译
        try:
            logger.info(f"正在翻译文章: {post_id}")

            # 构建命令
            cmd = [
                'claude-code-actions',
                '--input', source_file,
                '--output', target_file,
                '--prompt', translation_prompt
            ]

            # 执行翻译
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if result.returncode == 0:
                logger.info(f"成功翻译文章: {post_id}")

                # 验证输出文件
                if target_file.exists():
                    # 读取翻译结果并添加元数据
                    with open(target_file, 'r', encoding='utf-8') as f:
                        translated_content = f.read()

                    # 添加翻译元数据
                    header = f"""# (Translated)

**Original ID**: {post_id}
**Translation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Translation Service**: claude-code-actions

---

"""

                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(header + translated_content)

                    # 记录已翻译
                    self.save_translated_post(post_id)
                    return True
                else:
                    logger.error(f"翻译输出文件不存在: {target_file}")
                    return False
            else:
                logger.error(f"翻译失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"翻译文章 {post_id} 时出错: {e}")
            return False

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

        logger.info(f"翻译完成！成功翻译 {success_count} 篇文章")
        return success_count

if __name__ == "__main__":
    translator = PostTranslator()
    translator.translate_all()