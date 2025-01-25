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

## Using md2pdf

To create a wavefile called "low_tone_220Hz.wav" that plays a 220 hertz tone for 100 milliseconds, enter a command like this:

```bash
md2pdf my_markdown.md my_pdf.pdf 
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
