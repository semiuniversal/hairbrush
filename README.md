# TinyG Tester

A testing and configuration tool for TinyG CNC controllers, specifically designed for dual airbrush control systems.

## Installation

# Clone the repository
```bash
git clone <your-repo-url>
```

# Install dependencies using poetry
```bash
cd <directory that contains tinyg_tester>
poetry install
```

## Usage

# Activate the virtual environment
```bash
cd <directory that contains tinyg_tester>
poetry run python -m tinyg_tester.cli.main --config config/example.yaml
```