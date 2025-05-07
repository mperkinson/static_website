import re
from enum import Enum
from htmlnode import ParentNode
from inline_utils import text_to_textnodes
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    ULIST = "unordered_list"
    OLIST = "ordered_list"


def markdown_to_blocks(markdown):
    blocks = []
    splits = markdown.split("\n\n")
    for split in splits:
        if split == "" or split == "\n":
            continue
        stripped = split.strip()
        cleaned = stripped.replace("\n  ", "\n")
        blocks.append(cleaned)
    return blocks


def block_to_block_type(markdown):
    lines = markdown.split("\n")
    heading_pattern = r"#{1,6} \S+"
    code_pattern = r"\s*`{3}\s*\S+\s*`{3}"
    quote_pattern = r">"
    ulist_pattern = r"- "
    olist_pattern = r"1. "

    if re.match(heading_pattern, markdown):
        return BlockType.HEADING

    if markdown.startswith("```"):
        return BlockType.CODE

    if re.match(quote_pattern, markdown):
        for line in lines:
            if not re.match(quote_pattern, line):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE

    if re.match(ulist_pattern, markdown):
        for line in lines:
            if not re.match(ulist_pattern, line):
                return BlockType.PARAGRAPH
        return BlockType.ULIST

    if re.match(olist_pattern, markdown):
        i = 1
        for line in lines:
            if not re.match(f"{i}. ", line):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST

    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    if block_type == BlockType.ULIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.OLIST:
        return olist_to_html_node(block)
    raise ValueError("invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError("invalid heading level")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    lines = block.split("\n")
    start_line = 0
    end_line = len(lines)

    for i, line in enumerate(lines):
        if "```" in line:
            start_line = i
            break

    for i in range(len(lines) - 1, -1, -1):
        if "```" in lines[i]:
            end_line = i
            break

    content = "\n".join(lines[start_line + 1 : end_line])

    if not content.endswith("\n"):
        content += "\n"

    raw_text_node = TextNode(content, TextType.TEXT)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])


def quote_to_html_node(block):
    quote_pattern = r">"
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not re.match(quote_pattern, line):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)


def ulist_to_html_node(block):
    lines = block.split("\n")
    html_lines = []
    for line in lines:
        text = line[2:]
        children = text_to_children(text)
        html_lines.append(ParentNode("li", children))
    return ParentNode("ul", html_lines)


def olist_to_html_node(block):
    lines = block.split("\n")
    html_lines = []
    for line in lines:
        text = line[3:]
        children = text_to_children(text)
        html_lines.append(ParentNode("li", children))
    return ParentNode("ol", html_lines)
