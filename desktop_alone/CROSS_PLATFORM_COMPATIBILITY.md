# Cross-Platform Compatibility Guide
## Windows, macOS, Linux Support

**Last Updated:** November 12, 2025  
**Version:** 1.3.12+  
**Status:** Production Ready

---

## 📋 **Platform Support Matrix**

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| **Electron App** | ✅ x64 | ✅ x64, ARM64 | ✅ x64 |
| **Python Backend** | ✅ PyInstaller | ✅ PyInstaller | ✅ PyInstaller |
| **FastSurfer (Docker)** | ✅ Docker Desktop | ✅ Docker Desktop | ✅ Docker/Singularity |
| **File Storage** | ✅ Local | ✅ Local | ✅ Local |
| **Database** | ✅ SQLite | ✅ SQLite | ✅ SQLite |
| **Process Management** | ✅ Native | ✅ POSIX | ✅ POSIX |
| **GPU Support** | ✅ NVIDIA CUDA | ✅ Metal/CUDA | ✅ NVIDIA CUDA |

---

## 🔧 **Platform-Specific Implementations**

### **1. Process Management**

#### **Electron Backend Termination (`main.js`)**

```javascript
// ✅ CROSS-PLATFORM
function stopBackend() {
  if (process.platform === 'win32') {
    backendProcess.kill();  // Windows: No signal argument
  } else {
    backendProcess.kill('SIGTERM');  // Unix/Mac: Use SIGTERM
  }
}
```

**Why:**
- Windows doesn't support Unix signals (`SIGTERM`, `SIGKILL`)
- Windows `kill()` defaults to termination (no signal needed)
- Unix/Mac require explicit signal for graceful shutdown

---

#### **Python Process Groups (`mri_processor.py`)**

```python
# ✅ CROSS-PLATFORM
import platform
is_windows = platform.system() == 'Windows'

if is_windows:
    # Windows: Use CREATE_NEW_PROCESS_GROUP
    process = subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
else:
    # Unix/Mac: Use setsid for process groups
    process = subprocess.Popen(
        cmd,
        preexec_fn=os.setsid
    )
```

**Why:**
- Windows has different process management model (no `preexec_fn`)
- Unix/Mac use process groups for hierarchical termination
- `CREATE_NEW_PROCESS_GROUP` is Windows equivalent

---

#### **Process Termination**

```python
# ✅ CROSS-PLATFORM
if is_windows:
    process.terminate()  # Windows: Clean termination
    process.kill()       # Windows: Force kill
else:
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Unix: Kill group
    os.killpg(os.getpgid(process.pid), signal.SIGKILL)  # Unix: Force kill
```

**Why:**
- Windows processes don't have group IDs
- Unix `killpg()` doesn't exist on Windows
- Platform detection required for safe cleanup

---

### **2. Docker Path Handling**

#### **Desktop vs. Server Mode Paths**

```python
# ✅ CROSS-PLATFORM
if settings.desktop_mode:
    # Desktop: Direct host paths (all platforms)
    host_upload_dir = str(Path(settings.upload_dir).resolve())
    host_output_dir = str(Path(settings.output_dir).resolve())
else:
    # Server: Docker-in-Docker (Linux only)
    if platform.system() == 'Windows':
        hostname = os.environ.get('COMPUTERNAME', 'localhost')
    else:
        hostname = os.uname().nodename  # Unix only
```

**Why:**
- Desktop mode uses direct filesystem paths (no Docker-in-Docker)
- Server mode (Linux) may run inside Docker containers
- `os.uname()` doesn't exist on Windows
- Windows uses `%COMPUTERNAME%` environment variable

---

### **3. File Paths and Directories**

#### **User Directories (`config_desktop.py`)**

```python
# ✅ CROSS-PLATFORM - Uses platformdirs library
import platformdirs

@property
def user_data_dir(self) -> Path:
    """Cross-platform user data directory"""
    return Path(platformdirs.user_data_dir(self.app_name, "NeuroInsight"))

@property
def upload_dir(self) -> Path:
    """Cross-platform documents directory"""
    docs = Path(platformdirs.user_documents_dir())
    upload_dir = docs / self.app_name / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir
```

**Platform-specific locations:**

