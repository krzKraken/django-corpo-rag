import re


def format_to_html(text):
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

    return "".join(formatted_lines)


response_text = """En Eclesiastés 10 y 11, se aborda el tema de la suerte y el destino de la siguiente manera:

**Eclesiastés 10:**
- **Versículo 14**: "El tonto multiplica las palabras; no sabe lo que ha de ser..."

**Eclesiastés 11:**
- **Versículo 1**: "Echa tu pan sobre las aguas, porque después de muchos días lo hallarás."
- **Versículo 6**: "Siembra tu semilla por la mañana y a la tarde no dejes descansar tu mano..."

**En resumen:**
- La suerte es incierta.
- Se enfatiza la importancia de la acción y la diligencia"""

html_output = format_to_html(response_text)
print(html_output)
