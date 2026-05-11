# md2pdf - Convert Markdown Files To PDF

Travis L. Seymour, PhD

---

## Installation

### Install `uv`
Install `uv` for MacOS, Windows or Linux based on the instructions from (https://docs.astral.sh/uv/getting-started/installation/). The most likely scenarios are listed below

#### MacOS & Linux

Use curl to download the script and execute it with sh:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

Use irm to download the script and execute it with iex:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Install md2pdf

```bash
uv tool install git+https://github.com/travisseymour/md2pdf.git
```

--- 

## Usage

### Basic conversion

Convert a Markdown file to PDF. The output file defaults to the same name with a `.pdf` extension:

```bash
md2pdf my_document.md
```

This produces `my_document.pdf`. You can also specify the output path explicitly:

```bash
md2pdf my_document.md custom_name.pdf
```

### Options

| Option | Description |
| --- | --- |
| `--save-html` | Save the intermediate HTML file alongside the PDF |
| `--theme TEXT` | Pygments syntax highlighting theme (default: `monokai`). Options: `default`, `monokai`, `manni`, `vim`, `friendly`, `native`, `github` |
| `--margin FLOAT` | Page margins in inches (e.g. `0.75`). When omitted, the default margins are used |
| `--font-scale INT` | Font size as a percentage of the default (e.g. `120` for 20% larger) |

### Examples

Convert with larger text and narrower margins:

```bash
md2pdf notes.md --font-scale 120 --margin 0.5
```

Convert and keep the intermediate HTML for inspection:

```bash
md2pdf notes.md --save-html
```

Use a different syntax highlighting theme:

```bash
md2pdf notes.md --theme github
```

---

## Upgrade md2pdf

Upgrade md2pdf by opening your operating system's terminal application and type this command:

```bash
uv tool upgrade md2pdf
```

## Uninstall md2pdf

Uninstall md2pdf by opening your operating system's terminal application and type this command:

```bash
uv tool uninstall md2pdf
```
