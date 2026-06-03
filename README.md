# KazaALKIS
## Daily Greek Calendar and Proverb Notifications

KazaALKIS is a local Windows application that builds a daily Greek calendar
message and can deliver it through WhatsApp Business Cloud API, Twilio
WhatsApp, or a manual TXT export.

The initial default is manual TXT export mode. Live WhatsApp sending remains
disabled until the operator selects a provider and enters credentials through
the setup menu.

KazaALKIS is not an official Kazamias publication. Its publishable data must
come from public-domain, open-data, or user-entered sources with recorded
provenance.

## Storage Layout

Project source and the local SQLite database remain in this project directory.
Runtime resources default to `E:\AI` and can be overridden with environment
variables:

| Resource | Default |
| --- | --- |
| Models | `E:\AI\models` |
| Ollama models | `E:\AI\models\ollama` |
| Caches | `E:\AI\cache` |
| Python environments | `E:\AI\venvs` |
| Logs | `E:\AI\logs\KazaALKIS` |
| Exports | `E:\AI\outputs\KazaALKIS` |
| Temporary files | `E:\AI\tmp\KazaALKIS` |
| Vector stores | `E:\AI\vectorstore` |
| Tools | `E:\AI\tools` |

Supported overrides include `AI_ROOT`, `AI_MODELS`, `AI_CACHE`, `AI_OUTPUTS`,
`AI_VENVS`, `AI_LOGS`, `AI_TMP`, `AI_VECTORSTORE`, and `AI_TOOLS`.

## Setup

Run the PowerShell launcher:

```powershell
.\KazaALKIS.ps1
```

Useful direct commands:

```powershell
.\KazaALKIS.ps1 -Action Status
.\KazaALKIS.ps1 -Action Setup
.\KazaALKIS.ps1 -Action Run
.\KazaALKIS.ps1 -Action Schedule -SendTime "08:00"
.\KazaALKIS.ps1 -Action DisableSchedule
```

The launcher creates missing `E:\AI` subfolders, reports free disk space,
warns about legacy repo-local environments, and uses `E:\AI\venvs\KazaALKIS`.

## Open-Data Workflow

The SQLite schema records source name, URL, licence, public-domain status,
import date, confidence, and manual-review state. Bundled legacy samples are
marked `UNKNOWN - DO NOT PUBLISH` until their licences are reviewed.

Importer support includes:

- Greek namedays JSON
- CSV proverb lists
- OpenHolidays-compatible JSON APIs
- Wikimedia on-this-day JSON APIs
- Manual Excel import for historical events and custom notes

Use the Python menu's validation dashboard before publishing imported data.
It reports missing sources, missing licences, duplicate names, duplicate
quotes, movable-feast uncertainty, and records needing manual review.

## Privacy

- Store API credentials in `config\.env`.
- Do not put credentials in source files.
- Phone numbers are masked in manual exports and log exports.
- Duplicate daily sends are skipped unless the operator explicitly forces a
  resend.

## Testing

```powershell
python -m pytest -q
python -m compileall -q KazaALKIS_launcher.py src tests
```

## Website Publication

The repository includes `index.html`, `privacy.html`, and `terms.html` for a
static GitHub Pages website. Python menu option `12` writes a public-only daily
payload to:

```text
public_notifications/latest.json
public_notifications/history/YYYY-MM-DD.json
```

The website payload contains calendar content only. It never exports contacts,
phone numbers, API credentials, or delivery logs. Review generated JSON before
committing and pushing it to GitHub.

Menu option `12` generates a bilingual English/Greek commentary draft. Menu
option `13` publishes the approved draft into the website JSON. Menu option
`14` commits and pushes only the public website notification JSON files.

AI commentary providers:

- `template`: safe local fallback, no network.
- `ollama`: local Ollama endpoint, default `http://127.0.0.1:11434`.
- `openai_compatible`: OpenAI-compatible chat-completions endpoint using
  `OPENAI_API_KEY` or `OPENAI_COMPATIBLE_API_KEY`.

## Deployment Assumptions

- Windows has Python 3.8 or newer available for initial environment creation.
- `E:\AI` is the preferred AI workspace root; use `-AIRoot` or `AI_ROOT` to
  override it.
- WhatsApp API credentials and approved message usage remain the operator's
  responsibility.
- Bundled sample records require licence review before publication.
- API-backed imports require network access and should be reviewed before use.
