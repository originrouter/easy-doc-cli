# Style validation schemas derived from blockstyle.txt and blockcssstyle.txt

# CSS style fields per element type
_CSS_STYLE_FIELDS = {
    "TitleElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "AuthorElementCssStyle": {
        "backgroundColor", "marginTop", "marginBottom",
        "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "AuthorElementAuthorCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "justifyContent",
        "width", "lineHeight", "letterSpacing", "gap",
    },
    "AuthorElementInstitutionCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "justifyContent",
        "width", "lineHeight", "letterSpacing", "gap",
    },
    "AbstractElementCssStyle": {
        "fontSize", "letterSpacing", "fontWeight", "justifyContent",
        "marginTop", "marginBottom", "width",
    },
    "ParagraphElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "EquationElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "H1ElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "H2ElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "H3ElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "ImageElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
        "columnGap", "rowGap",
    },
    "TableElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "CodeElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
    },
    "LabelElementCssStyle": {
        "fontSize", "marginTop", "marginBottom", "width",
    },
    "ListElementCssStyle": {
        "fontFamily", "fontSize", "fontWeight", "color", "backgroundColor",
        "justifyContent", "marginTop", "marginBottom", "width", "lineHeight",
        "letterSpacing", "borderStyle", "borderWidth", "borderRadius", "borderColor",
        "alignItems", "columnGap", "rowGap",
    },
}

# Top-level style fields per element type (from blockstyle.txt)
# "style" key itself is always the CssStyle object; other keys are element-specific
ELEMENT_STYLE_SCHEMAS = {
    "title": {
        "style": _CSS_STYLE_FIELDS["TitleElementCssStyle"],
        "isTemplate": bool,
    },
    "author": {
        "style": _CSS_STYLE_FIELDS["AuthorElementCssStyle"],
        "authorStyle": _CSS_STYLE_FIELDS["AuthorElementAuthorCssStyle"],
        "institutionStyle": _CSS_STYLE_FIELDS["AuthorElementInstitutionCssStyle"],
        "isTemplate": bool,
    },
    "abstract": {
        "style": _CSS_STYLE_FIELDS["AbstractElementCssStyle"],
        "isTemplate": bool,
        "language": {"none", "zh", "en"},
        "titlePosition": {"left", "top"},
        "titlePadding": str,
    },
    "paragraph": {
        "style": _CSS_STYLE_FIELDS["ParagraphElementCssStyle"],
        "isTemplate": bool,
        "indent": bool,
    },
    "equation": {
        "style": _CSS_STYLE_FIELDS["EquationElementCssStyle"],
        "isTemplate": bool,
        "serial": bool,
    },
    "h1": {
        "style": _CSS_STYLE_FIELDS["H1ElementCssStyle"],
        "isTemplate": bool,
        "isHideIndex": bool,
    },
    "h2": {
        "style": _CSS_STYLE_FIELDS["H2ElementCssStyle"],
        "isTemplate": bool,
        "isHideIndex": bool,
    },
    "h3": {
        "style": _CSS_STYLE_FIELDS["H3ElementCssStyle"],
        "isTemplate": bool,
        "isHideIndex": bool,
    },
    "image": {
        "style": _CSS_STYLE_FIELDS["ImageElementCssStyle"],
        "isTemplate": bool,
        "serial": bool,
        "titleLanguage": {"none", "zh", "en"},
        "titleMargin": str,
        "titlePadding": str,
        "columns": {1, 2, 3},
        "columnRatios": list,
    },
    "table": {
        "style": _CSS_STYLE_FIELDS["TableElementCssStyle"],
        "isTemplate": bool,
        "textAlign": {"center", "start", "end"},
        "verticalAlign": {"middle", "top", "bottom"},
        "firstRowBold": bool,
        "firstColBold": bool,
        "padding": str,
    },
    "code": {
        "style": _CSS_STYLE_FIELDS["CodeElementCssStyle"],
        "isTemplate": bool,
        "isHideLanguage": bool,
    },
    "label": {
        "style": _CSS_STYLE_FIELDS["LabelElementCssStyle"],
        "isTemplate": bool,
        "nameWidth": str,
        "columnGap": str,
        "rowGap": str,
        "twoColumn": bool,
    },
    "list": {
        "style": _CSS_STYLE_FIELDS["ListElementCssStyle"],
        "isTemplate": bool,
        "orderType": {"disc", "decimal", "lower-alpha", "upper-alpha", "lower-roman", "upper-roman"},
        "orderWidth": str,
        "indentWidth": str,
    },
}


