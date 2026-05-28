# xuan-docx-to-wechat-html

将 `.docx` 文件转换为微信公众号兼容的 HTML 文件。

## 功能

- 按文档原始顺序提取正文、图片、图注
- 识别标题、元信息（机构、日期）、正文段落
- 图注与图片自动绑定，支持单图和双列宫格布局
- 自动判断推文类型：活动通知 / 活动简报
- 按推文类型读取平级 `manifest` 素材库，并在 HTML 中插入对应 PNG
- 输出微信兼容的 HTML 片段（内联样式，无外链 CSS/JS）
- 可选输出 `parsed.json` 供调试

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py --input /path/to/article.docx --output-dir /path/to/output
```

完整参数：

```
--input         必填，.docx 文件路径
--output-dir    可选，输出目录（默认：docx 同目录下的 output/）
--style         可选，渲染风格（默认：auto）
--article-type  可选，推文类型（默认：auto；支持 activity_notice / activity_briefing）
--asset-manifest 可选，PNG 素材库根 manifest.json（默认：xuan-skill 平级 manifest/manifest.json）
--debug         可选，输出 parsed.json 中间结构
--keep-original-text  可选，默认 true，保留原文措辞
```

## 输出

```
output/
  article_wechat.html   # 微信兼容 HTML 片段
  images/
    img_001.png
    img_002.jpg
    ...
  parsed.json           # debug 模式下输出
```

stdout 输出 JSON：

```json
{
  "status": "success",
  "output_html": "/path/to/output/article_wechat.html",
  "output_images_dir": "/path/to/output/images",
  "title": "活动标题",
  "summary_candidate": "首段正文摘要...",
  "first_image_candidate": "images/img_001.png",
  "images_count": 8,
  "captions_count": 5,
  "article_type": "activity_briefing",
  "style_name": "community_wechat_brief_style",
  "asset_library": {
    "manifest_path": "/path/to/manifest/manifest.json",
    "used_assets": []
  }
}
```

## MVP 边界与已知限制

| 场景 | 支持情况 |
|------|---------|
| 内嵌图片（inline）| ✅ 支持 |
| 浮动图片（text-wrap）| ❌ 不支持，跳过并警告 |
| 普通段落文本 | ✅ 支持 |
| 标题样式段落 | ✅ 支持 |
| 简单表格 | ⚠️ 渲染为纯文本行 |
| 文本框 / 形状 | ❌ 不支持，跳过 |
| 嵌套列表 | ⚠️ 展平为普通段落 |
| 自定义字体 | ❌ 忽略，使用系统字体 |
| 脚注 / 尾注 | ❌ 不支持 |
| 页眉 / 页脚 | ❌ 不支持 |

## 风格说明

默认 `--style auto`：

- `activity_briefing`：使用 `community_wechat_brief_style`，适合活动简报/回顾，浅暖色分块，图文交替，图注居中小字，文末有收束区。
- `activity_notice`：使用 `activity_notice_style`，适合活动通知/招募，突出时间、地点、对象、报名方式和截止提醒。通知稿常常没有图片，因此会优先使用素材库中的活动通知 PNG 做信息模块装饰。

素材库推荐与 skill 平级放置：

```
linshide/
  xuan-docx-to-wechat-html/
  manifest/
    manifest.json
    common/manifest.json
    activity_notice/manifest.json
    activity_briefing/manifest.json
```

渲染时只使用 `common` 和当前推文类型对应目录中的素材，不跨类型混用。所有样式均为内联写法，不使用 flex、grid、脚本、外链 CSS 或背景图。

## 依赖

- `python-docx` — docx 解析
- `lxml` — XML 处理
- `Pillow` — 图片格式识别（可选）
