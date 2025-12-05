import requests
from bs4 import BeautifulSoup
import os
import re
import time
import json
from datetime import datetime
import markdown
from urllib.parse import urljoin, urlparse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KexueScraper:
    def __init__(self):
        self.base_url = "https://kexue.fm"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.posts_dir = "kexue_fm_zh_cn"
        self.metadata_file = "scraped_posts.json"

    def get_post_list(self):
        """获取博客文章列表"""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            posts = []
            # 查找文章链接 - 根据网站结构调整选择器
            articles = soup.find_all('article') or soup.find_all('div', class_='post') or soup.find_all('h2')

            for article in articles[:20]:  # 获取最新的20篇文章
                link = article.find('a', href=True)
                if link:
                    href = link['href']
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)

                    title = link.get_text(strip=True)
                    posts.append({
                        'url': href,
                        'title': title
                    })

            return posts
        except Exception as e:
            logger.error(f"获取文章列表失败: {e}")
            return []

    def extract_post_id(self, url):
        """从URL中提取文章ID"""
        # 尝试从URL中提取ID，通常是数字部分
        match = re.search(r'(\d+)', url)
        return match.group(1) if match else url.split('/')[-1]

    def scrape_post(self, post_url):
        """爬取单篇文章"""
        try:
            logger.info(f"正在爬取: {post_url}")
            response = self.session.get(post_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题
            title = soup.find('h1') or soup.find('h2')
            title = title.get_text(strip=True) if title else "无标题"

            # 提取发布日期
            date_elem = soup.find('time') or soup.find('span', class_='date') or soup.find('div', class_='post-date')
            date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')

            # 提取正文
            content = ""
            # 尝试多个可能的内容选择器
            content_selectors = [
                'div.post-content',
                'div.entry-content',
                'div.article-content',
                'div.content',
                'article',
                'main'
            ]

            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = str(content_elem)
                    break

            # 如果没有找到内容区域，尝试获取整个body
            if not content:
                body = soup.find('body')
                content = str(body) if body else ""

            # 清理HTML
            content = self.clean_html(content)

            # 生成markdown
            markdown_content = f"""# {title}

**原文链接**: {post_url}
**发布日期**: {date}
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}
"""

            return title, markdown_content

        except Exception as e:
            logger.error(f"爬取文章失败 {post_url}: {e}")
            return None, None

    def clean_html(self, html_content):
        """清理HTML内容"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除不需要的标签
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            tag.decompose()

        # 移除广告和其他不需要的内容
        for ad in soup.find_all(class_=re.compile(r'ad|advertisement|banner')):
            ad.decompose()

        # 转换为markdown
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0

        markdown = h.handle(str(soup))

        return markdown.strip()

    def load_scraped_posts(self):
        """加载已爬取的文章记录"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_scraped_post(self, post_id, title, url):
        """保存已爬取的文章记录"""
        scraped = self.load_scraped_posts()
        scraped.append({
            'id': post_id,
            'title': title,
            'url': url,
            'scraped_at': datetime.now().isoformat()
        })

        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(scraped, f, ensure_ascii=False, indent=2)

    def is_already_scraped(self, post_id):
        """检查文章是否已经爬取"""
        scraped = self.load_scraped_posts()
        return any(post['id'] == post_id for post in scraped)

    def run(self):
        """运行爬虫"""
        logger.info("开始爬取科学松鼠会博客...")

        # 创建输出目录
        os.makedirs(self.posts_dir, exist_ok=True)

        # 获取文章列表
        posts = self.get_post_list()
        logger.info(f"找到 {len(posts)} 篇文章")

        new_posts_count = 0

        for post in posts:
            post_url = post['url']
            post_id = self.extract_post_id(post_url)

            # 检查是否已经爬取过
            if self.is_already_scraped(post_id):
                logger.info(f"文章 {post_id} 已存在，跳过")
                continue

            # 爬取文章内容
            title, content = self.scrape_post(post_url)

            if title and content:
                # 保存为markdown文件
                filename = f"{post_id}.md"
                filepath = os.path.join(self.posts_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

                # 记录已爬取
                self.save_scraped_post(post_id, title, post_url)

                logger.info(f"成功保存文章: {filename}")
                new_posts_count += 1

                # 添加延迟避免过于频繁的请求
                time.sleep(2)

        logger.info(f"爬取完成！新增 {new_posts_count} 篇文章")
        return new_posts_count

if __name__ == "__main__":
    scraper = KexueScraper()
    scraper.run()