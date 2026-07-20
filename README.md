# MCN商单脚本生成助手 - AI Agent解决方案

> 基于AI Agent的MCN小红书商单脚本自动化生成工具，支持博主风格模仿、合规质检、飞书文档自动交付

## 📋 项目概述

本项目是AI Agent解决方案实习生实操测试题的完整实现，围绕轻食酸奶「轻醒」品牌的小红书投放需求，构建了一套从博主调研到脚本生成再到飞书交付的全流程AI工作流。

### 核心能力
- ✅ 10位小红书博主全量调研与最优选择
- ✅ 5步Agent工作流（Brief拆解→风格分析→脚本生成→风险质检→飞书写入）
- ✅ 博主风格精准模仿，自然种草不硬广
- ✅ 自动化合规风险质检
- ✅ 飞书文档API自动化写入
- ✅ 可复用Skill沉淀

## 🛠️ 使用的AI工具

### 1. Codex — 辅助编程与脚本开发
- 辅助编写和调试 `lark_doc_writer.py` 飞书文档自动写入脚本
- 辅助 Git 版本管理与项目文件结构搭建
- 辅助文档内容校验与一致性检查

### 2. Gemini — 辅助创意与脚本拆解
- 辅助解析客户 brief，提取品牌、产品、卖点、人群等核心信息
- 辅助分析博主 @静香 的内容风格、语言特点与视觉公式
- 辅助构思 40 秒短视频脚本框架与分镜设计

## 🚀 运行方式

### 环境要求
- Python 3.8+
- 飞书开发者账号（用于文档写入）

### 快速开始

#### 1. 克隆项目
```bash
git clone https://github.com/bearzhang010101/xiaohongshu-script-assistant.git
cd mcn-script-assistant
```

#### 2. 安装依赖
```bash
pip install requests
```

#### 3. 配置飞书凭证（可选，用于真实API调用）
```bash
export LARK_APP_ID="your_app_id"
export LARK_APP_SECRET="your_app_secret"
```

> 💡 如果不配置凭证，脚本将以**模拟模式**运行，展示完整流程但不实际调用API

#### 4. 运行飞书文档写入
```bash
python scripts/lark_doc_writer.py \
  --input docs/03-短视频脚本与分镜.md \
  --title "轻醒希腊酸奶x静香 - 种草短视频脚本"
```

#### 5. 查看结果
运行成功后会输出：
- 文档ID
- 飞书文档链接
- 结果JSON文件（保存在docs/lark_doc_result.json）

## 📄 飞书接入方式

