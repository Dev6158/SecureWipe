# SecureWipe
# SecureErase Prototype

A Python-based prototype tool for **secure data wiping**, designed for SIH demonstration purposes. It supports both **full-disk cryptographic erasure** (for SSDs) and **single-file crypto-shredding** (file-level secure erase).

---

## ✨ Features
- **Full SSD Erasure**
  - ATA Secure Erase (via `hdparm`)
  - NVMe Crypto Erase (via `nvme-cli`)
  - Auto-detection of device type
  - Dry-run simulation for safe demos
- **File-level Crypto-shred**
  - Encrypts file with a one-time AES-GCM key, then destroys the key
  - Replaces original file with encrypted garbage data
  - Generates a **JSON + PDF certificate** containing key fingerprint & metadata
- **Certificates**
  - Timestamped PDF + JSON records for compliance & audit
- **Demo Friendly**
  - `--dry-run` mode for showing judges workflow without destructive actions

---

## ⚙️ Requirements
- **System Tools**
  - `hdparm` (for ATA SSDs)
  - `nvme-cli` (for NVMe SSDs)
- **Python Packages**
  ```bash
  pip install reportlab cryptography
  ```

---

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
- File-level shred currently loads entire file into RAM (prototype limitation).
- Requires root privileges for actual disk erasure.
- Effectiveness of TRIM/overwrite operations depends on SSD firmware.
- For production: implement chunked streaming encryption, GUI frontend, and vendor-specific support.

---

## 🎯 SIH Pitch Angle
> “Our tool provides **two-layer secure data sanitization**: enterprise-grade disk-level crypto-erase for IT asset disposal, and user-friendly file-level crypto-shredding for everyday use. Both produce verifiable certificates, bridging compliance with usability.”

---

## 👨‍💻 Authors
Developed by Team **ZeroTrust** for **Smart India Hackathon (SIH)**.
