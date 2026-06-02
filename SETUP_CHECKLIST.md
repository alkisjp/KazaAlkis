# KazaALKIS Installation & Setup Checklist

## ✅ Pre-Installation Requirements

- [ ] Windows 10 or later
- [ ] Python 3.8+ installed and in PATH
- [ ] Administrator privileges available
- [ ] Internet connection for API setup
- [ ] ~500MB disk space available
- [ ] WhatsApp Business API credentials (if using cloud API)

---

## 📦 Installation Steps

### Phase 1: Verify Locations

- [ ] Project location: `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS`
- [ ] Dependencies installed from project `requirements.txt`
- [ ] Project directories created:
  - [ ] `data/`
  - [ ] `config/`
  - [ ] `logs/`
  - [ ] `src/`

### Phase 2: Automated Setup

- [ ] Navigate to: `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS`
- [ ] Run: `setup_kazaalkis.bat`
- [ ] Virtual environment created: `E:\AI\venvs\KazaALKIS\`
- [ ] All dependencies installed into: `E:\AI\venvs\KazaALKIS\`
- [ ] Database initialized

**Or Manual Alternative:**
```bash
cd E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS
.\KazaALKIS.ps1 -Action Setup
```

### Phase 3: Initial Configuration

- [ ] Run: `python KazaALKIS_launcher.py`
- [ ] Select: Option 1 - Setup project
- [ ] Complete interactive setup wizard

### Phase 4: WhatsApp API Setup

- [ ] Run: `python KazaALKIS_launcher.py`
- [ ] Setup WhatsApp API credentials
- [ ] Credentials stored in `config/.env`
- [ ] Verify .env file is in .gitignore

### Phase 5: Contacts Configuration

- [ ] Open: `data/contacts.json`
- [ ] Add contact entries
- [ ] Include phone numbers with country code
- [ ] Verify JSON format is valid

### Phase 6: Testing

- [ ] Run: `python KazaALKIS_launcher.py`
- [ ] Select: Option 3 - Preview message
- [ ] Select: Option 5 - Send test message
- [ ] Verify message arrives on WhatsApp

---

## ✨ Success Criteria

Setup is complete when:
- [ ] Python launcher opens without errors
- [ ] Database loads successfully
- [ ] Configuration is valid
- [ ] Preview message displays correctly
- [ ] Test message arrives on WhatsApp

---

## 📍 File Locations Summary

| Component | Location |
|-----------|----------|
| **Project Directory** | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS` |
| **Database** | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS\data\kazaalkis.db` |
| **Dependencies** | `requirements.txt` installed into `E:\AI\venvs\KazaALKIS\` |
| **Configuration** | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS\config\` |
| **Logs** | `E:\AI\logs\KazaALKIS\` |
| **Source Code** | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS\src\` |
| **Data** | `E:\07_050_Workspaces_Code_Projects(latest)\KazaALKIS\data\` |

---

**Setup Guide Version:** 1.0.0
**Date:** June 1, 2026
**Status:** ✅ Ready for Use
