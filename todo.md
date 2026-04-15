# easy-doc-cli 优化待办事项 (TODO)

## 2. 原生 Markdown 文本解析 (Markdown Input Support)
- **痛点**：目前富文本输入强依赖 `--latex` 格式。要在 Shell 传入含 `$` 符号或连续 `$` 符号的文本极其痛苦，一旦解析错位会直接导致服务端响应 1781460 等异常 UUID。
- **建议**：在插入/替换命令中增加类似 `--markdown` 选项，让用户可以通过 `**粗体**`、`_斜体_` 的形式输入，CLI 内部统一转换为 `latex_to_leaves` 所需的字典结构或者直接被服务端接管解析。

## 3. ID 依赖降级与相对定位支持 (Relative Positioning)
- **痛点**：当前 `insert` / `replace` 强依赖于目标块的具体 UUID。导致人工调用时永远需要先执行 `read doc --blocks` 然后复制最后一行极长的 UUID。
- **建议**：
  - 允许在 `--ref-id` 中传入负索引（如 `-1` 默认取最后一个 block 的 ID）。
  - 提供类似 `--position end` 的快捷参数，在 `insert` 追加时直接由服务端或 CLI 自动推断末尾追加，无需用户再手动传目标 UUID。



