# Product Export System

A Python-based system for exporting product data from the warranty database to Shopify using group IDs as the primary identifier.

## Features

- Group ID-based product processing (e.g., GID-100968, LGD-102654)
- Atomic Shopify operations to prevent product locking
- Comprehensive error handling and retry mechanisms
- Configurable environment-based settings
- Modular architecture for maintainability
- Support for product images (placeholder for future implementation)
- Efficient batch processing for large datasets

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` with your configuration

## Configuration

The system uses YAML configuration files with environment variable substitution. See `config/config.yaml` for the configuration structure and `.env.example` for required environment variables.

## Usage

### Process Specific Group IDs
```bash
python src/main.py LGD-101792 GID-100288 LGD-100040
```

### Process All Group IDs
```bash
python src/main.py --all
```

### Dry Run (Validate without creating products)
```bash
python src/main.py LGD-101792 --dry-run
```

### Verbose Logging
```bash
python src/main.py LGD-101792 --verbose
```

## Project Structure

```
src/
├── core/           # Core business logic
├── models/         # Data models
├── utils/          # Utility modules
├── mapping/        # Data mapping logic
└── main.py         # CLI entry point

config/
├── config.yaml     # Configuration file
└── .env.example    # Environment variables template

tests/              # Test files
docs/               # Documentation
logs/               # Log files
```

## Testing

Run tests with:
```bash
pytest
```

## Development

The system follows the specification outlined in `specs/PRODUCT_EXPORT_SYSTEM_SPEC.md` and integrates with the existing warranty database and Shopify API using MCP servers.
