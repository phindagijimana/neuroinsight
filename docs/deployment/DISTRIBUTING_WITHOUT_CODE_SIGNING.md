# Distributing Software Without Code Signing Certificates
**For Research & Open-Source Software**  
**Cost: $0 (completely free)**

---

## TL;DR: Yes, You Can Skip Code Signing!

For **research software** and **open-source projects**, you can distribute unsigned applications. Users will see security warnings, but you can provide clear instructions to bypass them.

**Trade-off**: Users see scary warnings, but it's FREE and totally acceptable for academic/research software.

---

## Option 1: Distribute Unsigned + Clear Instructions (RECOMMENDED)

### What Users Will See:

#### macOS
```
"NeuroInsight.app" cannot be opened because the developer cannot be verified.
macOS cannot verify that this app is free from malware.
```

#### Windows
```
Windows protected your PC
Windows Defender SmartScreen prevented an unrecognized app from starting.
Running this app might put your PC at risk.
```

#### Linux
```
(No warning - Linux users are comfortable with this)
```

### Solution: Provide Clear Bypass Instructions

**Create**: `INSTALLATION.md`

```markdown
# Installing NeuroInsight (Unsigned Version)

NeuroInsight is open-source research software distributed without 
commercial code signing certificates. This means you'll see security 
warnings during installation - this is normal for academic software.

## macOS Installation

1. Download `NeuroInsight-macos.dmg`

2. Open the DMG file and drag NeuroInsight to Applications

3. When you try to open it, you'll see a security warning. 
   **This is expected for research software.**

4. To bypass the warning:
   - Right-click (or Control+click) on NeuroInsight.app
   - Select "Open" from the menu
   - Click "Open" in the dialog that appears
   - OR: Go to System Preferences → Security & Privacy → 
     Click "Open Anyway"

5. NeuroInsight will now run. You only need to do this once.

**Why this warning?**
We're a research lab, not a commercial company. The $99/year Apple 
Developer certificate is used to fund Apple's app store ecosystem. 
Academic software typically doesn't pay for this.

**Is it safe?**
Yes! Our source code is open and available at:
https://github.com/your-username/neuroinsight

## Windows Installation

1. Download `NeuroInsight-Setup.exe`

2. Run the installer

3. You'll see "Windows protected your PC" warning.
   **This is expected for research software.**

4. To bypass:
   - Click "More info"
   - Click "Run anyway"

5. Complete the installation normally

**Why this warning?**
Microsoft's SmartScreen requires either:
- Extended Validation certificate ($400+/year)
- Established "reputation" (lots of downloads)

Research software rarely has either initially.

**Is it safe?**
Yes! Our source code is open and available at:
https://github.com/your-username/neuroinsight

You can also scan with your antivirus before installing.

## Linux Installation

No warnings! Linux users expect to install from source.

### AppImage
```bash
chmod +x NeuroInsight-x86_64.AppImage
./NeuroInsight-x86_64.AppImage
```

### Debian/Ubuntu (.deb)
```bash
sudo dpkg -i neuroinsight_1.0.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed
```

### From Source
```bash
git clone https://github.com/your-username/neuroinsight.git
cd neuroinsight
./install.sh
```

## Frequently Asked Questions

### Why don't you just get code signing certificates?
Code signing costs $100-500/year and is primarily designed for 
commercial software distribution. Many research labs and open-source 
projects cannot justify this recurring cost.

### How do I know it's safe?
1. Download from official sources only (GitHub releases)
2. Verify checksums (provided with each release)
3. Review source code (fully open-source)
4. Scan with antivirus if concerned
5. Check the GitHub repository for community trust

### Will you get certificates in the future?
If we secure funding or the software becomes widely adopted, 
we may purchase certificates. For now, the software is free 
and open-source.

## Verifying Your Download (Recommended)

### Check SHA256 Checksums

**macOS/Linux:**
```bash
sha256sum NeuroInsight-macos.dmg
# Compare with published checksum
```

**Windows (PowerShell):**
```powershell
Get-FileHash NeuroInsight-Setup.exe -Algorithm SHA256
# Compare with published checksum
```

Published checksums are in `checksums.txt` on the GitHub release page.
```

---

## Option 2: Self-Signing (Free, Slightly Better)

You can create your own certificates for free. Users still see warnings, but they can verify it's always from you.

### macOS: Self-Signed Certificate

```bash
# Create a self-signed certificate
security create-keypair -a RSA -s 2048 -f "/tmp/neuroinsight-key"

# Create certificate signing request
security create-cert-request \
  -c "NeuroInsight Research" \
  -e "your@email.com" \
  -o "/tmp/neuroinsight.csr"

# Sign your app
codesign --deep --force --sign "NeuroInsight Research" \
  "NeuroInsight.app"
```

