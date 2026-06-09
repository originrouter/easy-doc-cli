# easy-doc-cli

文档编辑命令行工具，通过 API 对文档块进行增删改查和样式调整。

## 快速开始

```bash
# 1. 创建 session（每次编辑前需要先创建）
python cli.py session create --doc-id <文档ID>

# 2. 读取文档
python cli.py read doc --text
```

---

## 命令总览

| 命令 | 说明 |
|------|------|
| `session create` | 创建编辑 session |
| `session info` | 查看当前 session 信息 |
| `doc create` | 创建文档 |
| `doc delete` | 删除文档 |
| `list groups` | 列出所有 group |
| `list articles` | 列出文章（含子文章） |
| `read doc` | 读取完整文档 |
| `read block` | 读取指定块 |
| `insert` | 在指定块前后插入新块 |
| `append` | 向块追加文本 |
| `replace` | 替换块的全部文本 |
| `block delete` | 删除指定块 |
| `block-style` | 修改块的样式 |
| `style-schema` | 查询块类型支持的样式字段 |

---

## session 管理

### `session create`

创建一个新的编辑 session，session 信息会缓存到本地。session 过期后，后续命令会自动重建。

```bash
python cli.py session create --doc-id <文档ID>
```

### `session info`

查看当前缓存的 session 信息。

```bash
python cli.py session info
# 输出：
# docId:      xxx
# sessionId:  xxx
# blockCount: 10
```

---

## 文档管理

### `doc create`

创建一篇新文档。

```bash
python cli.py doc create --name "新文档" --group-id 0
# 输出：
# 创建成功
#   outer_id: 269073564450299904
#   name:     新文档
#   group:    0
```

| 参数 | 说明 |
|------|------|
| `--name` | 文档名称（必填） |
| `--group-id` | 所属 group ID（默认 `0`） |

### `doc delete`

删除指定文档。

```bash
python cli.py doc delete --doc-id 269073564450299904
```

---

## 列出 group 和文章

### `list groups`

列出所有 group 的 ID 和名称。

```bash
python cli.py list groups
# 输出：
# GROUP_ID     NAME
# ----------------------------------------
# 0            我的私人文章
# 12345        物理笔记
```

### `list articles`

列出文章，子文章缩进显示。

```bash
# 列出所有文章
python cli.py list articles

# 只列出指定 group
python cli.py list articles --group-id 0

# 时间戳保留原始数字
python cli.py list articles --raw

# 输出原始 JSON
python cli.py list articles --json
```

输出示例：

```
GROUP          DOC_ID                 NAME                             创建时间
------------------------------------------------------------------------------------------
我的私人文章   73490789023490048      量子力学                         2025-01-01 08:00:00
               267699966355578880     Hamilton-Jacobi                  2025-01-02 08:00:00
                 └ 267699966355578881  Hamilton-Jacobi 第一章           2025-01-03 08:00:00
```

---

## 读取文档

### `read doc`

读取完整文档，默认输出完整 JSON。

```bash
# 完整 JSON
python cli.py read doc

# 只输出纯文本
python cli.py read doc --text

# 逐行输出每个 block 的 JSON
python cli.py read doc --blocks
```

### `read block`

读取指定块的详细信息（含 path、类型、内容等）。

```bash
python cli.py read block --id <blockId>
```

---

## 删除块

### `block delete`

删除指定块。

```bash
python cli.py block delete --id <blockId>
```

| 参数 | 说明 |
|------|------|
| `--id` | 块 ID（必填） |

---

## 插入块

在参考块的前面或后面插入一个或多个新块。

```bash
python cli.py insert --ref-id <参考块ID> [--position before|after] (--type ... | --block ...)
```

**参数：**

| 参数 | 说明 |
|------|------|
| `--ref-id` | 参考块 ID（必填） |
| `--position` | `before` 或 `after`（默认 `after`） |
| `--type` | 块类型，见下方支持列表 |
| `--text` | 文本内容 |
| `--latex` | LaTeX 格式文本 |
| `--equation` | LaTeX 公式（`equation` 类型专用） |
| `--code` | 代码内容（`code` 类型专用） |
| `--language` | 代码语言（默认 `纯文本`） |
| `--items` | 列表项，空格分隔（`list` 类型专用） |
| `--block JSON` | 直接传入原始 JSON 块，可重复使用 |

**支持的块类型：**

