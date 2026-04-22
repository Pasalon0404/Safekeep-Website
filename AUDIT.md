# SafeKeep OS v1.1b - Audit Guide

Welcome, paranoid reviewer. This document maps how SafeKeep OS is locked down and built, allowing you to trace the final bootable `.img` file back to its source scripts.

## 1. The UI & Cryptography (Web App Layer)
The entire user interface, BIP-85 derivation, SeedXOR Tool, Shamir Backups, and PSBT Signer logic occur completely offline in the browser. All poetic legacy terminology has been scrubbed in favor of literal, descriptive labels.
* **Pre-bundled Source:** `/src/` and `/seed-xor-tool/` directories.
* **The Final Artifact:** `/seed-xor-tool/boot.html` (The compiled UI. Note the strict GTK file chooser lockdowns and hardcoded `file://` directory targets).

## 2. The OS Build & Hardening Layer
The Ubuntu environment is heavily stripped and locked down to prevent network leaks, unauthorized mounting, and file-picker escapes.
* **Partitioning & Boot:** `build.sh` (Maps partition sizes, LUKS container math, and OS structure).
* **Package Lockdown:** `chroot-setup.sh` (Lists exactly which apt packages are installed, and forcefully purges `gvfs` to kill virtual network mounts).
* **Security & Sandboxing:** `safekeep-harden.sh` (Review this for module blacklists like Bluetooth/Wi-Fi, masked systemd services, polkit rules, and the immutable GTK file-chooser jail).
* **Drive Hiding:** `/config/99-hide-drives.rules` (The specific udev rules to hide internal host drives).

## 3. The Runtime & Vault Execution
How the OS handles the encrypted vault, manages the transfer drive, and launches the amnesic kiosk on boot.
* **Boot Wrapper:** `safekeep-boot.sh` (Detects first-boot state, manages encrypted daemons, fences systemd race conditions, and launches Chromium with kiosk flags).
* **LUKS Container:** `setup-vault.sh` & `unlock-vault.sh` (Verifies the `safekeep-data` label, iter-time parameters, and handles clean power-offs for sneakernet transfers).

## Integrity Verification
Included in this source tree is a `SHA256SUMS.txt` containing the hash of the release artifacts. You can verify the integrity of the standalone release using the clear-signed `SHA256SUMS.txt.asc` provided alongside the download.