**Users still see warnings**, but they can verify the signature is consistent across updates.

### Windows: Self-Signed Certificate

```powershell
# Create self-signed certificate (PowerShell as Admin)
$cert = New-SelfSignedCertificate `
  -Subject "CN=NeuroInsight Research" `
  -Type CodeSigning `
  -CertStoreLocation Cert:\CurrentUser\My

# Export certificate
Export-Certificate -Cert $cert -FilePath neuroinsight.cer

# Sign your app
signtool sign /f neuroinsight.pfx /p password /tr http://timestamp.digicert.com NeuroInsight-Setup.exe
```

**Benefit**: Users can add your certificate to their trust store (advanced users).

---

## Option 3: Let's Encrypt for Linux (Free)

For Linux, you can use Let's Encrypt to sign packages (GPG keys).

```bash
# Generate GPG key (free)
gpg --full-generate-key

# Sign your package
gpg --armor --detach-sign NeuroInsight-x86_64.AppImage

# Users verify:
gpg --verify NeuroInsight-x86_64.AppImage.asc NeuroInsight-x86_64.AppImage
```

**Benefit**: Strong cryptographic verification, completely free.

---

## Option 4: Source Distribution Only (Most Trusted)

Distribute source code and let users build it themselves.

### Advantages:
- ✅ Maximum transparency
- ✅ No security warnings
- ✅ Users can inspect code
- ✅ Works on any platform
- ✅ Free

### Disadvantages:
- ❌ Requires technical users
- ❌ Longer installation time
- ❌ Dependency management challenges

### Implementation:

**Create**: `BUILD_FROM_SOURCE.md`

```markdown
# Building NeuroInsight from Source

## Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Singularity or Docker (for FastSurfer)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/neuroinsight.git
cd neuroinsight
```

### 2. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Set Up Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Download FastSurfer
```bash
# Using Singularity
singularity pull docker://deepmi/fastsurfer:latest

# OR using Docker
docker pull deepmi/fastsurfer:latest
```

### 5. Run Application
```bash
./start.sh  # On Windows: start.bat
```

### 6. Access Application
Open browser to: http://localhost:56052
```

---

## Option 5: Trusted Third-Party Distribution

Get your software included in trusted repositories where they handle signing.

### Package Managers (Free!)

#### Homebrew (macOS)
```bash
# Users install via:
brew install --cask neuroinsight

# No warnings! Homebrew is trusted.
```

**How to get listed**: Create a "cask" formula and submit PR to homebrew-cask

#### Chocolatey (Windows)
```bash
# Users install via:
choco install neuroinsight

# Trusted by Windows admins
```

**How to get listed**: Submit package to Chocolatey community repository

#### APT/YUM (Linux)
```bash
# Users install via:
sudo apt install neuroinsight  # Ubuntu/Debian
sudo yum install neuroinsight  # RHEL/CentOS
```

**How to get listed**: Submit to distribution repositories

### Snap/Flatpak (Linux - Cross-Distro)

```bash
# Package as Snap
snapcraft

# Users install:
sudo snap install neuroinsight

# Automatic signing by Snap store
```