`title` / `abstract` / `paragraph` / `h1` / `h2` / `h3` / `equation` / `code` / `list` / `author` / `image` / `table` / `label`

**示例：**

```bash
# 插入段落
python cli.py insert --ref-id abc123 --type paragraph --text "这是一段新内容"

# 插入标题（在前面）
python cli.py insert --ref-id abc123 --position before --type h1 --text "第一章"

# 插入代码块
python cli.py insert --ref-id abc123 --type code --code "print('hello')" --language Python

# 插入公式
python cli.py insert --ref-id abc123 --type equation --equation "E=mc^2"

# 插入列表
python cli.py insert --ref-id abc123 --type list --items "第一项" "第二项" "第三项"

# 插入原始 JSON 块
python cli.py insert --ref-id abc123 --block '{"type":"paragraph","children":[{"text":"内容"}]}'
```

**代码语言可选值：**

`纯文本` `Bash` `C` `C#` `C++` `CSS` `Dart` `Dockerfile` `F#` `Fortran` `Go` `HTML` `Java` `JavaScript` `JSON` `Julia` `Kotlin` `Less` `Lua` `Markdown` `MATLAB` `PHP` `PowerShell` `Python` `R` `Rust` `Sass` `SQL` `Swift` `TypeScript` `YAML` `XML`

---

## 追加文本

向指定块末尾追加文本，不覆盖原有内容。

```bash
# 追加纯文本
python cli.py append --id <blockId> --text "追加的内容"

# 追加 LaTeX 文本
python cli.py append --id <blockId> --latex "x^2 + y^2 = z^2"
```

`--text` 和 `--latex` 二选一，均为必填。

---

## 替换块文本

替换指定块的全部文本内容。

```bash
# 替换为纯文本
python cli.py replace --id <blockId> --text "新内容"

# 替换为 LaTeX 文本
python cli.py replace --id <blockId> --latex "\alpha + \beta = \gamma"
```

`--text` 和 `--latex` 二选一，均为必填。

---

## 修改块样式

修改指定块的 CSS 样式或块特有属性。

```bash
python cli.py block-style --id <blockId> [样式参数...]
```

**CSS 样式（`--css` / `--css-style`）：**

```bash
# 键值对方式（可重复）
python cli.py block-style --id abc123 --css fontSize=18px --css color=#333333

# JSON 方式
python cli.py block-style --id abc123 --css-style '{"fontSize":"18px","color":"#333333"}'
```

**块特有属性（`--prop` / `--style`）：**

```bash
# 键值对方式（可重复，支持 true/false/数字）
python cli.py block-style --id abc123 --prop isTemplate=true --prop indent=true

# JSON 方式
python cli.py block-style --id abc123 --style '{"isTemplate":true,"indent":true}'
```

两种方式可以混用，JSON 参数优先，键值对参数叠加其上。

---

## 查询样式字段

查看各块类型支持哪些样式字段，方便使用 `block-style` 前确认字段名。

```bash
# 查看所有类型
python cli.py style-schema

# 查看指定类型
python cli.py style-schema --type paragraph
python cli.py style-schema --type table
```

输出示例：

```
Block type: paragraph
  CSS fields (--css):
    backgroundColor
    borderColor
    fontSize
    ...
  Block props (--prop):
    indent               bool
    isTemplate           bool
```

---

## 块特有属性参考

| 块类型 | 可用属性 |
|--------|---------|
| `title` | `isTemplate` |
| `abstract` | `isTemplate`, `language` (none/zh/en), `titlePosition` (left/top), `titlePadding` |
| `paragraph` | `isTemplate`, `indent` |
| `h1/h2/h3` | `isTemplate`, `isHideIndex` |
| `equation` | `isTemplate`, `serial` |
| `code` | `isTemplate`, `isHideLanguage` |
| `list` | `isTemplate`, `orderType` (disc/decimal/lower-alpha/upper-alpha/lower-roman/upper-roman), `orderWidth`, `indentWidth` |
| `image` | `isTemplate`, `serial`, `titleLanguage`, `titleMargin`, `titlePadding`, `columns` (1/2/3), `columnRatios` |
| `table` | `isTemplate`, `textAlign` (center/start/end), `verticalAlign` (middle/top/bottom), `firstRowBold`, `firstColBold`, `padding` |
| `label` | `isTemplate`, `nameWidth`, `columnGap`, `rowGap`, `twoColumn` |
| `author` | `isTemplate`, `authorStyle`, `institutionStyle` |
