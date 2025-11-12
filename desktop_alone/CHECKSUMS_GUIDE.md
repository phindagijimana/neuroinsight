# Checksum Verification Guide

**How to verify your NeuroInsight download is authentic and untampered** 🔒

---

## 🎯 Why Verify Checksums?

Checksums ensure:
- ✅ File downloaded correctly (no corruption)
- ✅ File hasn't been tampered with
- ✅ You have the exact file the developers created

**Always verify checksums before installing!** This is a security best practice.

---

## 📍 Where Are the Checksum Files?

### **The checksums are INSIDE the artifact zip files!**

When you download an artifact from GitHub Actions, you get:

### Linux Artifact
```
neuroinsight-linux.zip
├── NeuroInsight-1.3.9.AppImage     (2.74 GB) ← The app
└── checksums-linux.txt             (86 bytes) ← The checksum ✅
```

### macOS Artifact
```
neuroinsight-mac.zip
├── NeuroInsight-1.3.9.dmg          (450 MB) ← The installer
├── NeuroInsight-1.3.9-arm64.dmg    (450 MB) ← Apple Silicon version
└── checksums-mac.txt               (155 bytes) ← The checksum ✅
```

### Windows Artifact
```
neuroinsight-windows.zip
├── NeuroInsight-Setup-1.3.8.exe    (200 MB) ← The installer
└── checksums-windows.txt           (98 bytes) ← The checksum ✅
```

---

## 📥 Step-by-Step: Download & Verify

### Step 1: Download the Artifact

1. Go to: https://github.com/phindagijimana/neuroinsight/actions
2. Click on latest successful workflow run
3. Scroll to bottom → "Artifacts" section
4. Download your platform's artifact

### Step 2: Extract the Zip

**All platforms:**
- Extract/unzip the downloaded file
- You'll see **2 files**: the installer AND the checksum file

### Step 3: Verify Checksum

Choose your platform:

---

## 🐧 Linux Verification

### Method 1: Automatic (Recommended)

```bash
# Navigate to extracted folder
cd ~/Downloads/neuroinsight-linux

# Verify automatically
sha256sum -c checksums-linux.txt
```

**Expected output:**
```
NeuroInsight-1.3.9.AppImage: OK ✅
```

### Method 2: Manual

```bash
# Calculate hash of downloaded file
sha256sum NeuroInsight-1.3.9.AppImage

# View expected hash
cat checksums-linux.txt

# Compare the hashes - they should match!
```

**Example:**
```bash
$ sha256sum NeuroInsight-1.3.9.AppImage
a1b2c3d4e5f6...  NeuroInsight-1.3.9.AppImage

$ cat checksums-linux.txt
a1b2c3d4e5f6...  NeuroInsight-1.3.9.AppImage

# ✅ They match! Safe to install.
```

---

## 🍎 macOS Verification

### Method 1: Automatic (Recommended)

```bash
# Navigate to extracted folder
cd ~/Downloads/neuroinsight-mac

# Verify automatically
shasum -a 256 -c checksums-mac.txt
```

**Expected output:**
```
NeuroInsight-1.3.9.dmg: OK ✅
NeuroInsight-1.3.9-arm64.dmg: OK ✅
```

### Method 2: Manual

```bash
# Calculate hash of downloaded DMG
shasum -a 256 NeuroInsight-1.3.9.dmg

# View expected hash
cat checksums-mac.txt

# Compare - they should match!
```

**Example:**
```bash
$ shasum -a 256 NeuroInsight-1.3.9.dmg
x1y2z3a4b5c6...  NeuroInsight-1.3.9.dmg

$ cat checksums-mac.txt
x1y2z3a4b5c6...  NeuroInsight-1.3.9.dmg

# ✅ They match! Safe to install.
```

---

## 🪟 Windows Verification

### Method 1: Automatic (Recommended)

```powershell
# Navigate to extracted folder
cd ~\Downloads\neuroinsight-windows

# Run verification script
$expected = (Get-Content checksums-windows.txt).Split()[0]
$actual = (Get-FileHash "NeuroInsight-Setup-1.3.8.exe" -Algorithm SHA256).Hash
if ($expected -eq $actual) { 
    Write-Host "✅ Checksum verified! Safe to install." -ForegroundColor Green 
} else { 
    Write-Host "❌ Checksum MISMATCH! Do not install!" -ForegroundColor Red 
}
```

**Expected output:**
```
✅ Checksum verified! Safe to install.
```

### Method 2: Manual

```powershell
# Calculate hash
Get-FileHash "NeuroInsight-Setup-1.3.8.exe" -Algorithm SHA256

# View expected hash
Get-Content checksums-windows.txt

# Compare manually
```

**Example:**
```powershell
PS> Get-FileHash "NeuroInsight-Setup-1.3.8.exe" -Algorithm SHA256

Algorithm       Hash
---------       ----
SHA256          F1E2D3C4B5A6...

PS> Get-Content checksums-windows.txt
F1E2D3C4B5A6...  NeuroInsight-Setup-1.3.8.exe

# ✅ They match! Safe to install.
```

---

## ❌ What If Checksums Don't Match?

### **DO NOT INSTALL!**

If you see:
```
❌ Checksum MISMATCH!
```

**This means:**
- File was corrupted during download
- File was tampered with
- Wrong file downloaded

### **Steps to fix:**

1. **Delete the downloaded file**
   ```bash
   # Do not install it!
   ```

