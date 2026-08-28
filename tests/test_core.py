from marklassian import markdown_to_adf


def test_basic_markdown_elements(basics_adf):
    markdown = """# Hello World

This is a **bold** and *italic* text.

This is a [link](https://example.org).

This is `inline code`

This is ~~striked~~ text

Below is an image
![Example Image](https://picsum.photos/400/300)

## Lists
- Item 1
- Item 2
  - Nested item

1. Ordered item 1
2. Ordered item 2

> This is a blockquote"""

    adf = markdown_to_adf(markdown)
    assert adf == basics_adf


def test_nested_lists(nested_list_adf):
    markdown = """- Item 1
  - Nested item
    - Nested Nested item
      1. Ordered List item nested in unordered list
- **Strong** Item 2

1. Ordered item 1
    1. Nested ordered list item
          1. Nested ordered list item
                - Unordered list item nested in ordered list
2. **Strong** Ordered item 2"""

    adf = markdown_to_adf(markdown)
    assert adf == nested_list_adf


def test_inline_code_marks_only_allow_link(inline_code_marks_adf):
    markdown = """[`Inline Code`](https://github.com)

[**`Inline Code`**](https://github.com)"""

    adf = markdown_to_adf(markdown)
    assert adf == inline_code_marks_adf


def test_nested_inline_marks_inside_link_are_preserved(adf_validator):
    adf = markdown_to_adf(
        "[plain **bold** *italic* ~~strike~~ `code`](https://example.com)"
    )

    adf_validator.validate(adf)
    link = {"type": "link", "attrs": {"href": "https://example.com"}}
    assert adf["content"][0]["content"] == [
        {"type": "text", "text": "plain ", "marks": [link]},
        {"type": "text", "text": "bold", "marks": [link, {"type": "strong"}]},
        {"type": "text", "text": " ", "marks": [link]},
        {"type": "text", "text": "italic", "marks": [link, {"type": "em"}]},
        {"type": "text", "text": " ", "marks": [link]},
        {"type": "text", "text": "strike", "marks": [link, {"type": "strike"}]},
        {"type": "text", "text": " ", "marks": [link]},
        {"type": "text", "text": "code", "marks": [link, {"type": "code"}]},
    ]


def test_outer_marks_are_preserved_across_nested_link_content(adf_validator):
    adf = markdown_to_adf("**outer [plain *italic*](https://example.com)**")

    adf_validator.validate(adf)
    link = {"type": "link", "attrs": {"href": "https://example.com"}}
    assert adf["content"][0]["content"] == [
        {"type": "text", "text": "outer ", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "plain ", "marks": [{"type": "strong"}, link]},
        {
            "type": "text",
            "text": "italic",
            "marks": [{"type": "strong"}, link, {"type": "em"}],
        },
    ]


def test_linked_image_keeps_alt_text_fallback(adf_validator):
    adf = markdown_to_adf("[![Alt text](image.png)](https://example.com)")

    adf_validator.validate(adf)
    assert adf["content"][0]["content"] == [
        {
            "type": "text",
            "text": "Alt text",
            "marks": [
                {
                    "type": "link",
                    "attrs": {"href": "https://example.com"},
                }
            ],
        }
    ]


def test_sibling_text_nodes_do_not_share_mutable_marks():
    adf = markdown_to_adf("[plain **bold** tail](https://example.com)")

    first, middle, last = adf["content"][0]["content"]
    assert first["marks"] is not last["marks"]
    assert first["marks"][0] is not middle["marks"][0]
    assert first["marks"][0]["attrs"] is not middle["marks"][0]["attrs"]


def test_code_blocks(code_blocks_adf):
    markdown = """```typescript
const hello = "world";
console.log(hello);
```

```bash
echo "Hello World"
```

```
Some text
```"""

    adf = markdown_to_adf(markdown)
    assert adf == code_blocks_adf


