# KazaALKIS Quick Reference Card

## 🚀 Quick Start

### Setup
```bash
cd E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS
setup_kazaalkis.bat
```

### Launch
```bash
python KazaALKIS_launcher.py
```

---

## 📋 Menu Options

| # | Option | Description |
|---|--------|-------------|
| 1 | Setup project | Initialize database & config |
| 2 | Import database | Load external Kazamias data |
| 3 | Preview message | View today's message |
| 4 | Send message | Send to all contacts |
| 5 | Test message | Send to single contact |
| 6 | Edit contacts | Manage contact list |
| 7 | View logs | Show recent messages |
| 8 | Configuration | View current settings |
| 9 | Exit | Quit application |

---

## 🌍 Language Codes

| Language | Code |
|----------|------|
| English | `en` |
| Greek | `gr` |
| Bilingual | `bilingual` |

---

## 🎭 Tone Options

| Tone | Code |
|------|------|
| Formal | `formal` |
| Friendly | `friendly` |
| Traditional | `traditional` |
| Humorous | `humorous` |

---

## 📱 WhatsApp Providers

| Provider | Code |
|----------|------|
| WhatsApp Business Cloud | `whatsapp_business_cloud` |
| Twilio | `twilio` |
| Manual | `manual` |

---

## 🗂️ File Locations

| Component | Path |
|-----------|------|
| Project Root | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS` |
| Database | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS\data\kazaalkis.db` |
| Config | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS\config\` |
| Logs | `E:\AI\logs\KazaALKIS\` |
| Dependencies | `requirements.txt` installed into `E:\AI\venvs\KazaALKIS\` |

---

## 🔐 Environment Variables (.env)

```bash
# WhatsApp Business Cloud
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account

# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=+1234567890
```

---

**Version:** 1.0.0
**Last Updated:** June 1, 2026
