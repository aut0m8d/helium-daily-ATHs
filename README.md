# Day-of-Week Records

`day_of_week_records.py` prints every date whose total data usage set a fresh record for its weekday at the moment it happened. The script pulls live Helium Mobile metrics so there is nothing to maintain locally.

## Requirements

- Python 3.8+ (any recent CPython should work)
- Internet access (the script fetches JSON from Helium Mobile’s public S3 bucket)

## Usage

```bash
python3 day_of_week_records.py
```

The script downloads the latest `daily_total_data_tb_all_carriers_6mo_hist.json`, computes weekday-specific records in chronological order, and renders a formatted table directly to stdout.

### Optional flags

- `--json-url`: use a different JSON endpoint. Example:

  ```bash
  python3 day_of_week_records.py --json-url https://example.com/custom.json
  ```

### Tip

If you need to inspect or reuse the dataset offline, save the remote JSON to disk yourself; the script intentionally avoids touching local files to stay up-to-date automatically.
