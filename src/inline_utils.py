from textnode import TextNode, TextType
import re


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        chunks = old_node.text.split(delimiter)
        if len(chunks) % 2 == 0:
            raise ValueError("invalid Markdown")
        for idx in range(len(chunks)):
            if chunks[idx] == "":
                continue
            if idx % 2 == 0:
                split_nodes.append(TextNode(chunks[idx], TextType.TEXT))
            else:
                split_nodes.append(TextNode(chunks[idx], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def extract_markdown_images(text):
    matches = re.findall(r"!\[(.*?)\]\((\w+\:\/\/[^\s)]+)\)", text)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"\[(.*?)\]\((\w+\:\/\/[^\s)]+)\)", text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        orig_text = old_node.text
        images = extract_markdown_images(orig_text)
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            chunks = orig_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(chunks) != 2:
                raise ValueError("invalid Markdown")
            if chunks[0] != "":
                new_nodes.append(TextNode(chunks[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            orig_text = chunks[1]
        if orig_text != "":
            new_nodes.append(TextNode(orig_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        orig_text = old_node.text
        links = extract_markdown_links(orig_text)
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
        for link in links:
            chunks = orig_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(chunks) != 2:
                raise ValueError("invalid Markdown")
            if chunks[0] != "":
                new_nodes.append(TextNode(chunks[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            orig_text = chunks[1]
        if orig_text != "":
            new_nodes.append(TextNode(orig_text, TextType.TEXT))
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
