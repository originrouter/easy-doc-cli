"""
Parse a LaTeX tabular environment into a TableElement-compatible dict.

Supports:
  \\multicolumn{n}{fmt}{content}
  \\multirow{n}{*}{content}
  Nested \\multicolumn{...}{...}{\\multirow{...}{*}{content}}
  Rich cell content via latex_to_leaves
"""

from __future__ import annotations
from latex_to_leaves import latex_to_leaves


# ---------------------------------------------------------------------------
# Low-level brace helpers
# ---------------------------------------------------------------------------

def _read_brace_group(s: str, pos: int) -> tuple[str, int]:
    """Read a {...} group starting at pos (pos must point at '{').
    Returns (inner_content, new_pos)."""
    if pos >= len(s) or s[pos] != '{':
        raise ValueError(f"expected '{{' at pos {pos}, got {s[pos:pos+5]!r}")
    depth = 0
    start = pos + 1
    i = pos
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return s[start:i], i + 1
        i += 1
    raise ValueError("Unmatched '{' in LaTeX input")


def _split_cells(row: str) -> list[str]:
    """Split a tabular row by '&' respecting brace depth."""
    cells: list[str] = []
    depth = 0
    current: list[str] = []
    for c in row:
        if c == '{':
            depth += 1
            current.append(c)
        elif c == '}':
            depth -= 1
            current.append(c)
        elif c == '&' and depth == 0:
            cells.append(''.join(current))
            current = []
        else:
            current.append(c)
    cells.append(''.join(current))
    return cells


# ---------------------------------------------------------------------------
# Cell parser
# ---------------------------------------------------------------------------

def _parse_cell(raw: str) -> dict:
    """
    Parse a single cell string into:
      { type, colSpan, rowSpan, children }
    Handles \\multicolumn, \\multirow, and nesting.
    """
    s = raw.strip()
    col_span = 1
    row_span = 1

    # Unwrap \multicolumn{n}{fmt}{content}
    if s.startswith(r'\multicolumn'):
        pos = len(r'\multicolumn')
        n_str, pos = _read_brace_group(s, pos)
        _fmt, pos = _read_brace_group(s, pos)
        inner, pos = _read_brace_group(s, pos)
        col_span = int(n_str.strip())
        s = inner.strip()

    # Unwrap \multirow{n}{*}{content}
    if s.startswith(r'\multirow'):
        pos = len(r'\multirow')
        n_str, pos = _read_brace_group(s, pos)
        _width, pos = _read_brace_group(s, pos)
        inner, pos = _read_brace_group(s, pos)
        row_span = int(n_str.strip())
        s = inner.strip()

    children = latex_to_leaves(s) if s else [{"type": "default", "text": ""}]

    return {
        "type": "table-cell",
        "children": children,
        "colSpan": col_span,
        "rowSpan": row_span,
    }


# ---------------------------------------------------------------------------
# Row splitter
# ---------------------------------------------------------------------------

def _split_rows(body: str) -> list[str]:
    """Split tabular body by '\\\\' (row terminator), drop \\hline and empty rows."""
    import re
    rows = []
    for part in re.split(r'\\\\', body):
        cleaned = part.strip()
        cleaned = re.sub(r'\\hline', '', cleaned).strip()
        if cleaned:
            rows.append(cleaned)
    return rows


# ---------------------------------------------------------------------------
# Span-aware table builder
# ---------------------------------------------------------------------------

def _parse_col_spec(spec: str) -> int:
    """Count the number of data columns in a tabular column spec like 'c|c|c'."""
    return sum(1 for ch in spec if ch in 'clrp')


def _build_table(raw_rows: list[list[dict]], col_length: int) -> dict:
    """
    Given a list of rows (each row = list of parsed cells with colSpan/rowSpan)
    and the known column count, build the TableElement dict.

    For each row, advance a column cursor c from 0 to col_length.
    At each free slot, consume the next raw cell and place it.
    When c reaches col_length, stop — any remaining raw cells are LaTeX
    placeholders for spanned regions and are discarded.
    """
    num_rows = len(raw_rows)
    occupied: set[tuple[int, int]] = set()
    table_rows: list[dict] = []

    for r, raw_cells in enumerate(raw_rows):
        cells_out: list[dict] = []
        c = 0
        cell_iter = iter(raw_cells)

        while c < col_length:
            # Skip slots occupied by rowSpan cells from previous rows
            if (r, c) in occupied:
                c += 1
                continue

            # Consume next logical cell
            cell = next(cell_iter, None)
            if cell is None:
                break

            cs = cell["colSpan"]
            rs = cell["rowSpan"]

            for dr in range(rs):
                for dc in range(cs):
                    occupied.add((r + dr, c + dc))

            cells_out.append(cell)
            c += cs

        table_rows.append({
            "type": "table-row",
            "children": cells_out,
        })

    return {
        "type": "table",
        "children": table_rows,
        "rowLength": num_rows,
        "colLength": col_length,
        "style": {},
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def latex_table_to_dict(latex: str) -> dict:
    """
    Parse a LaTeX string containing a tabular environment and return a
    TableElement-compatible dict.

    The input may be a bare \\begin{tabular}...\\end{tabular} block,
    or a full document — only the first tabular is used.
    """
    begin_tag = r'\begin{tabular}'
    end_tag = r'\end{tabular}'

    start = latex.find(begin_tag)
    if start == -1:
        raise ValueError(r"No \begin{tabular} found in input")

    # Skip the column-spec argument {c|c|...}
    after_begin = start + len(begin_tag)
    col_spec, body_start = _read_brace_group(latex, after_begin)

    end = latex.find(end_tag, body_start)
    if end == -1:
        raise ValueError(r"No \end{tabular} found in input")

    col_length = _parse_col_spec(col_spec)
    body = latex[body_start:end]
    raw_rows = _split_rows(body)
    parsed_rows = [[_parse_cell(c) for c in _split_cells(row)] for row in raw_rows]
    return _build_table(parsed_rows, col_length)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # Correct tabular derived from export_origin (3).json:
    #   row0: 1, 2, 3, 4, 5
    #   row1: 6(c2), 7(r2), 8(c2,r2)
    #   row2: 9, 10  (cols 2-4 occupied by row1 spans)
    sample = r"""
\begin{tabular}{c|c|c|c|c}
\hline
1 & 2 & 3 & 4 & 5 \\
\hline
\multicolumn{2}{|c|}{6} & \multirow{2}{*}{7} & \multicolumn{2}{|c|}{\multirow{2}{*}{8}} \\
\hline
9 & 10 & \multicolumn{2}{|c|}{} & \\
\hline
\end{tabular}
"""
    result = latex_table_to_dict(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))
