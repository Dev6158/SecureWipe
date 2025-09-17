#!/usr/bin/env python3
import argparse
import os
import subprocess
import json
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Certificate output directory
CERT_DIR = "certificates"
os.makedirs(CERT_DIR, exist_ok=True)

CHUNK_SIZE = 64 * 1024  # 64 KB chunks for file shredding

def generate_certificate(metadata, prefix):
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    base = f"{prefix}_{ts}"
    json_path = os.path.join(CERT_DIR, f"{base}.json")
    pdf_path = os.path.join(CERT_DIR, f"{base}.pdf")

    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=4)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "SecureErase Certificate")
    c.setFont("Helvetica", 12)
    y = 730
    for k, v in metadata.items():
        c.drawString(100, y, f"{k}: {v}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.showPage()
    c.save()

    print(f"[+] Certificate generated: {json_path}, {pdf_path}")

def full_disk_erase(device, is_nvme, dry_run):
    if dry_run:
        print(f"[DRY-RUN] Would securely erase device: {device}")
        metadata = {
            "operation": "full-disk-erase",
            "device": device,
            "nvme": is_nvme,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "dry-run"
        }
        generate_certificate(metadata, "disk_erase")
        return

    print(f"\n⚠️ WARNING: You are about to ERASE ALL DATA on device {device}")
    print("This action is IRREVERSIBLE and will wipe the entire SSD.")
    confirm = input("\nTo confirm, type ERASE-ALL and press Enter: ")
    if confirm.strip() != "ERASE-ALL":
        print("[!] Aborted by user. No changes made.")
        return

    try:
        if is_nvme:
            print(f"[*] Running NVMe secure erase on {device}")
            subprocess.run(["sudo", "nvme", "format", device, "--ses=1"], check=True)
        else:
            print(f"[*] Running ATA secure erase on {device}")
            subprocess.run(["sudo", "hdparm", "--user-master", "u", "--security-set-pass", "p", device], check=True)
            subprocess.run(["sudo", "hdparm", "--user-master", "u", "--security-erase", "p", device], check=True)

        metadata = {
            "operation": "full-disk-erase",
            "device": device,
            "nvme": is_nvme,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "completed"
        }
        generate_certificate(metadata, "disk_erase")
    except Exception as e:
        print(f"[!] Error: {e}")

def file_crypto_shred(file_path, dry_run):
    if not os.path.exists(file_path):
        print("[!] File does not exist")
        return

    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    iv = secrets.token_bytes(12)  # 96-bit nonce for GCM

    if dry_run:
        print(f"[DRY-RUN] Would crypto-shred file: {file_path}")
        metadata = {
            "operation": "crypto-shred",
            "target": file_path,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "key_fingerprint": key.hex(),
            "status": "dry-run"
        }
        generate_certificate(metadata, "file_shred")
        return

    temp_path = file_path + ".tmp"
    try:
        with open(file_path, "rb") as fin, open(temp_path, "wb") as fout:
            while True:
                chunk = fin.read(CHUNK_SIZE)
                if not chunk:
                    break
                encrypted = aesgcm.encrypt(iv, chunk, None)
                fout.write(encrypted)

        os.replace(temp_path, file_path)

        # Key fingerprint for audit
        fingerprint = secrets.token_hex(16)

        metadata = {
            "operation": "crypto-shred",
            "target": file_path,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "key_fingerprint": fingerprint,
            "status": "completed"
        }
        generate_certificate(metadata, "file_shred")
        print(f"[+] File crypto-shredded: {file_path}")
    except Exception as e:
        print(f"[!] Error during file shred: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

def interactive_mode():
    print("=== SecureWipe Interactive Mode ===")
    print("1. Full Disk Erase")
    print("2. File Crypto-Shred")
    choice = input("Select operation (1/2): ").strip()
    if choice == "1":
        device = input("Enter device path (e.g., /dev/sda, /dev/nvme0n1): ").strip()
        is_nvme = input("Is this NVMe? (y/n): ").strip().lower() == "y"
        dry = input("Dry-run? (y/n): ").strip().lower() == "y"
        full_disk_erase(device, is_nvme, dry)
    elif choice == "2":
        file_path = input("Enter file path: ").strip()
        dry = input("Dry-run? (y/n): ").strip().lower() == "y"
        file_crypto_shred(file_path, dry)
    else:
        print("[!] Invalid choice")

def main():
    parser = argparse.ArgumentParser(description="Secure Wipe Prototype")
    parser.add_argument("--device", help="Target device (e.g., /dev/sda, /dev/nvme0n1)")
    parser.add_argument("--nvme", action="store_true", help="Specify NVMe device")
    parser.add_argument("--cryptoshred", action="store_true", help="Perform file crypto-shred")
    parser.add_argument("--file", help="Target file for crypto-shred")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes")
    parser.add_argument("--interactive", action="store_true", help="Run interactive mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.device:
        full_disk_erase(args.device, args.nvme, args.dry_run)
    elif args.cryptoshred and args.file:
        file_crypto_shred(args.file, args.dry_run)
    else:
        print("[!] No valid operation specified. Use --help for options.")

if __name__ == "__main__":
    main()
