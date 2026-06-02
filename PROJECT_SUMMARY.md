# KazaALKIS Project Summary

KazaALKIS is a Windows-local daily Greek calendar notification application.
It is not an official Kazamias publication. Publishable records must be
public-domain, open-data, or user-entered content with provenance metadata.

## Locations

- Project source and SQLite data: this project directory
- Python environment: `E:\AI\venvs\KazaALKIS`
- Logs: `E:\AI\logs\KazaALKIS`
- Exports: `E:\AI\outputs\KazaALKIS`
- Cache, tools, models, and temporary resources: configurable `E:\AI`
  subdirectories

## Main Components

- `KazaALKIS.ps1`: AI workspace setup, launch, disk status, and scheduling
- `KazaALKIS_launcher.py`: interactive application menu
- `src/database.py`: schema, migrations, provenance, and duplicate checks
- `src/data_importer.py`: open-data and manual import workflows
- `src/message_builder.py`: daily message composition
- `src/whatsapp_notifier.py`: Cloud API, Twilio, and masked manual delivery
- `src/logger_dashboard.py`: operational and validation dashboards
- `src/calendar_exporter.py`: masked logs and nameday exports
- `tests/`: regression suite

## Publication Gate

Bundled sample records are assigned an `UNKNOWN - DO NOT PUBLISH` source and
remain flagged for manual review. Replace or review those records before using
them for public messages.

## Start

```powershell
.\KazaALKIS.ps1
```
