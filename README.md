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

**Fix specific configurations:**
```bash
python fix_legends.py --update-list config_id_1 config_id_2
```

**Use a custom configuration file:**
```bash
python fix_legends.py --update-all --conf path/to/your/conf
```

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

## Typical Workflow

1. **Identify problem configurations** - Run with `--update-all` to automatically detect and fix issues
2. **Verify fixes** - The script logs all changes and validates against the Sentinel Hub API
3. **Check specific layers** - Use the diagnostic functions in `src/utils.py` for manual inspection if needed

## Dependencies

- Python 3.7+
- sentinelhub SDK
- requests, pydantic, and other standard libraries (see `requirements.txt`)