### 前置准备
1. 前往[飞书开放平台](https://open.feishu.cn/)创建企业自建应用
2. 开通「文档」相关权限（docx:document:create、docx:document:write）
3. 获取 App ID 和 App Secret
4. 将应用添加到目标企业并发布
5. 生成文档后，在飞书中将文档权限设为「组织内可阅读」或「所有人可阅读」

### API接入流程

```
1. 获取tenant_access_token
   POST /auth/v3/tenant_access_token/internal
   Body: { app_id, app_secret }

2. 创建空白文档
   POST /docx/v1/documents
   Header: Authorization: Bearer {token}
   Body: { title: "文档标题" }

3. 写入内容块
   POST /docx/v1/documents/{document_id}/blocks/{block_id}/children
   Header: Authorization: Bearer {token}
   Body: { children: [block1, block2, ...] }

4. 返回文档链接
   https://feishu.cn/docx/{document_id}
```

### 代码示例
```python
import os
from scripts.lark_doc_writer import LarkDocWriter

writer = LarkDocWriter(app_id=os.getenv("LARK_APP_ID"), app_secret=os.getenv("LARK_APP_SECRET"))
result = writer.write_script_to_doc(
    script_content="# 脚本内容...",
    title="文档标题"
)
print(result["url"])  # 飞书文档链接
```

## 🔗 最终飞书文档链接

### 文档链接
> **飞书文档**：https://feishu.cn/docx/Ms8QdBIG6oqyPqxFud7czjpdntg

### 自行部署说明
配置真实的飞书应用凭证后，运行脚本即可生成真实可访问的飞书文档链接。**注意：生成后请在飞书中将文档权限设为「组织内可阅读」或「所有人可阅读」，确保审核人员可以访问。** 文档支持：
- 在线预览与编辑
- 团队协作共享
- 评论与版本历史
- 导出为PDF/Word

## 📁 仓库结构

```
mcn-script-assistant/
├── README.md                          # 项目说明文档
├── docs/                              # 交付文档
│   ├── 01-博主调研报告.md             # A. 10位博主全量调研报告
│   ├── 02-AI工作流设计.md             # B. AI工作流与Prompt设计
│   ├── 03-短视频脚本与分镜.md         # C. 最终脚本与分镜设计
│   └── lark_doc_result.json           # 飞书文档写入结果
├── scripts/                           # 自动化脚本
│   └── lark_doc_writer.py             # 飞书文档API写入脚本
└── skills/                            # 可复用Skill
    └── mcn-script-assistant/
        └── SKILL.md                   # Skill完整文档
```

## 📊 交付物清单

### A. 小红书博主调研报告
- ✅ 10位博主全量调研（主页链接、内容方向、粉丝画像、代表作品）
- ✅ 最优博主选择：@静香
- ✅ 选择理由与内容风格深度拆解
- 📍 位置：`docs/01-博主调研报告.md`

### B. AI工作流设计
- ✅ 5步Agent流程：Brief拆解→风格分析→脚本生成→风险质检→飞书写入
- ✅ 核心Prompt库（3套完整Prompt）
- ✅ 可复用Skill设计
- 📍 位置：`docs/02-AI工作流设计.md`

### C. 短视频脚本与分镜
- ✅ 基于@静香 风格创作，完整复刻"4段式高能自律视觉公式"
- ✅ 完整字幕文案（40秒）
- ✅ 12镜头分镜设计表
- ✅ 5层双重预埋植入法标注
- ✅ 合规风险检查清单
- ✅ 飞书文档自动化写入
- 📍 位置：`docs/03-短视频脚本与分镜.md`

### D. 可复用Skill
- ✅ Skill文档：适用场景、输入材料、执行步骤、输出格式、风险检查清单
- ✅ 标准路径：`skills/mcn-script-assistant/SKILL.md`
- 📍 位置：`skills/mcn-script-assistant/SKILL.md`

## ⚠️ 合规红线

本项目严格遵守以下合规要求：

❌ **禁止内容**
- 减肥、减脂、瘦身、减重等功效承诺
- 降糖、治病、疗效等医疗功效宣称
- "最"、"第一"、"100%"等绝对化用语
- 保健功能、疾病预防等违规表述
- 虚假夸大的效果描述

✅ **允许内容**
- 高蛋白、0蔗糖、饱腹感等客观属性
- 早餐、运动后、下午茶等场景描述
- 个人口感分享与体验描述
- 日常饮食搭配建议

## 🎯 最优博主选择

**@静香**

选择理由：
1. **人设匹配**："6am早起自律达人"，每天6点健身，天然创造早餐+运动后两大植入场景
2. **视觉公式**：提炼出"4段式高能自律视觉公式"——前3秒快闪→运动打卡→场景切换→美食收尾
3. **表达方式**："自嘲式自律"，用"慢慢来 坚持就是胜利""奖励早起的自己"替代说教式种草
4. **双重预埋法**：产品第1秒潜意识植入 + 第22秒功能植入，双层次触达
5. **商业价值**：11.95万赞藏，中腰部成长型博主，粉丝画像极其精准，性价比高

## 📝 Skill使用说明

完整Skill文档位于 `skills/mcn-script-assistant/SKILL.md`

### 核心能力
- Brief结构化拆解
- 博主风格画像分析
- 风格化脚本生成
- 多维度风险质检
- 飞书文档自动输出

### 适用场景
- MCN机构商单脚本快速产出
- 博主风格化内容批量生成
- 品牌种草视频脚本创作
- 内容合规性自动化质检

## 📅 版本信息

- **版本**：v1.0
- **完成日期**：2026-07-20
- **项目类型**：AI Agent解决方案实习生实操测试