**Benefit**: Canonical (Ubuntu's company) signs Snaps automatically, no cost to you!

---

## Option 6: University/Institution Signing

If you're at a university, they may have institutional certificates.

**Ask**:
- Your IT department
- Research computing office
- Technology transfer office

Many universities have:
- Apple Developer accounts (for iOS apps)
- Windows code signing certificates
- Institutional signing services

**Cost to you**: Usually $0 (absorbed by institution)

---

## Option 7: Open-Source Certificate Initiatives

Some organizations provide free certificates for open-source projects.

### Example: SignPath.io
- **Cost**: Free for open-source
- **Requirements**: Public GitHub repository, OSS license
- **Benefit**: Automated signing in CI/CD
- **Website**: https://signpath.io

### Example: Let's Encrypt (for some use cases)
- Free SSL/TLS certificates
- Can be used for certain signing scenarios

---

## Best Practices for Unsigned Distribution

### 1. Provide Multiple Download Verification Methods

**Create**: `checksums.txt` with each release

```
# SHA256 Checksums for NeuroInsight v1.0.0

# macOS
1234567890abcdef...  NeuroInsight-1.0.0-macos.dmg

# Windows
abcdef1234567890...  NeuroInsight-Setup-1.0.0.exe

# Linux
7890abcdef123456...  NeuroInsight-1.0.0-x86_64.AppImage
```

### 2. Use GitHub Releases (Trusted Source)

Distribute via GitHub releases:
- ✅ URL shows it's from official repository
- ✅ GitHub's reputation helps trust
- ✅ Download counts visible
- ✅ Community can review

### 3. Provide Clear Documentation

Include in every release:
- Why there's no code signing (cost, academic software)
- How to verify authenticity (checksums)
- Step-by-step installation with screenshots
- Source code availability
- Community support channels

### 4. Build Trust Through Transparency

- ✅ Open-source repository
- ✅ Clear changelog
- ✅ Active community
- ✅ Responsive to issues
- ✅ Academic affiliation visible
- ✅ Publications citing the software

### 5. Automated Builds (Reproducibility)

Use GitHub Actions to build releases:

```yaml
# .github/workflows/release.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, windows-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Application
        run: npm run build
      
      - name: Generate Checksums
        run: sha256sum dist/* > checksums.txt
      
      - name: Upload Release
        uses: actions/upload-release-asset@v1
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./dist/*
```

**Benefit**: Users can verify builds are automated and reproducible.

---

## Real-World Examples (Successful Unsigned Software)

Many respected research tools distribute unsigned:

### Scientific Software
- **FreeSurfer** (Harvard/MGH)
- **FSL** (Oxford FMRIB)
- **SPM** (UCL Wellcome Trust)
- **ITK-SNAP** (Penn/UNC)
- **3D Slicer** (initially unsigned)

### Open-Source Tools
- **Blender** (was unsigned for years)
- **GIMP** (GNU Image Manipulation Program)
- **Audacity** (audio editor)
- **OBS Studio** (streaming software)

**Lesson**: Research/academic software is commonly distributed unsigned. Users in this space understand and accept this.

---

## When Should You Eventually Get Certificates?

Consider getting certificates when:
- ✅ Software is mature and stable (v2.0+)
- ✅ Large user base (1000+ downloads)
- ✅ Funding secured (grant or institutional)
- ✅ Clinical adoption (regulatory requirement)
- ✅ Commercial use cases emerge
- ✅ Institutional IT requests it

**Timeline**: Year 2-3 of the project, if successful

---

## Summary: Recommended Approach

### For Research/Academic Software:

**Phase 1** (Now - Year 1): Unsigned + Clear Instructions
- ✅ Cost: $0
- ✅ Distribute via GitHub releases
- ✅ Provide detailed installation guide
- ✅ Include checksums for verification
- ✅ Make source code available

**Phase 2** (Year 1-2): Package Managers
- ✅ Submit to Homebrew (macOS)
- ✅ Submit to Chocolatey (Windows)
- ✅ Create Snap/Flatpak (Linux)
- ✅ Still free, but more trusted

**Phase 3** (Year 2+): Code Signing (if needed)
- Only if you secure funding
- Or if clinical deployment requires it
- Or if user base demands it

---

## Checklist: Distributing Unsigned

- [ ] Create detailed `INSTALLATION.md` with bypass instructions
- [ ] Include screenshots showing security warnings
- [ ] Explain why unsigned (academic/research software)
- [ ] Provide SHA256 checksums
- [ ] Distribute via GitHub releases (trusted source)
- [ ] Make source code publicly available
- [ ] Include "Build from Source" instructions
- [ ] Set up automated builds (GitHub Actions)
- [ ] Add FAQ addressing security concerns
- [ ] Include links to source code in installer
- [ ] Submit to package managers (Homebrew, Chocolatey, Snap)
- [ ] Build community trust through transparency

---

## Template: Installation Warning Notice

Add this to your downloads page and README:

```markdown
## ⚠️ Security Warning Notice

When installing NeuroInsight, you will see security warnings from 
your operating system. This is expected and normal for academic 
research software.

### Why This Happens
NeuroInsight is distributed without commercial code signing 
certificates, which cost $100-500 per year. As an open-source 
research project from [Your Institution], we prioritize making 
the software freely available to researchers worldwide.

### Is It Safe?
**Yes.** NeuroInsight is:
- ✅ Fully open-source (inspect the code)
- ✅ Hosted on GitHub (trusted platform)
- ✅ Built automatically (reproducible builds)
- ✅ Checksum verified (detect tampering)
- ✅ Used by [X] research institutions
- ✅ Peer-reviewed publication: [DOI]

### Bypassing Security Warnings
[Detailed instructions for macOS, Windows, Linux]

### Prefer to Build from Source?
See `BUILD_FROM_SOURCE.md` for complete instructions.

### Questions?
- GitHub Issues: [link]
- Email: [your-email]
- Documentation: [link]
```

---

## Bottom Line

**You absolutely can (and should) distribute without code signing** for research software!

**Cost**: $0  
**Effort**: 1-2 hours to write clear instructions  
**Acceptance**: Standard practice in academic software  
**Users**: Researchers understand this  

**Key Success Factors**:
1. Clear, detailed installation instructions
2. Checksums for verification
3. Open-source code (build trust)
4. Active GitHub presence
5. Responsive to user questions

Most successful research tools started unsigned and only got certificates later (if ever). Your users will understand!

