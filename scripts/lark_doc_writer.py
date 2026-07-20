#!/usr/bin/env python3
"""
飞书文档自动化写入脚本
用于将MCN商单脚本自动写入飞书文档，实现自动化交付

使用方法：

1. 设置环境变量 LARK_APP_ID 和 LARK_APP_SECRET
2. 运行 python lark_doc_writer.py --input <脚本文件路径>
3. 返回飞书文档链接

扩展：支持 Make/Webhook 自动化集成
配合 Make (Integromat) 等自动化平台使用：
1. AI生成脚本后输出JSON
2. Webhook推送至Make
3. Make调用飞书API自动创建文档
4. 全程无需手动操作
"""

import os
import sys
import json
import requests
import argparse
import re
from pathlib import Path


class LarkDocWriter:
    """飞书文档写入器"""

    def __init__(self, app_id=None, app_secret=None):
        self.app_id = app_id or os.getenv("LARK_APP_ID")
        self.app_secret = app_secret or os.getenv("LARK_APP_SECRET")
        self.tenant_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"

        if not self.app_id or not self.app_secret:
            print("警告：未设置飞书应用凭证，请设置 LARK_APP_ID 和 LARK_APP_SECRET 环境变量")
            print("将使用模拟模式运行，展示写入流程但不实际调用API")
            self.mock_mode = True
        else:
            self.mock_mode = False

    def get_tenant_access_token(self):
        """获取租户访问令牌"""
        if self.mock_mode:
            return "mock_token"

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.post(url, json=payload)
        data = response.json()

        if data.get("code") == 0:
            self.tenant_access_token = data["tenant_access_token"]
            return self.tenant_access_token
        else:
            raise Exception(f"获取token失败: {data}")

    def create_document(self, title):
        """创建新文档"""
        if self.mock_mode:
            return {
                "document_id": "mock_doc_123456",
                "url": "https://feishu.cn/docx/mock_doc_123456"
            }

        self.get_tenant_access_token()
        url = f"{self.base_url}/docx/v1/documents"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "title": title
        }
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if data.get("code") == 0:
            doc = data["data"]["document"]
            return {
                "document_id": doc["document_id"],
                "url": f"https://feishu.cn/docx/{doc['document_id']}"
            }
        else:
            raise Exception(f"创建文档失败: {data}")


    def _parse_inline_elements(self, text):
        elements = []
        pattern = r'(\*\*[^\*]+\*\*)'
        last = 0
        for m in re.finditer(pattern, text):
            if m.start() > last:
                elements.append({"text_run": {"content": text[last:m.start()]}})
            if m.group(1):
                elements.append({"text_run": {"content": m.group(1)[2:-2], "text_element_style": {"bold": True}}})
            elif m.group(2):
                elements.append({"text_run": {"content": m.group(2)[1:-1], "text_element_style": {"inline_code": True}}})
            last = m.end()
        if last < len(text):
            elements.append({"text_run": {"content": text[last:]}})
        return elements if elements else [{"text_run": {"content": text}}]

    def _build_divider_block(self):
        return {"block_type": 22, "divider": {}}

    def _build_heading_block(self, text, level=1):
        """构建标题块"""
        heading_map = {1: (3, "heading1"), 2: (4, "heading2"), 3: (5, "heading3")}
        btype, field = heading_map.get(level, (4, "heading2"))
        return {
            "block_type": btype,
            field: {
                "elements": self._parse_inline_elements(text),
                "style": {}
            }
        }

    def _build_text_block(self, text):
        """构建文本块"""
        return {
            "block_type": 2,
            "text": {
                "elements": self._parse_inline_elements(text),
                "style": {}
            }
        }

    def _build_table_block(self, headers, rows):
        """构建表格块"""
        # 飞书表格需要特殊处理，这里简化为文本形式
        table_text = "| " + " | ".join(headers) + " |\n"
        table_text += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        for row in rows:
            table_text += "| " + " | ".join(str(cell) for cell in row) + " |\n"
        return self._build_text_block(table_text)

    def _build_bullet_block(self, text):
        """构建无序列表块"""
        return {
            "block_type": 12,
            "bullet": {
                "elements": self._parse_inline_elements(text),
                "style": {}
            }
        }

    def write_script_to_doc(self, script_content, title="轻醒希腊酸奶 - 种草短视频脚本"):
        """
        将脚本内容写入飞书文档

        Args:
            script_content: 脚本内容（markdown格式字符串）
            title: 文档标题

        Returns:
            dict: 包含document_id和url的字典
        """
        print(f"正在创建飞书文档: {title}")

        # 创建文档
        doc_info = self.create_document(title)
        document_id = doc_info["document_id"]

        if self.mock_mode:
            print("[模拟模式] 文档创建成功")
            print(f"[模拟模式] 文档ID: {document_id}")
            print(f"[模拟模式] 正在写入内容...")
            print(f"[模拟模式] 内容长度: {len(script_content)} 字符")
            print(f"[模拟模式] 写入完成")
            return doc_info

        # 获取文档根block_id
        self.get_tenant_access_token()
        url = f"{self.base_url}/docx/v1/documents/{document_id}/blocks/{document_id}/children"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        # 解析markdown内容，构建blocks
        blocks = self._parse_markdown_to_blocks(script_content)

        # 分批写入（飞书API限制每次最多100个block）
        batch_size = 50
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            payload = {
                "children": batch,
                "index": i
            }
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()

            if data.get("code") != 0:
                print(f"警告：第{i}批block写入可能有问题: {data}")

        print(f"文档写入完成，共写入 {len(blocks)} 个内容块")
        return doc_info

    def _parse_markdown_to_blocks(self, markdown_text):
        """markdown解析，转换为飞书block格式，保留行内格式、分隔线、代码块"""
        blocks = []
        lines = markdown_text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()
            
            if not line:
                i += 1
                continue

            # 分隔线
            if line.strip() == '---' or line.strip() == '***':
                blocks.append(self._build_divider_block())
                i += 1
                continue

            # 代码块
            if line.startswith('`'):
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].rstrip().startswith('`'):
                    code_lines.append(lines[i].rstrip())
                    i += 1
                if code_lines:
                    blocks.append(self._build_text_block('\n'.join(code_lines)))
                i += 1
                continue

            # 标题
            if line.startswith('# '):
                blocks.append(self._build_heading_block(line[2:], level=1))
            elif line.startswith('## '):
                blocks.append(self._build_heading_block(line[3:], level=2))
            elif line.startswith('### '):
                blocks.append(self._build_heading_block(line[4:], level=3))
            # 表格
            elif line.startswith('|'):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i].strip())
                    i += 1
                if len(table_lines) >= 2:
                    headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
                    rows = [[c.strip() for c in r.split('|')[1:-1]] for r in table_lines[2:]]
                    blocks.append(self._build_table_block(headers, rows))
                elif table_lines:
                    blocks.append(self._build_text_block(table_lines[0]))
                continue
            # 无序列表
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append(self._build_bullet_block(line[2:]))
            # 普通文本
            else:
                blocks.append(self._build_text_block(line))

            i += 1

        return blocks


