"""
Convert a LaTeX-formatted string into a list of TextLeaf nodes.

Supported LaTeX constructs:
  \\textbf{...}          -> bold
  \\textit{...}          -> italic
  \\underline{...}       -> textDecoration: underline
  \\sout{...}            -> textDecoration: line-through  (requires ulem)
  \\textcolor{color}{...}-> color
  \\href{url}{text}      -> UrlText (type: url)
  \\texttt{...}          -> CodeText (type: inlinecode)
  $...$                  -> LatexText (type: latex)
  Nesting is supported (e.g. \\textbf{\\textit{...}})
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Internal state carried through recursive parsing
# ---------------------------------------------------------------------------

@dataclass
class _Style:
    bold: bool = False
    italic: bool = False
    text_decoration: str | None = None  # "underline" | "line-through"
    color: str | None = None

    def copy(self) -> "_Style":
        return _Style(self.bold, self.italic, self.text_decoration, self.color)


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

def _tokenise(s: str) -> list[str]:
    """
    Split a LaTeX string into tokens:
      - LaTeX commands: \\commandname
      - Single characters (including '{', '}', '$')
    """
    tokens: list[str] = []
    i = 0
    while i < len(s):
        if s[i] == '\\':
            # Read command name (letters only)
            j = i + 1
            while j < len(s) and s[j].isalpha():
                j += 1
            if j == i + 1:
                # Single non-alpha char after backslash (e.g. \\ or \{)
                tokens.append(s[i:i+2])
                i += 2
            else:
                tokens.append(s[i:j])
                i = j
        else:
            tokens.append(s[i])
            i += 1
    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _parse(tokens: list[str], pos: int, style: _Style, results: list[dict]) -> int:
    """
    Recursively parse tokens starting at *pos*.
    Appends TextLeaf dicts to *results*.
    Returns the new position after parsing.
    """
    while pos < len(tokens):
        tok = tokens[pos]

        if tok == '}':
            # End of a group – return to caller
            return pos + 1

        # ---- inline math $...$ ----------------------------------------
        if tok == '\\$':
            results.append(_make_text('$', style))
            pos += 1
            continue

        if tok == '$':
            pos += 1
            math_tokens: list[str] = []
            while pos < len(tokens) and tokens[pos] != '$':
                math_tokens.append(tokens[pos])
                pos += 1
            pos += 1  # consume closing $
            results.append({
                "type": "latex",
                "text": "".join(math_tokens),
            })
            continue

        # ---- commands -------------------------------------------------
        if tok.startswith('\\'):
            cmd = tok[1:]  # strip backslash

            # \textbf{...}
            if cmd == 'textbf':
                pos = _expect_group(tokens, pos + 1, style.copy(), results,
                                    bold=True)
                continue

            # \textit{...}
            if cmd == 'textit':
                pos = _expect_group(tokens, pos + 1, style.copy(), results,
                                    italic=True)
                continue

            # \underline{...}
            if cmd == 'underline':
                pos = _expect_group(tokens, pos + 1, style.copy(), results,
                                    text_decoration='underline')
                continue

            # \sout{...}  (strikethrough via ulem package)
            if cmd == 'sout':
                pos = _expect_group(tokens, pos + 1, style.copy(), results,
                                    text_decoration='line-through')
                continue

            # \textcolor{color}{text}
            if cmd == 'textcolor':
                color_val, pos = _read_group_text(tokens, pos + 1)
                pos = _expect_group(tokens, pos, style.copy(), results,
                                    color=color_val)
                continue

            # \texttt{...}  -> inlinecode
            if cmd == 'texttt':
                code_text, pos = _read_group_text(tokens, pos + 1)
                results.append({
                    "type": "inlinecode",
                    "text": code_text,
                })
                continue

            # \href{url}{display text}
            if cmd == 'href':
                url_val, pos = _read_group_text(tokens, pos + 1)
                display_text, pos = _read_group_text(tokens, pos)
                results.append({
                    "type": "url",
                    "text": display_text,
                    "url": url_val,
                })
                continue

            # \\ -> newline (skip or treat as space)
            if cmd == '\\':
                pos += 1
                continue

            # Unknown command – emit as literal text
            results.append(_make_text(tok, style))
            pos += 1
            continue

        # ---- plain '{' opens an anonymous group -----------------------
        if tok == '{':
            pos = _parse(tokens, pos + 1, style.copy(), results)
            continue

        # ---- plain text character -------------------------------------
        results.append(_make_text(tok, style))
        pos += 1

    return pos


def _expect_group(tokens: list[str], pos: int, style: _Style,
                  results: list[dict], **style_overrides) -> int:
    """Consume '{', apply style overrides, parse until '}', return new pos."""
    for k, v in style_overrides.items():
        setattr(style, k, v)
    if pos < len(tokens) and tokens[pos] == '{':
        pos = _parse(tokens, pos + 1, style, results)
    return pos


def _read_group_text(tokens: list[str], pos: int) -> tuple[str, int]:
    """Read a brace group and return its raw text content + new pos."""
    if pos >= len(tokens) or tokens[pos] != '{':
        return '', pos
    pos += 1
    parts: list[str] = []
    depth = 1
    while pos < len(tokens):
        t = tokens[pos]
        if t == '{':
            depth += 1
            parts.append(t)
        elif t == '}':
            depth -= 1
            if depth == 0:
                pos += 1
                break
            parts.append(t)
        else:
            parts.append(t)
        pos += 1
    return ''.join(parts), pos


def _make_text(char: str, style: _Style) -> dict:
    node: dict[str, Any] = {
        "type": "default",
        "text": char,
    }
    if style.bold:
        node["bold"] = True
    if style.italic:
        node["italic"] = True
    if style.text_decoration:
        node["textDecoration"] = style.text_decoration
    if style.color:
        node["color"] = style.color
    return node


# ---------------------------------------------------------------------------
# Merge consecutive FormattedText nodes with identical styles
# ---------------------------------------------------------------------------

def _merge(nodes: list[dict]) -> list[dict]:
    if not nodes:
        return nodes
    merged: list[dict] = [nodes[0]]
    for node in nodes[1:]:
        prev = merged[-1]
        # Only merge "default" text nodes
        if (prev.get("type") == "default" == node.get("type") and
                prev.get("bold") == node.get("bold") and
                prev.get("italic") == node.get("italic") and
                prev.get("textDecoration") == node.get("textDecoration") and
                prev.get("color") == node.get("color")):
            prev["text"] += node["text"]
        else:
            merged.append(node)
    return merged


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def latex_to_leaves(latex: str) -> list[dict]:
    """
    Convert a LaTeX inline string to a list of TextLeaf dicts.

    Example
    -------
    >>> latex_to_leaves(r"hello \\textbf{world}")
    [
      { "type": "default", "text": "hello "},
      { "type": "default", "bold": True, "text": "world"},
    ]
    """
    tokens = _tokenise(latex)
    results: list[dict] = []
    _parse(tokens, 0, _Style(), results)
    return _merge(results)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    samples = [
        r"使用cli操作文档，\textbf{加粗，}\textbf{\textit{斜体}}",
        r"普通 \underline{下划线} 和 \sout{删除线}",
        r"\textcolor{red}{红色文字}",
        r"行内代码：\texttt{print('hello')}",
        r"链接：\href{https://example.com}{点击这里}",
        r"公式：$E = mc^2$ 结束",
    ]

    for s in samples:
        print(f"Input : {s}")
        print(json.dumps(latex_to_leaves(s), ensure_ascii=False, indent=2))
        print()