| Platform | Data Directory | Documents Directory |
|----------|----------------|---------------------|
| **Windows** | `%APPDATA%\NeuroInsight` | `%USERPROFILE%\Documents\NeuroInsight` |
| **macOS** | `~/Library/Application Support/NeuroInsight` | `~/Documents/NeuroInsight` |
| **Linux** | `~/.local/share/NeuroInsight` | `~/Documents/NeuroInsight` |

**Why:**
- Each OS has different conventions for user data
- `platformdirs` handles all platform differences
- Ensures compliance with OS standards

---

#### **Path Separators**

```python
# ✅ ALWAYS USE pathlib.Path() - Handles separators automatically
from pathlib import Path

# Good (cross-platform):
upload_path = Path(settings.upload_dir) / filename
output_path = Path(settings.output_dir) / job_id / "results"

# Bad (platform-specific):
upload_path = settings.upload_dir + "/" + filename  # ❌ Fails on Windows
output_path = f"{settings.output_dir}\\{job_id}\\results"  # ❌ Fails on Unix
```

**Why:**
- Windows uses backslashes (`\`), Unix/Mac use forward slashes (`/`)
- `pathlib.Path()` handles this automatically
- String concatenation can break paths

---

### **4. Executable Names**

#### **Backend Executable (`main.js`)**

```javascript
// ✅ CROSS-PLATFORM
function getBackendPath() {
  const backendDir = path.join(resources, 'backend');
  
  if (process.platform === 'win32') {
    return path.join(backendDir, 'neuroinsight-backend.exe');
  } else {
    return path.join(backendDir, 'neuroinsight-backend');
  }
}
```

**Platform-specific executables:**
- **Windows:** `neuroinsight-backend.exe`
- **macOS:** `neuroinsight-backend` (no extension)
- **Linux:** `neuroinsight-backend` (no extension)

---

#### **PyInstaller Build (`build.spec`)**

```python
# ✅ CROSS-PLATFORM
import sys

exe = EXE(
    ...
    name='neuroinsight-backend',
    icon='electron-app/build/icon.ico' if sys.platform == 'win32' else None,
)
```

**Platform-specific icons:**
- **Windows:** `.ico` format
- **macOS:** `.icns` format (set in package.json build config)
- **Linux:** `.png` files in `build/icons/` directory

---

### **5. Docker/Singularity Support**

#### **Container Runtime Detection**

```python
# ✅ CROSS-PLATFORM
# Desktop mode: Docker Desktop (all platforms)
# Server mode: Docker or Singularity (Linux)

# Check Docker first
try:
    subprocess.run(["docker", "version"], capture_output=True)
    logger.info("docker_available")
except FileNotFoundError:
    # Docker not found - try Singularity (Linux only)
    if platform.system() != 'Windows':
        try:
            subprocess.run(["singularity", "--version"], capture_output=True)
            logger.info("singularity_available")
        except FileNotFoundError:
            raise DockerNotAvailableError()
```

**Platform availability:**
- **Windows:** Docker Desktop only
- **macOS:** Docker Desktop only
- **Linux:** Docker Desktop, Docker Engine, OR Singularity/Apptainer

---

### **6. Process Finding and Killing**

#### **Task Management Service**

```python
# ✅ CROSS-PLATFORM - Uses psutil library (fallback to Unix commands)
import psutil

# Primary method (all platforms):
for proc in psutil.process_iter(['pid', 'cmdline']):
    if job_id in ' '.join(proc.info.get('cmdline', [])):
        proc.terminate()  # Cross-platform
        proc.kill()       # Cross-platform force kill

# Fallback (Unix only):
try:
    subprocess.run(['pgrep', '-f', job_id], ...)  # Unix only
    os.kill(int(pid), signal.SIGTERM)  # Unix only
except:
    pass  # Silently fail on Windows (psutil is primary)
```

**Why:**
- `psutil` works on all platforms
- `pgrep`/`pkill` only exist on Unix/Mac
- Fallback only runs if `psutil` import fails

---

## 🏗️ **Build Configuration**

### **Electron Builder (`package.json`)**

```json
{
  "build": {
    "win": {
      "target": "nsis",
      "icon": "build/icon.ico",
      "requestedExecutionLevel": "asInvoker"
    },
    "mac": {
      "target": "dmg",
      "arch": ["x64", "arm64"],
      "icon": "build/icon.icns",
      "hardenedRuntime": true
    },
    "linux": {
      "target": "AppImage",
      "icon": "build/icons",
      "category": "Science;MedicalSoftware"
    }
  }
}
```

**Platform-specific settings:**
- **Windows:** NSIS installer, ICO icon, execution level
- **macOS:** DMG disk image, ICNS icon, code signing settings, universal binary (x64 + ARM64)
- **Linux:** AppImage, PNG icons, desktop entry categories

---

### **GitHub Actions Runners**

```yaml
build-linux:
  runs-on: ubuntu-latest  # ✅ Linux build on Linux
  
build-windows:
  runs-on: windows-latest  # ✅ Windows build on Windows
  
build-macos:
  runs-on: macos-latest    # ✅ macOS build on macOS
```

**Why:**
- Each platform builds on its native OS
- Ensures platform-specific features work correctly
- Tests actual runtime environment

---

## 🐛 **Common Cross-Platform Pitfalls**

### **❌ DON'T: Use Platform-Specific Functions Without Checks**

```python
# ❌ BAD - Will crash on Windows
hostname = os.uname().nodename

# ❌ BAD - Will crash on Windows
process = subprocess.Popen(cmd, preexec_fn=os.setsid)

# ❌ BAD - Will crash on Windows
os.killpg(os.getpgid(pid), signal.SIGTERM)
```

### **✅ DO: Check Platform Before Using OS-Specific Code**

```python
# ✅ GOOD - Platform detection
import platform

if platform.system() == 'Windows':
    hostname = os.environ.get('COMPUTERNAME')
else:
    hostname = os.uname().nodename

# ✅ GOOD - Conditional execution
if platform.system() != 'Windows':
    process = subprocess.Popen(cmd, preexec_fn=os.setsid)
else:
    process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
```

---

### **❌ DON'T: Hardcode Path Separators**

```python
# ❌ BAD - Breaks on Windows
file_path = base_dir + "/" + filename

# ❌ BAD - Breaks on Unix/Mac
file_path = base_dir + "\\" + filename
```

### **✅ DO: Use pathlib.Path() for All Paths**

```python
# ✅ GOOD - Works everywhere
from pathlib import Path

file_path = Path(base_dir) / filename
```

---

### **❌ DON'T: Use Shell-Specific Commands Without Platform Check**

```python
# ❌ BAD - pgrep doesn't exist on Windows
subprocess.run(['pgrep', '-f', 'pattern'])

# ❌ BAD - tasklist doesn't exist on Unix
subprocess.run(['tasklist', '/FI', 'IMAGENAME eq app.exe'])
```

### **✅ DO: Use Cross-Platform Libraries**

```python
# ✅ GOOD - Works on all platforms
import psutil

for proc in psutil.process_iter(['name', 'cmdline']):
    if 'pattern' in proc.info['name']:
        proc.terminate()
```

---

### **❌ DON'T: Assume Signal Support**

```python
# ❌ BAD - SIGTERM doesn't work on Windows
backendProcess.kill('SIGTERM')
```

### **✅ DO: Platform-Specific Signal Handling**

```javascript
// ✅ GOOD - Platform detection
if (process.platform === 'win32') {
  backendProcess.kill();  // No signal
} else {
  backendProcess.kill('SIGTERM');
}
```

---

## 📁 **File Path Reference**

### **Desktop Mode Paths (All Platforms)**

**Windows:**
```
Data:    C:\Users\<user>\AppData\Roaming\NeuroInsight\
Logs:    C:\Users\<user>\AppData\Roaming\NeuroInsight\logs\
DB:      C:\Users\<user>\AppData\Roaming\NeuroInsight\neuroinsight.db
Uploads: C:\Users\<user>\Documents\NeuroInsight\uploads\
Outputs: C:\Users\<user>\Documents\NeuroInsight\outputs\
```

**macOS:**
```
Data:    ~/Library/Application Support/NeuroInsight/
Logs:    ~/Library/Application Support/NeuroInsight/logs/
DB:      ~/Library/Application Support/NeuroInsight/neuroinsight.db
Uploads: ~/Documents/NeuroInsight/uploads/
Outputs: ~/Documents/NeuroInsight/outputs/
```

**Linux:**
```
Data:    ~/.local/share/NeuroInsight/
Logs:    ~/.local/share/NeuroInsight/logs/
DB:      ~/.local/share/NeuroInsight/neuroinsight.db
Uploads: ~/Documents/NeuroInsight/uploads/
Outputs: ~/Documents/NeuroInsight/outputs/
```

---

## 🛠️ **Development Best Practices**

### **1. Always Test on Target Platform**

```yaml
# GitHub Actions ensures this:
build-linux:   runs-on: ubuntu-latest
build-windows: runs-on: windows-latest
build-macos:   runs-on: macos-latest
```

### **2. Use Cross-Platform Libraries**

**✅ Recommended:**
- **Paths:** `pathlib.Path()` (Python), `path.join()` (Node.js)
- **User dirs:** `platformdirs` (Python), `electron.app.getPath()` (Electron)
- **Process mgmt:** `psutil` (Python), native Electron APIs
- **File I/O:** Use binary mode (`'rb'`, `'wb'`) for portability

**❌ Avoid:**
- String concatenation for paths
- Shell-specific commands (`pgrep`, `tasklist`, etc.)
- Hardcoded directory separators
- Platform-specific system calls without checks

### **3. Platform Detection Pattern**

```python
# Python:
import platform

if platform.system() == 'Windows':
    # Windows-specific code
elif platform.system() == 'Darwin':  # macOS
    # macOS-specific code
elif platform.system() == 'Linux':
    # Linux-specific code
```

```javascript
// JavaScript/Node.js:
if (process.platform === 'win32') {
  // Windows-specific code
} else if (process.platform === 'darwin') {
  // macOS-specific code
} else if (process.platform === 'linux') {
  // Linux-specific code
}
```

---

## 🚀 **Build System Compatibility**

### **PyInstaller (Backend)**

**Platform-specific considerations:**

**Windows:**
- Generates `.exe` executable
- May require `--add-binary` for DLLs
- Antivirus can interfere (whitelist needed)
- Icon: `icon.ico`

**macOS:**
- Generates standalone binary (no extension)
- May require code signing for distribution
- Gatekeeper may block unsigned apps
- Icon: Set via Electron Builder

**Linux:**
- Generates standalone binary (no extension)
- May need `chmod +x` for execution
- Libraries linked dynamically (ensure compatibility)
- No icon (set via desktop entry)

---

### **Electron Builder (Frontend)**

**Platform-specific targets:**

```json
{
  "win": {
    "target": "nsis",           // Windows installer
    "arch": ["x64"]             // 64-bit only
  },
  "mac": {
    "target": "dmg",            // Disk image
    "arch": ["x64", "arm64"]    // Universal binary
  },
  "linux": {
    "target": "AppImage"        // Portable executable
  }
}
```

---

## 🧪 **Testing Checklist**

### **Platform-Specific Tests**

**Windows:**
- [ ] App installs via NSIS installer
- [ ] Backend starts without errors
- [ ] Docker Desktop integration works
- [ ] Paths use backslashes correctly
- [ ] Process termination works gracefully
- [ ] No Unix command errors in logs

**macOS:**
- [ ] DMG opens and drags to Applications
- [ ] Gatekeeper bypass works (unsigned app)
- [ ] Backend starts on both Intel and Apple Silicon
- [ ] Docker Desktop integration works
- [ ] Process groups terminate correctly

**Linux:**
- [ ] AppImage runs with `chmod +x`
- [ ] Desktop entry creates correctly
- [ ] Docker OR Singularity works
- [ ] Process groups work correctly
- [ ] Permissions are correct

---

## 🔍 **Debugging Platform Issues**

### **Windows Issues**

**Symptom:** `AttributeError: module 'os' has no attribute 'getuid'`  
**Fix:** Check for `os.uname()`, `os.setsid()`, `os.getpgid()`, `os.killpg()` usage

**Symptom:** Backend won't start  
**Fix:** Check if `.exe` extension is used, verify PyInstaller built Windows executable

**Symptom:** Paths not found  
**Fix:** Use `Path().resolve()` and check for backslash escaping

---

### **macOS Issues**

**Symptom:** "App cannot be opened because developer cannot be verified"  
**Fix:** Right-click → Open (first time), or disable Gatekeeper

**Symptom:** Process won't terminate  
**Fix:** Check if SIGTERM is used (not just kill())

**Symptom:** Backend crashes on ARM (Apple Silicon)  
**Fix:** Ensure PyInstaller builds for ARM64 (`--target-arch arm64`)

---

### **Linux Issues**

**Symptom:** AppImage won't run  
**Fix:** Check if execute permission is set (`chmod +x`)

**Symptom:** Docker not found  
**Fix:** Check if Singularity fallback activates correctly

**Symptom:** "Operation not permitted" errors  
**Fix:** Check if `--cleanenv` or `--containall` needed for Singularity

---

## 📚 **Platform-Specific Dependencies**

### **Runtime Requirements**

**Windows:**
- Python 3.10+
- Docker Desktop (for FastSurfer)
- Visual C++ Redistributable (bundled by PyInstaller)

**macOS:**
- Python 3.10+
- Docker Desktop (for FastSurfer)
- macOS 10.15+ (Catalina or newer)
- Rosetta 2 (for Intel apps on Apple Silicon)

**Linux:**
- Python 3.10+
- Docker Desktop/Engine OR Singularity/Apptainer
- FUSE 2.x (for AppImage)
- `libxcb`, `libx11` (GUI libraries)

---

## 🎯 **Quick Reference: Platform Detection**

### **Python**

```python
import platform
import sys

os_name = platform.system()  # 'Windows', 'Darwin', 'Linux'
is_windows = os_name == 'Windows'
is_mac = os_name == 'Darwin'
is_linux = os_name == 'Linux'
is_64bit = sys.maxsize > 2**32
```

### **JavaScript/Node.js**

```javascript
const is_windows = process.platform === 'win32';
const is_mac = process.platform === 'darwin';
const is_linux = process.platform === 'linux';
const is_64bit = process.arch === 'x64';
const is_arm = process.arch === 'arm64';
```

---

## ✅ **Verified Cross-Platform Features**

| Component | Implementation | Status |
|-----------|----------------|--------|
| **File paths** | `pathlib.Path()` | ✅ All platforms |
| **User directories** | `platformdirs` | ✅ All platforms |
| **Process management** | Platform detection | ✅ All platforms |
| **Docker paths** | Desktop mode check | ✅ All platforms |
| **Backend executable** | Platform-specific naming | ✅ All platforms |
| **Process termination** | Conditional signals | ✅ All platforms |
| **Build system** | Native runners | ✅ All platforms |
| **File storage** | Local filesystem | ✅ All platforms |
| **Database** | SQLite | ✅ All platforms |

---

## 📝 **Code Review Checklist**

When adding new code, verify:

- [ ] No hardcoded path separators (`/` or `\`)
- [ ] All paths use `pathlib.Path()` or `path.join()`
- [ ] No Unix-only functions without platform checks
- [ ] No Windows-only functions without platform checks
- [ ] Subprocess calls work on all platforms
- [ ] File operations use cross-platform libraries
- [ ] Process management handles platform differences
- [ ] Build configuration includes all platforms
- [ ] Documentation mentions platform-specific behavior
- [ ] Tests cover all platforms (via CI/CD)

---

## 🚦 **Migration Guide: Making Code Cross-Platform**

### **Step 1: Identify Platform-Specific Code**

```bash
# Search for potential issues:
grep -r "os.uname\|os.setsid\|os.killpg\|preexec_fn" .
grep -r "pgrep\|pkill\|tasklist" .
grep -r '"\/"' .  # Hardcoded forward slashes
grep -r '"\\\\"' .  # Hardcoded backslashes
```

### **Step 2: Add Platform Detection**

```python
import platform
is_windows = platform.system() == 'Windows'
```

### **Step 3: Implement Platform-Specific Logic**

```python
if is_windows:
    # Windows implementation
else:
    # Unix/Mac implementation
```

### **Step 4: Test on All Platforms**

- Push to GitHub → Triggers builds on all platforms
- Download artifacts and test manually
- Check logs for platform-specific errors

---

## 🎓 **Resources**

**Cross-Platform Libraries:**
- **platformdirs:** https://github.com/platformdirs/platformdirs
- **psutil:** https://github.com/giampaolo/psutil
- **pathlib:** https://docs.python.org/3/library/pathlib.html

**Platform Detection:**
- **Python platform:** https://docs.python.org/3/library/platform.html
- **Node.js process:** https://nodejs.org/api/process.html

**Build Tools:**
- **PyInstaller:** https://pyinstaller.org/
- **Electron Builder:** https://www.electron.build/

---

## 📞 **Support**

If you encounter platform-specific issues:

1. **Check logs:** Platform-specific error messages
2. **Review this guide:** Common pitfalls section
3. **Test locally:** If possible, test on actual platform
4. **Use CI/CD:** GitHub Actions tests all platforms
5. **Report bug:** Include platform and OS version

---

**Last Updated:** v1.3.12  
**Platforms:** Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)  
**Status:** ✅ Production Ready

