---
name: xuan-docx-to-wechat-html
description: 将 .docx 文件解析并转换为微信公众号兼容的 HTML 文件，供后续发布 skill 使用
allowed-tools: Bash
---

# docx → 微信公众号 HTML 转换

将本地 Word 文档结构化解析，提取图片、识别图注，生成适合微信公众号正文的 HTML 文件。

## 使用前提

安装依赖（首次使用）：

```bash
pip install -r "$SKILL_DIR/requirements.txt"
```

## 执行步骤

1. 询问用户以下信息（如未在命令中提供）：
   - **docx 文件路径**：必填
   - **输出目录**：可选，默认为 docx 同目录下的 `output/`
   - **是否开启 debug**：可选，开启后额外输出 `parsed.json`

2. 确认后运行：

```bash
python "$SKILL_DIR/main.py" --input <docx文件路径> --output-dir <输出目录> --style community_wechat_brief_style
```

debug 模式：

```bash
python "$SKILL_DIR/main.py" --input <docx文件路径> --output-dir <输出目录> --debug
```

3. 脚本输出 JSON，包含以下字段：

| 字段 | 含义 |
|------|------|
| status | success / error |
| output_html | 生成的 HTML 文件路径 |
| output_images_dir | 提取的图片目录 |
| output_json | debug 模式下的结构 JSON 路径 |
| title | 识别出的文章标题 |
| summary_candidate | 首段正文摘要（≤120字） |
| first_image_candidate | 第一张图片的相对路径 |
| images_count | 提取图片数量 |
| captions_count | 识别图注数量 |

4. 告知用户输出文件路径，提示可用后续发布 skill 继续上传。

## 常见问题

| 问题 | 原因 | 建议 |
|------|------|------|
| images_count=0 | docx 中图片为浮动图片 | MVP 不支持浮动图片，需手动嵌入 |
| 图注识别为 0 | 图注文字过长或格式特殊 | 检查 parsed.json 中 caption_candidates |
| HTML 图片显示空白 | 图片路径未替换为线上 URL | 需后续发布 skill 上传图片并替换 src |
