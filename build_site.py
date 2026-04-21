from __future__ import annotations

import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site"
PDF_EXT = ".pdf"
IGNORE_DIRS = {".git", ".github", "site", "__pycache__"}

COMMON_CSS = r'''
:root {
  --bg: #f6f8fb;
  --text: #1f2937;
  --muted: #6b7280;
  --card: #ffffff;
  --border: #dbe3ef;
  --accent: #2563eb;
  --shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: Arial, Helvetica, sans-serif;
  color: var(--text);
  background: linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
}
.wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px 18px 48px;
}
.hero {
  margin-bottom: 22px;
}
.hero h1 {
  margin: 0 0 8px;
  font-size: 2rem;
}
.hero p {
  margin: 0;
  color: var(--muted);
  line-height: 1.45;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow);
  text-decoration: none;
  color: inherit;
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.card:hover {
  transform: translateY(-2px);
  border-color: #bfd2ff;
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.12);
}
.card-title {
  font-size: 1.05rem;
  font-weight: 700;
}
.card-subtitle {
  font-size: .92rem;
  color: var(--muted);
}
.back-link {
  display: inline-block;
  margin-bottom: 20px;
  text-decoration: none;
  color: var(--accent);
  font-weight: 700;
}
.meta {
  margin-top: 10px;
  color: var(--muted);
  font-size: .92rem;
}
.empty {
  color: var(--muted);
}
.code {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: #eef4ff;
  color: #1d4ed8;
  font-size: 0.88rem;
  font-weight: 700;
}
.notice {
  margin-top: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fff;
  color: var(--muted);
  font-size: .92rem;
}
'''


def prettify_folder_name(name: str) -> str:
    text = name.replace("-", " ").replace("_", " ").strip()
    if not text:
        return name
    return " ".join(part.capitalize() for part in text.split())



def prettify_file_label(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ")



def metro_sort_key(filename: str):
    stem = Path(filename).stem
    match = re.search(r"(?:^|[^A-Za-z])M\s*-?\s*(\d+)(?:[^\d]|$)", stem, flags=re.IGNORECASE)
    if match:
        return (0, int(match.group(1)), stem.lower())

    nums = re.findall(r"\d+", stem)
    if nums:
        return (1, int(nums[-1]), stem.lower())

    return (2, 999999, stem.lower())



def find_planogram_dirs(root: Path) -> list[Path]:
    folders: list[Path] = []
    for item in root.iterdir():
        if not item.is_dir() or item.name in IGNORE_DIRS or item.name.startswith('.'):
            continue
        if any(child.is_file() and child.suffix.lower() == PDF_EXT for child in item.iterdir()):
            folders.append(item)
    return sorted(folders, key=lambda p: p.name.lower())



def render_root_index(entries: list[tuple[str, int]]) -> str:
    cards = []
    for folder_name, pdf_count in entries:
        label = prettify_folder_name(folder_name)
        subtitle = f"{pdf_count} PDF" if pdf_count == 1 else f"{pdf_count} PDFs"
        cards.append(
            f'''<a class="card" href="./{escape(folder_name)}/">\n'''
            f'''  <span class="card-title">{escape(label)}</span>\n'''
            f'''  <span class="card-subtitle">{escape(subtitle)}</span>\n'''
            f'''  <span class="meta"><span class="code">/{escape(folder_name)}/</span></span>\n'''
            f'''</a>'''
        )

    cards_html = "\n".join(cards) if cards else '<p class="empty">No se encontraron carpetas con PDFs.</p>'

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Planogramas</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
  <main class="wrap">
    <header class="hero">
      <h1>Planogramas</h1>
      <p>Selecciona una familia para ver sus metros. La página se construye automáticamente en base a las carpetas y a los nombres de los archivos PDF.</p>
    </header>
    <section class="grid">
      {cards_html}
    </section>
  </main>
</body>
</html>
'''



def render_folder_index(folder_name: str, pdf_names: list[str]) -> str:
    title = prettify_folder_name(folder_name)
    cards = []
    for pdf_name in pdf_names:
        cards.append(
            f'''<a class="card" href="../{escape(pdf_name)}" target="_blank" rel="noopener">\n'''
            f'''  <span class="card-title">{escape(prettify_file_label(pdf_name))}</span>\n'''
            f'''  <span class="card-subtitle">Abrir PDF</span>\n'''
            f'''  <span class="meta"><span class="code">/{escape(pdf_name)}</span></span>\n'''
            f'''</a>'''
        )

    cards_html = "\n".join(cards) if cards else '<p class="empty">No hay PDFs en esta carpeta.</p>'
    example_note = (
        f'<div class="notice">Los PDFs se publican en la raíz del sitio para mantener URLs como '
        f'<span class="code">/{escape(pdf_names[0])}</span>.</div>'
        if pdf_names
        else ''
    )

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | Planogramas</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
  <main class="wrap">
    <a class="back-link" href="../">← Volver a planogramas</a>
    <header class="hero">
      <h1>{escape(title)}</h1>
      <p>Selecciona el metro que quieras revisar.</p>
      <div class="meta">Ruta de la vista: <span class="code">/{escape(folder_name)}/</span></div>
      {example_note}
    </header>
    <section class="grid">
      {cards_html}
    </section>
  </main>
</body>
</html>
'''



def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    entries: list[tuple[str, int]] = []
    published_pdf_names: set[str] = set()

    for folder in find_planogram_dirs(ROOT):
        destination = OUT / folder.name
        destination.mkdir(parents=True, exist_ok=True)

        pdfs = sorted(
            [item.name for item in folder.iterdir() if item.is_file() and item.suffix.lower() == PDF_EXT],
            key=metro_sort_key,
        )

        for pdf_name in pdfs:
            if pdf_name in published_pdf_names:
                raise ValueError(
                    f"Nombre de PDF duplicado al publicar en la raíz del sitio: {pdf_name}. "
                    "Cada PDF debe tener un nombre único global, por ejemplo yogures-M1.pdf."
                )
            published_pdf_names.add(pdf_name)
            shutil.copy2(folder / pdf_name, OUT / pdf_name)

        (destination / 'index.html').write_text(render_folder_index(folder.name, pdfs), encoding='utf-8')
        entries.append((folder.name, len(pdfs)))

    (OUT / 'index.html').write_text(render_root_index(entries), encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Sitio generado en: {OUT}')


if __name__ == '__main__':
    build()
