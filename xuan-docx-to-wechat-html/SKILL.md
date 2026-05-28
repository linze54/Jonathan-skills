---
name: xuan-docx-to-wechat-html
description: 将 .docx 文件解析并转换为微信公众号兼容的 HTML 文件，供后续发布 skill 使用
allowed-tools: Bash
---

# docx → 微信公众号 HTML 转换

将本地 Word 文档结构化解析，提取图片、识别图注，生成适合微信公众号正文的 HTML 文件。

## 推文类型与素材库规则

默认使用自动类型判断：

```text
读取原始材料
→ 提取关键信息
→ 判断推文类型：activity_notice / activity_briefing
→ 读取平级 manifest/manifest.json
→ 读取 common manifest + 对应类型 manifest
→ 按对应风格和本地 PNG 素材生成微信兼容 HTML
```

类型规则：

- `activity_notice`：活动通知/招募/报名类推文。重点突出时间、地点、对象、报名方式、截止时间。通知稿通常没有现场图片，因此应使用 `activity_notice` 素材库增加信息模块装饰。
- `activity_briefing`：活动简报/回顾/总结类推文。重点突出活动过程、现场图片、参与情况、成果和反馈。沿用社区活动简报风格。

素材库默认位置：

```text
<xuan-skill父目录>/manifest/manifest.json
```

只允许使用：

- `common` 通用素材
- 当前推文类型对应目录素材

不要跨类型混用素材。活动通知不要使用简报成果章，活动简报不要使用报名按钮，除非 manifest 明确允许。

所有 HTML 必须保持微信公众号兼容的原始写法：内联 style、普通 `section/div/table/p/img`，不使用 flex、grid、脚本、外链 CSS、复杂定位或背景图。

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
python "$SKILL_DIR/main.py" --input <docx文件路径> --output-dir <输出目录>
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
| title | 识别出的文档标题 |
| article_title | 推文标题（用于API发布） |
| author_info | 作者/机构信息 |
| summary_candidate | 首段正文摘要（≤120字） |
| first_image_candidate | 第一张图片的相对路径 |
| images_count | 提取图片数量 |
| captions_count | 识别图注数量 |

4. 告知用户输出文件路径，提示可用后续发布 skill 继续上传。

## 内容块类型与渲染规则

脚本将文档解析为以下内容块类型，渲染器根据类型决定是否输出到HTML正文：

| 块类型 | 说明 | 是否渲染到正文 |
|--------|------|----------------|
| title | 文档大标题 | ❌ 不渲染（通过API的title字段展示，避免重复） |
| meta | 元信息（机构名、日期、文档类型等） | ❌ 不渲染（通过API元数据字段传递） |
| preamble | 前言/副标题/项目名称（第一张图片之前的短标题） | ❌ 不渲染（与推文标题重复） |
| summary | 活动导语/总述段落 | ✅ 渲染（红色上下横线卡片样式） |
| body | 正文段落 | ✅ 渲染（白底卡片样式） |
| image | 单张图片 | ✅ 渲染 |
| gallery | 多图并排 | ✅ 渲染 |
| end | 文末收束 | ✅ 渲染 |

### 关键设计决策

1. **title/meta/preamble 不渲染到正文**：微信推文发布时，标题通过API的 `title` 字段传递，已经在推文顶部展示。如果正文中再次出现标题、副标题、项目名称等，会造成内容重复。因此这些块只用于提取元数据，不输出到HTML正文。

2. **preamble 识别规则**：在第一张图片出现之前，文档中的短文本（≤100字）heading 和 body 段落被归为 preamble。这些通常是项目名称、副标题、推文标题等，与API title字段重复。

3. **导语保留规则**：包含活动背景/目的/概述关键词（如"为深化"、"顺利开展"等）的长段落被识别为导语，保留在正文中渲染。

4. **长文本不归为meta**：即使包含日期+机构名，超过80字的段落不会被归为meta，避免将正文导语错误丢弃。

## 多模型协作工作流（2026-05-19 新增）

### 模型分工
- **默认主力**：DeepSeek（文字处理、逻辑推理、代码生成）
- **识图任务**：Qwen (`qwen/qwen3.5-plus`) — 支持 text+image 输入

