# Paper Package

The paper draft in `internetx.tex` is substantive and aligned with the current repository state. The current local environment does not include `pdflatex` or `latexmk`, so the repository uses `make paper-check` as an in-repo sanity step.

To build a PDF on a machine with LaTeX installed:

```bash
pdflatex internetx.tex
bibtex internetx
pdflatex internetx.tex
pdflatex internetx.tex
```