def test_text_edge_cases(text_edge_cases_adf):
    # Note: Line 6 has two trailing spaces after "a" for hard break
    markdown = (
        "Text will still be in same text block\n"
        "when only one line break.\n"
        "\n"
        "Multiple spaces   will be preserved     in this     text.\n"
        "\n"
        "This line will have a  \n"  # Two trailing spaces for hard break
        "hard break.\n"
        "\n"
        "Thisstringoftexthasa**strong**wordcontained."
    )

    adf = markdown_to_adf(markdown)
    assert adf == text_edge_cases_adf


def test_significant_inline_whitespace_is_preserved(adf_validator):
    adf = markdown_to_adf(
        "Plain   text with\u00a0\u00a0non-breaking spaces.\n\n"
        "`code  with\ttabs`\n\n"
        "`  padded  `\n\n"
        "**Bold   text**\n\n"
        "[Link\u00a0\u00a0text](https://example.com)"
    )

    adf_validator.validate(adf)
    assert [node["content"][0]["text"] for node in adf["content"]] == [
        "Plain   text with\u00a0\u00a0non-breaking spaces.",
        "code  with\ttabs",
        " padded ",
        "Bold   text",
        "Link\u00a0\u00a0text",
    ]


def test_tables(table_adf):
    markdown = """| **First Header** | Second Header |
| ------------- | ------------- |
| Content Cell  | ![Example Image](https://picsum.photos/400/300) Image with text in cell |
| ~~Content Cell~~  | Content Cell  |
| | |"""

    adf = markdown_to_adf(markdown)
    assert adf == table_adf


def test_special_characters(special_chars_adf):
    markdown = r"""# Special Characters Test

## Unicode and Emojis
Text with emojis: 🚀 🎉 ✨ 💻 📝

## Accented Characters
Café, naïve, résumé, piñata, Zürich

## Mathematical Symbols
Equations: α + β = γ, ∑(x²), √16 = 4, π ≈ 3.14159

## Currency and Symbols
Prices: $100, €50, ¥1000, £75, ₹500
Symbols: ©2024, ®, ™, °C, ±5%

## Special Punctuation
Quotes: "Hello" 'World' „German" «French»
Dashes: em—dash, en–dash, hyphen-dash
Ellipsis: Wait... for it…

## Escaped Markdown Characters
Literal asterisks: \*not bold\*, \*\*not bold\*\*
Literal underscores: \_not italic\_, \_\_not bold\_\_
Literal backticks: \`not code\`
Literal hash: \# not heading

## Mixed Content
**Bold with émojis: 🔥 café** and *italic with symbols: α±β*

[Link with special chars](https://example.com/café?param=value&other=™)

`Code with symbols: const π = Math.PI; // ≈ 3.14159`

## Code Block with Special Characters
```javascript
// Special chars in code
const greeting = "Hello 🌍!";
const price = "€25.99";
console.log(`Price: ${price}`);
```

## Table with Special Characters
| Symbol | Description | Unicode |
|--------|-------------|---------|
| 🚀 | Rocket | U+1F680 |
| café ☕ | Coffee shop | Mixed |
| α + β | Math symbols | Greek |

> Blockquote with special characters: "Wisdom is knowing that you don't know." — Socrates ⭐"""

    adf = markdown_to_adf(markdown)
    assert adf == special_chars_adf


def test_empty_block_nodes_have_schema_valid_content() -> None:
    empty_code = markdown_to_adf("```\n```")
    assert empty_code["content"] == [
        {"type": "codeBlock", "attrs": {"language": "text"}},
    ]

    empty_quote = markdown_to_adf(">")
    assert empty_quote["content"] == [
        {"type": "blockquote", "content": [{"type": "paragraph"}]},
    ]

    empty_list = markdown_to_adf("-")
    assert empty_list["content"] == [
        {
            "type": "bulletList",
            "content": [
                {"type": "listItem", "content": [{"type": "paragraph"}]},
            ],
        },
    ]
