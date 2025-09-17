#!/usr/bin/env python3
import argparse
import os
import subprocess
import json
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import secrets
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Certificate output directory
CERT_DIR = "certificates"
os.makedirs(CERT_DIR, exist_ok=True)

def generate_certificate(metadata, prefix):
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    base = f"{prefix}_{ts}"
    json_path = os.path.join(CERT_DIR, f"{base}.json")
    pdf_path = os.path.join(CERT_DIR, f"{base}.pdf")

    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=4)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "SecureErase Certificate")
    y = 730
    for k, v in metadata.items():
        c.drawString(100, y, f"{k}: {v}")
        y -= 20
    c.showPage()
    c.save()

    print(f"[+] Certificate generated: {json_path}, {pdf_path}")

def full_disk_erase(device, is_nvme, dry_run):
    if dry_run:
        print(f"[DRY-RUN] Would securely erase device: {device}")
        return

    # Extra safeguard confirmation
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

    if dry_run:
        print(f"[DRY-RUN] Would crypto-shred file: {file_path}")
        return

    key = secrets.token_bytes(32)
    iv = secrets.token_bytes(16)

    with open(file_path, "rb") as f:
        data = f.read()

    encryptor = Cipher(
        algorithms.AES(key),
        modes.CFB(iv),
        backend=default_backend()
    ).encryptor()

    ciphertext = encryptor.update(data) + encryptor.finalize()

    with open(file_path, "wb") as f:
        f.write(ciphertext)

    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(key)
    fingerprint = digest.finalize().hex()

    metadata = {
        "operation": "crypto-shred",
        "target": file_path,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "key_fingerprint": fingerprint,
        "status": "completed"
    }
    generate_certificate(metadata, "file_shred")

def main():
    parser = argparse.ArgumentParser(description="Secure Erase Prototype")
    parser.add_argument("--device", help="Target device (e.g., /dev/sda, /dev/nvme0n1)")
    parser.add_argument("--nvme", action="store_true", help="Specify NVMe device")
    parser.add_argument("--cryptoshred", action="store_true", help="Perform file crypto-shred")
    parser.add_argument("--file", help="Target file for crypto-shred")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes")
    args = parser.parse_args()

    if args.device:
        full_disk_erase(args.device, args.nvme, args.dry_run)
    elif args.cryptoshred and args.file:
        file_crypto_shred(args.file, args.dry_run)
    else:
        print("[!] No valid operation specified. Use --help for options.")

if __name__ == "__main__":
    main()
