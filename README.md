# SecureWipe
# SecureErase Prototype

A Python-based **secure data wiping prototype**, designed for **Smart India Hackathon (SIH)** demos. Supports **full-disk cryptographic erasure** (for SSDs) and **file-level crypto-shredding**, with verifiable certificates for compliance.

---

## ✨ Features
- **Full SSD Erasure**
  - ATA Secure Erase (via `hdparm`)  
  - NVMe Crypto Erase (via `nvme-cli`)  
  - Auto-detection of device type  
  - Dry-run simulation for safe demos  
- **File-level Crypto-Shred**
  - AES-GCM encryption with a one-time key  
  - Chunked encryption for large files  
  - Replaces original file with securely shredded data  
  - Generates **JSON + PDF certificates** with key fingerprint & metadata  
- **Certificates**
  - Timestamped PDF + JSON for audit & compliance  
  - Dry-run still generates demo certificates for safe demos  
- **Interactive Mode**
  - Guided menu for safe demonstrations  
  - Allows full SSD erase or file crypto-shred in a controlled environment  

---

## ⚙️ Requirements
- **System Tools**
  - `hdparm` (for ATA SSDs)  
  - `nvme-cli` (for NVMe SSDs)  
- **Python Packages**
```bash
pip install reportlab cryptography


## 🚀 Usage

### 1. Interactive Mode (Safe Demo)
```bash
python secure_wipe.py --interactive --dry-run
```

### 2. Full SSD Erasure
- For **NVMe** SSDs:
  ```bash
  sudo python secure_wipe.py --device /dev/nvme0n1 --nvme
  ```
- For **ATA** SSDs:
  ```bash
  sudo python secure_wipe.py --device /dev/sda
  ```

⚠️ **Warning:** These operations are destructive — use only on disposable test drives.

### 3. File-level Crypto-Shred
- Safe demo (no overwrite):
  ```bash
  python secure_wipe.py --cryptoshred --file /path/to/test.txt --dry-run
  ```
- Real crypto-shred (irreversible):
  ```bash
  python secure_wipe.py --cryptoshred --file /path/to/test.txt
  ```

Certificates are stored in the `certificates/` directory.

---

## 📂 Project Structure
```
secure_wipe.py   # Main prototype script
certificates/               # Generated PDF + JSON certificates
```

---

## 🛡️ Limitations
Full SSD erase requires root privileges.

Effectiveness of TRIM/overwrite may vary by SSD firmware.

Currently prototype-only; for production: add GUI, vendor-specific support, and advanced logging.
---

## 🎯 SIH Pitch Angle
> “SecureWipe provides two-layer data sanitization: enterprise-grade disk-level crypto-erase for IT asset disposal, and user-friendly file-level crypto-shredding for everyday use. Both operations generate verifiable certificates, bridging compliance with usability.”

---

## 👨‍💻 Authors
Developed by Team **ZeroTrace** for **Smart India Hackathon (SIH)**.