def read_script_file(file_path):
    """读取脚本文件"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"脚本文件不存在: {file_path}")
    return path.read_text(encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='飞书文档自动化写入工具')
    parser.add_argument('--input', '-i', required=True, help='脚本文件路径（markdown格式）')
    parser.add_argument('--title', '-t', default='MCN商单短视频脚本', help='文档标题')
    parser.add_argument('--app-id', help='飞书应用ID（也可通过环境变量LARK_APP_ID设置）')
    parser.add_argument('--app-secret', help='飞书应用密钥（也可通过环境变量LARK_APP_SECRET设置）')

    args = parser.parse_args()

    # 读取脚本内容
    try:
        script_content = read_script_file(args.input)
        print(f"成功读取脚本文件: {args.input}")
        print(f"内容长度: {len(script_content)} 字符")
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)

    # 初始化写入器
    writer = LarkDocWriter(app_id=args.app_id, app_secret=args.app_secret)

    # 写入文档
    try:
        result = writer.write_script_to_doc(script_content, title=args.title)

        print("\n" + "="*50)
        print("飞书文档创建成功！")
        print(f"文档ID: {result['document_id']}")
        print(f"文档链接: {result['url']}")
        print("="*50)

        # 保存结果到JSON文件
        output_file = Path(args.input).parent / "lark_doc_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {output_file}")

    except Exception as e:
        print(f"写入文档失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


