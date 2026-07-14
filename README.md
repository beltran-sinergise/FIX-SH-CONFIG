# SentinelHub Legend Configuration Fixer

This tool fixes legend color formatting issues in Sentinel Hub configurations.

## Quick Start

### 1. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

Create or edit a `conf` file in the repository root with your Sentinel Hub credentials:

```
sh_client_id="your_sh_client_id"
sh_client_secret="your_sh_client_secret"
```

See the following guide on how to obtain your [SH credentials](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html).

### 4. Run the Script

**Fix all configurations:**
```bash
python fix_legends.py --update-all
```

**Dry run:**
```bash
python fix_legends.py --dry-run --update-all
```

**Fix specific configurations:**
```bash
python fix_legends.py --update-list config_id_1 config_id_2
```

**Use a custom configuration file:**
```bash
python fix_legends.py --update-all --conf path/to/your/conf
```

**Only update CLMS configurations (filters by name):**
```bash
python fix_legends.py --update-all --clms-only
```

**Combine options:**
```bash
python fix_legends.py --update-all --clms-only --dry-run
```

**Notes:**
- `--dry-run` shows what would be updated without making API changes
- `--clms-only` filters configurations to only CLMS products (config name must contain 'CLMS' or 'clms')
- Both flags work with `--update-all` and `--update-list`

## Recommended Workflow

1. **Preview changes first with dry-run mode:**
   ```bash
   python fix_legends.py --update-all --clms-only --dry-run
   ```
   This inspects all CLMS configurations and logs which ones contain errors and would be updated, without making any API changes.

2. **Apply the fixes:**
   ```bash
   python fix_legends.py --update-all --clms-only
   ```
   This applies the legend color format fixes to all CLMS configurations.

## What It Does

The script automatically:
- Identifies layers with legend color formatting errors
- Converts color formats to the correct specification
- Fixes gradient color definitions
- Validates changes against Sentinel Hub WMS services

## Configuration File Format

The `conf` file should contain your Sentinel Hub OAuth credentials:

```
sh_client_id="<your-client-id>"
sh_client_secret="<your-client-secret>"
```

The script reads this file to authenticate with Sentinel Hub and update your configurations.

## Dependencies

- Python 3.7+
- sentinelhub SDK
- requests, pydantic, and other standard libraries (see `requirements.txt`)