### 使用场景
当用户发来推文预览截图并指出排版问题时：
1. 用 Qwen 识别截图中的问题（图注截断、图片错位、样式异常等）
2. 结合用户描述定位 HTML 源文件中的问题代码
3. 修正 HTML 并重新发布

### 示例对话
用户："图注被截断了，帮我修复"
→ 调用 Qwen 识图 → 定位问题 → 修改 HTML → 重新发布

### 配置要求
- Qwen API Key：按量付费国内端点 (`qwen-standard-api-key-cn`)
- 验证命令：`openclaw models list --provider qwen`

---

## 与 baoyu-post-to-wechat 配合使用

发布到微信公众号时，推文标题应从以下字段中选取（优先级从高到低）：
1. `article_title`（推文标题，如果非空）
2. 从 `preamble` 块中选取最合适的标题
3. `title`（文档大标题，作为兜底）

推文摘要使用 `summary_candidate` 字段。

## 后处理修正指南（生成 HTML 后必做）

xuan-skill 生成的 HTML 通常需要以下手动修正，建议开启 --debug 查看 parsed.json 辅助判断：

### 1. 图注识别修正
图片后紧跟的短文本（如“XXX答疑指导”、“XXX现场”）经常被归为 body 而非图注。需要：
- 从正文卡片中移出
- 放到对应图片下方，使用图注样式：`font-size:12px;color:#9e8e82;text-align:center;`

### 2. 去除全文加粗
原始 docx 如果全文加粗，生成的 HTML 也会全部加粗。需要：
- 正文段落：去掉 `font-weight:bold`
- 小标题：保留加粗

### 3. 小标题单独成块
如“特色赋能强专业 座谈部署明方向”这类小标题，需要：
- 从正文卡片中拆出
- 用 `<table><tr><td align="center" style="border:none;padding:10px 0;font-size:16px;font-weight:bold;">` 单独居中显示

### 4. 导语红色边框修正
生成的嵌套 table border 在微信中渲染异常，需要改为 section 嵌套：
```html
<section style="margin:0 0 16px 0;padding:4px;border:2px solid #c0392b;">
  <section style="border:1px dashed #c0392b;background:#ffffff;padding:14px 16px;">
    <p style="...">...</p>
  </section>
</section>
```

### 5. 其他 table 隐藏边框
图片、小标题等用的 table 需要显式隐藏边框：
```html
<table cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;border:none;">
  <tr><td style="border:none;">...</td></tr>
</table>
```

## 发布注意事项

1. **先问发到哪个公众号**
2. **不写作者名**（除非用户特别要求）
3. 封面图如果用户单独发来，用用户发的原图
4. 微信 API author 字段有长度限制，超过约8个字会报错 45110

## 常见问题

| 问题 | 原因 | 建议 |
|------|------|------|
| images_count=0 | docx 中图片为浮动图片 | MVP 不支持浮动图片，需手动嵌入 |
| 图注识别为 0 | 图注文字过长或格式特殊 | 检查 parsed.json 中 caption_candidates |
| HTML 图片显示空白 | 图片路径未替换为线上 URL | 需后续发布 skill 上传图片并替换 src |
| 正文出现重复标题 | title/preamble 块未正确跳过 | 检查 html_renderer.py 中 title/preamble 的 continue 逻辑 |
| 导语段落丢失 | 长文本被错误归为 meta | 检查 parser.py 中 meta 归类的长度限制（应 ≤80 字） |

## 更新记录

### v2.2 (2026-05-19)
- **新增多模型协作工作流**：默认 DeepSeek + 识图切换 Qwen
- Qwen 用于识别推文预览截图中的排版问题（图注截断、gallery 布局、样式异常等）
- 结合用户描述直接定位并修复 HTML 源文件

### v2.1 (2026-04-28)
- **修复标题重复**：title/meta/preamble 块不再渲染到HTML正文中，避免与微信推文标题重复
- **修复导语丢失**：长文本（>80字）不再被错误归为meta，即使包含日期+机构名
- **新增 preamble 类型**：第一张图片之前的短标题/副标题归为 preamble，不渲染到正文
- **增强 overview 信号**：新增"为深化"、"顺利开展"等关键词匹配

### v2.0
- 初始版本，支持社区活动简报风格转换
