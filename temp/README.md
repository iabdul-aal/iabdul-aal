# CV Source

This folder contains the source files for the professional CV.

- Main LaTeX source: `main.tex`
- Bibliography data: `publications.bib`
- ORCID icon asset: `orcid.png`

## Build

From this folder:

```bash
latexmk -pdf main.tex
```

The generated final PDF should be copied to the repository root as `cv.pdf`.