2. **Clear browser cache**
   ```bash
   # Or use incognito/private mode
   ```

3. **Download again**
   - From official GitHub Actions page
   - Verify URL is correct: `github.com/phindagijimana/neuroinsight`

4. **Verify checksum again**
   - Should match this time

5. **Still doesn't match?**
   - Report issue on GitHub
   - Include: OS, browser, download method
   - Wait for response before installing

---

## 📋 Checksum File Format

### What's Inside checksums-*.txt?

**Linux (`checksums-linux.txt`):**
```
a1b2c3d4e5f6789012345678901234567890123456789012345678901234  NeuroInsight-1.3.9.AppImage
```

**macOS (`checksums-mac.txt`):**
```
x1y2z3a4b5c6d7e8f9012345678901234567890123456789012345678  NeuroInsight-1.3.9.dmg
m1n2o3p4q5r6s7t8u9012345678901234567890123456789012345678  NeuroInsight-1.3.9-arm64.dmg
```

**Windows (`checksums-windows.txt`):**
```
F1E2D3C4B5A6789012345678901234567890123456789012345678901234  NeuroInsight-Setup-1.3.8.exe
```

**Format:**
```
<SHA256-hash> <space> <filename>
```

- **SHA256 hash**: 64 hexadecimal characters
- **Filename**: Name of the file to verify

---

## 🔍 Understanding SHA256

**SHA256** is a cryptographic hash function that:
- Creates a unique "fingerprint" for a file
- Any tiny change → completely different hash
- Impossible to reverse (can't recreate file from hash)
- Collision-resistant (two files won't have same hash)

**Example:**
```
File: "Hello"          → Hash: 185f8db32271fe...
File: "Hello!"         → Hash: 334d016f755cd6...  (completely different!)
```

This is why it's perfect for verifying file integrity!

---

## 🎓 Advanced: Verify via GitHub Releases

### Alternative: Download checksums from GitHub Releases

Checksums are also available in the GitHub Release:

1. Go to: https://github.com/phindagijimana/neuroinsight/releases
2. Click on latest release (e.g., `desktop-v1.3.9`)
3. Download the checksum file:
   - `checksums-linux.txt`
   - `checksums-mac.txt`
   - `checksums-windows.txt`

**Note:** Installers are too large for GitHub Releases (>2GB), so:
- Download **installers** from Actions artifacts
- Download **checksums** from Releases (or from artifacts)
- Verify locally

---

## 📊 Checksum Verification Checklist

Before installing, verify:

- [ ] Downloaded artifact from official GitHub Actions
- [ ] Extracted zip file completely
- [ ] Found BOTH installer and checksums-*.txt file
- [ ] Ran checksum verification command
- [ ] Got "OK" or "Checksum verified!" message
- [ ] Checksums match (if manually verified)

**Only proceed if ALL checkboxes are ✅**

---

## 🔗 Official Download Links

**Trusted sources only:**

- **GitHub Actions**: https://github.com/phindagijimana/neuroinsight/actions
- **GitHub Releases**: https://github.com/phindagijimana/neuroinsight/releases
- **Repository**: https://github.com/phindagijimana/neuroinsight

**Never download from:**
- Third-party sites
- File sharing services
- Unofficial mirrors
- Email attachments

---

## 💡 Pro Tips

1. **Always verify** - Even if you trust the source, verify checksums
2. **Save checksums** - Keep the checksum file for your records
3. **Re-verify after transfer** - If you copy to another machine, verify again
4. **Check the URL** - Make sure you're on `github.com/phindagijimana/neuroinsight`
5. **Use automatic verification** - Less prone to human error

---

## 🆘 Troubleshooting

### Issue: "Command not found"

**Linux/macOS:**
```bash
# sha256sum not found? Try:
shasum -a 256 filename

# shasum not found? Try:
openssl dgst -sha256 filename
```

**Windows:**
```powershell
# PowerShell 3.0+ required
# Check version:
$PSVersionTable.PSVersion

# If old PowerShell, use certutil:
certutil -hashfile filename SHA256
```

### Issue: "File not found"

```bash
# Make sure you're in the right directory
ls -la

# Or use full path
sha256sum /full/path/to/NeuroInsight-1.3.9.AppImage
```

### Issue: Checksum file is empty

```bash
# Check file size
ls -lh checksums-*.txt

# If 0 bytes:
# 1. Re-download the artifact
# 2. Extract completely
# 3. Try again
```

---

## 📞 Getting Help

If checksums don't match or you have issues:

1. **DO NOT install the file**
2. **Report the issue**:
   - GitHub Issues: https://github.com/phindagijimana/neuroinsight/issues
   - Include: OS, file size, download method
3. **Wait for confirmation** before installing

---

## ✅ Summary

**Quick checklist:**

```bash
# 1. Download artifact
# 2. Extract zip
# 3. Verify checksum:

# Linux:
sha256sum -c checksums-linux.txt

# macOS:
shasum -a 256 -c checksums-mac.txt

# Windows:
$e=(Get-Content checksums-windows.txt).Split()[0]; $a=(Get-FileHash "NeuroInsight*.exe" -Algorithm SHA256).Hash; if($e -eq $a){"✅ OK"}else{"❌ BAD"}

# 4. If OK → Install
# 5. If BAD → Delete & re-download
```

---

**Last Updated**: November 12, 2025  
**Latest Version**: 1.3.9  
**Hash Algorithm**: SHA256

---

**Stay safe! Always verify your downloads! 🔒**