def _is_css_field(expected) -> bool:
    """A schema value is a CSS field set if it's a set of strings (not a set of literals like {1,2,3})."""
    return isinstance(expected, set) and all(isinstance(e, str) for e in expected)


def validate_css_style(element_type: str, css_style: dict) -> list[str]:
    """
    Validate CSS style fields (the 'style' key in payload) for the given element type.
    css_style should be a flat dict of CSS property -> value, e.g. {"fontSize": "16px"}.
    """
    errors = []
    schema = ELEMENT_STYLE_SCHEMAS.get(element_type)
    if schema is None:
        return [f"Unknown element type: '{element_type}'"]

    # Find the CSS field set for this element (keyed as "style" in schema)
    css_fields = schema.get("style")
    if css_fields is None:
        return [f"[{element_type}] does not support css-style"]

    for key in css_style:
        if key not in css_fields:
            errors.append(f"[{element_type}] '{key}' is not a valid CSS style field")

    return errors


def validate_block_style(element_type: str, style: dict) -> list[str]:
    """
    Validate block-specific style fields (non-CSS) for the given element type.
    e.g. {"isTemplate": true, "serial": true}
    """
    errors = []
    schema = ELEMENT_STYLE_SCHEMAS.get(element_type)
    if schema is None:
        return [f"Unknown element type: '{element_type}'"]

    for key, value in style.items():
        if key == "style":
            errors.append(f"[{element_type}] use --css-style for CSS fields, not --style")
            continue
        if key not in schema:
            errors.append(f"[{element_type}] Unknown style field: '{key}'")
            continue

        expected = schema[key]

        if _is_css_field(expected):
            errors.append(f"[{element_type}] '{key}' is a CSS style field, use --css-style instead")
        elif isinstance(expected, set):
            # enum of literal values
            if value not in expected:
                errors.append(
                    f"[{element_type}] '{key}' must be one of {sorted(str(v) for v in expected)}, got '{value}'"
                )
        elif expected is bool:
            if not isinstance(value, bool):
                errors.append(f"[{element_type}] '{key}' must be a boolean, got {type(value).__name__}")
        elif expected is str:
            if not isinstance(value, str):
                errors.append(f"[{element_type}] '{key}' must be a string, got {type(value).__name__}")
        elif expected is list:
            if not isinstance(value, list):
                errors.append(f"[{element_type}] '{key}' must be a list, got {type(value).__name__}")

    return errors


def validate_style(element_type: str, style: dict) -> list[str]:
    """
    Legacy: validate a combined style dict (css fields nested under 'style' key + block-specific fields).
    Kept for backwards compatibility.
    """
    errors = []
    schema = ELEMENT_STYLE_SCHEMAS.get(element_type)
    if schema is None:
        return [f"Unknown element type: '{element_type}'"]

    for key, value in style.items():
        if key not in schema:
            errors.append(f"[{element_type}] Unknown style field: '{key}'")
            continue

        expected = schema[key]

        if _is_css_field(expected):
            if not isinstance(value, dict):
                errors.append(f"[{element_type}] '{key}' must be a dict, got {type(value).__name__}")
            else:
                for css_key in value:
                    if css_key not in expected:
                        errors.append(f"[{element_type}] '{key}.{css_key}' is not a valid CSS style field")
        elif isinstance(expected, set):
            if value not in expected:
                errors.append(
                    f"[{element_type}] '{key}' must be one of {sorted(str(v) for v in expected)}, got '{value}'"
                )
        elif expected is bool:
            if not isinstance(value, bool):
                errors.append(f"[{element_type}] '{key}' must be a boolean, got {type(value).__name__}")
        elif expected is str:
            if not isinstance(value, str):
                errors.append(f"[{element_type}] '{key}' must be a string, got {type(value).__name__}")
        elif expected is list:
            if not isinstance(value, list):
                errors.append(f"[{element_type}] '{key}' must be a list, got {type(value).__name__}")

    return errors
