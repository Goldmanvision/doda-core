"""Measured-width wrapping and pagination for CRT catalog text."""
import re

def wrap_lines(lines, measure, width):
    if width <= 0:
        raise ValueError("Text width must be positive.")
    output = []
    for value in lines:
        for paragraph in str(value).split("\n"):
            words = re.findall(r"\S+", paragraph)
            if not words:
                output.append("")
                continue
            current = ""
            for word in words:
                candidate = current + (" " if current else "") + word
                if measure(candidate) <= width:
                    current = candidate
                    continue
                if current:
                    output.append(current)
                    current = ""
                while word and measure(word) > width:
                    count = 0
                    for i in range(1, len(word) + 1):
                        if measure(word[:i]) <= width:
                            count = i
                        else:
                            break
                    if count == 0:
                        raise ValueError("Panel cannot fit one text character.")
                    output.append(word[:count])
                    word = word[count:]
                current = word
            if current:
                output.append(current)
    return output or [""]

def detail_pages(lines, measure, width, page_size=23):
    if page_size < 1:
        raise ValueError("Page size must be positive.")
    wrapped = wrap_lines(lines, measure, width)
    return [wrapped[i:i + page_size] for i in range(0, len(wrapped), page_size)]

def sidebar_pages(rows, measure, width, height=343, line_height=14):
    pages, page, used = [], [], 0
    for row in rows:
        name = row.get("display_name") or row.get("facility_id", "")
        lines = wrap_lines([name], measure, width)
        entry_height = max(42, len(lines) * line_height + 20)
        if entry_height > height:
            raise ValueError("Catalog entry name exceeds the sidebar height.")
        if page and used + entry_height > height:
            pages.append(page)
            page, used = [], 0
        page.append((row, lines, entry_height))
        used += entry_height
    if page:
        pages.append(page)
    return pages or [[]]

def header_layout(title, left_heading, right_heading,
                  title_measure, heading_measure,
                  title_width, left_width, right_width):
    title_lines = wrap_lines([title], title_measure, title_width)
    left_lines = wrap_lines([left_heading], heading_measure, left_width)
    right_lines = wrap_lines([right_heading], heading_measure, right_width)
    banner_bottom = max(48, 18 + 12 + len(title_lines) * 16)
    panel_top = banner_bottom + 10
    heading_top = panel_top + 11
    body_top = heading_top + max(len(left_lines), len(right_lines)) * 16 + 7
    if body_top > 390:
        raise ValueError("Catalog headers leave insufficient body space.")
    return {
        "title_lines": title_lines,
        "left_lines": left_lines,
        "right_lines": right_lines,
        "banner_bottom": banner_bottom,
        "panel_top": panel_top,
        "heading_top": heading_top,
        "body_top": body_top,
        "sidebar_height": 436 - body_top,
        "detail_page_size": (435 - body_top) // 15 + 1,
    }
