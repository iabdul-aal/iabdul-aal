# Islam I. Abdulaal - CV Repository

This repository contains the LaTeX source for my academic CV and related publication metadata.

## Quick Links

- Website: [iabdul-aal.github.io](https://iabdul-aal.github.io)
- CV Source: [`temp/main.tex`](temp/main.tex)
- CV PDF: [`cv.pdf`](cv.pdf)
- Publications Data: [`temp/publications.bib`](temp/publications.bib)
- ORCID: [0009-0004-9300-3936](https://orcid.org/0009-0004-9300-3936)
- LinkedIn: [linkedin.com/in/iabdul-aal](https://linkedin.com/in/iabdul-aal)
- GitHub: [github.com/iabdul-aal](https://github.com/iabdul-aal)

## Design Direction

The CV template is styled to match the visual language of my website:

- Deep navy: `#010814`
- Accent gold: `#B48654`
- Clean section separators and compact research-first layout

## Repository Layout

```text
.
|-- cv.pdf
|-- README.md
`-- temp/
    |-- main.tex
    |-- publications.bib
    `-- orcid.png
```

## Build Instructions

From the `temp/` directory:

```bash
latexmk -pdf main.tex
```

`latexmk` will invoke `biber` automatically when bibliography data changes.

## Notes

- The template is optimized for academic/research applications.
- Content sections can be reused as modular blocks for targeted CV versions (research, internships, scholarships, etc.).
