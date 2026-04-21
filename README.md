# Estructura automática para QR-Planogramas

## Qué hace

- Lee automáticamente las carpetas del repositorio.
- Toma como planogramas todas las carpetas que contengan PDFs.
- Genera un `index.html` principal con las familias.
- Genera un `index.html` dentro de cada carpeta con sus metros.
- Ordena automáticamente archivos como `M1`, `M2`, `M3`.
- No deja los enlaces escritos a mano en el HTML.
- Publica los PDFs en la raíz del sitio para mantener URLs como `.../yogures-M3.pdf`.

## Estructura sugerida del repo

```text
QR-Planogramas/
├─ build_site.py
├─ .github/
│  └─ workflows/
│     └─ deploy-pages.yml
├─ arroz/
│  ├─ arroz-M1.pdf
│  ├─ arroz-M2.pdf
│  └─ ...
├─ yogures/
│  ├─ yogures-M1.pdf
│  ├─ yogures-M2.pdf
│  └─ ...
└─ lavalozas/
   ├─ lavalozas-M1.pdf
   └─ ...
```

## Cómo se publica

En el repositorio los PDFs viven dentro de sus carpetas, pero durante el build se copian así:

```text
site/
├─ index.html
├─ yogures/
│  └─ index.html
├─ arroz/
│  └─ index.html
├─ yogures-M1.pdf
├─ yogures-M2.pdf
├─ yogures-M3.pdf
├─ arroz-M1.pdf
└─ arroz-M2.pdf
```

De esa forma:
- `/QR-Planogramas/` muestra las familias.
- `/QR-Planogramas/yogures/` muestra los metros de yogures.
- Al abrir un metro, el link del PDF queda como `/QR-Planogramas/yogures-M3.pdf`.

## Cómo usarlo

1. Crea una carpeta por planograma.
2. Deja dentro los PDFs de sus metros.
3. Sube `build_site.py` y `.github/workflows/deploy-pages.yml` al repo.
4. En GitHub, entra a **Settings → Pages** y deja como source **GitHub Actions**.
5. Haz push a `main`.

## Importante

- Cada PDF debe tener un nombre único global.
- Ejemplo correcto: `yogures-M1.pdf`, `arroz-M1.pdf`, `lavalozas-M1.pdf`.
- Si dos carpetas tienen un archivo con el mismo nombre, el build fallará para evitar conflictos.

## Nota

El sitio se genera en la carpeta `site/` durante el workflow. Esa carpeta no necesitas subirla al repo.
