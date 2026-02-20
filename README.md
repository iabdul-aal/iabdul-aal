# Islam I. Abdulaal

Integrated photonics researcher focused on simulation-driven device design, nonlinear quantum photonics, and physics-informed engineering workflows.

This repository is my **GitHub profile summary source** and also stores the CV assets used across GitHub and my website.

## Current Focus

- Integrated photonics and photonic-electronic co-design
- Nonlinear and quantum-compatible photonic structures
- Physics-informed machine learning for inverse design
- Reproducible research workflows and public technical communication

## Selected Highlights

- Research Intern, NanoPhoto Lab (IMRE, A*STAR)
- arXiv preprint: *Terahertz Quasi-BIC Metasurfaces for Ultra-Sensitive Biosensing and High-Speed Wireless Communications*
- Alexandria University Technology Park (AUTP) research grant (USD 15k)
- Founded/led student technical initiatives: Si-Cast, Si-Clash, AlexDuino, HW Carnival

## Professional Links

- Website: [iabdul-aal.github.io](https://iabdul-aal.github.io)
- CV (final): [`cv.pdf`](cv.pdf)
- CV source: [`temp/main.tex`](temp/main.tex)
- Publications data: [`temp/publications.bib`](temp/publications.bib)
- ORCID: [0009-0004-9300-3936](https://orcid.org/0009-0004-9300-3936)
- LinkedIn: [linkedin.com/in/iabdul-aal](https://linkedin.com/in/iabdul-aal)
- Google Scholar: [Profile](https://scholar.google.com/citations?user=CPmqNv4AAAAJ&hl=en)

## Technical Stack

- Photonics: Lumerical (FDTD, MODE, INTERCONNECT), COMSOL
- Scientific Computing: MATLAB, Python, PyTorch
- Mixed-Signal / IC: Cadence, LTspice, Verilog-A/AMS, Xschem, NGspice
- Digital / Hardware: Verilog, VHDL, Vivado, Quartus, FPGA/CPLD workflows

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

## Build CV

From `temp/`:

```bash
latexmk -pdf main.tex
```

`latexmk` invokes `biber` automatically when bibliography metadata changes.
