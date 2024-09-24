""" def format_to_html(text):
    # Convertir saltos de línea en <br>
    text = text.replace("\n", "<br>")

    # Convertir **texto** en <strong>texto</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)

    # Convertir - elemento en una lista
    lines = text.split("<br>")
    formatted_lines = []
    in_list = False

    for line in lines:
        if line.strip().startswith("-"):
            if not in_list:
                formatted_lines.append("<ul>")
                in_list = True
            formatted_lines.append(f"<li>{line.strip()[1:].strip()}</li>")
        else:
            if in_list:
                formatted_lines.append("</ul>")
                in_list = False
            formatted_lines.append(line)

    if in_list:
        formatted_lines.append("</ul>")

    print(formatted_lines)

    return "".join(formatted_lines)
"""
