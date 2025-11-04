# NeuroInsight Desktop App - Branch Information

## Branch Strategy

This project uses multiple Git branches to support different deployment approaches:

### `desktop-app` - Electron Desktop Application (In Progress)

**Status:** Development paused due to Docker PATH issues on macOS

**Contains:**
- Full Electron desktop application
- Docker Desktop integration
- Automatic service management
- macOS, Windows, Linux builds via GitHub Actions
- All PATH fixes attempted (v1.0.1 through v1.0.5)

**Issues:**
- macOS PATH detection challenges with GUI apps
- Docker Desktop dependency complexity
- `spawn docker ENOENT` errors

**To Resume Development:**
```bash
git checkout desktop-app
cd hippo_desktop
npm install
npm start
```

**Future Options:**
1. Continue fixing Docker PATH issues
2. Migrate to standalone app (no Docker) - see `STANDALONE_MIGRATION_PLAN.md`
3. Hybrid approach (bundled Python, no Docker)

---

### `web-app` - Docker Compose Web Application (For Paper)

**Status:** Active - Recommended for paper publication

**Contains:**
- Simplified docker-compose deployment
- Web UI (browser-based)
- All backend services
- Focus on reliability and ease of use

**Usage:**
```bash
git checkout web-app
docker-compose up -d
open http://localhost:3000
```

**Why This Branch:**
- ✅ Works reliably (no PATH issues)
- ✅ Standard approach in neuroimaging
- ✅ $0 hosting costs
- ✅ HIPAA-compliant (local processing)
- ✅ Paper-ready

---

### `main` - Main Branch

**Status:** Will track the recommended approach

Currently points to web-app approach for stable release.

---

## Version History

### Desktop App Attempts (desktop-app branch)

- **v1.0.0** - Initial release (had emoji issues)
- **v1.0.1** - Fixed emojis, added docker-compose detection
- **v1.0.2** - Fixed docker-compose compatibility
- **v1.0.3** - Fixed process initialization error
- **v1.0.4** - Added Docker PATH detection per-command
- **v1.0.5** - Added global PATH fix at startup (still had issues)

**Lesson Learned:** Electron + Docker Desktop = Complex PATH management on macOS

---

## Documentation References

- **Desktop App Migration Plan:** `STANDALONE_MIGRATION_PLAN.md` (desktop-app branch)
- **Quick Start Guide:** `QUICK_START.md` (desktop-app branch)
- **Contributing:** `CONTRIBUTING.md`

---

## Switching Between Branches

### To Work on Desktop App:
```bash
git checkout desktop-app
# All desktop app code is here
# Continue development or migrate to standalone
```

### To Use Web App (Recommended):
```bash
git checkout web-app
# Simplified, stable version
# For paper and general use
```

### To Start Standalone Migration (Future):
```bash
git checkout -b standalone-migration
# Follow STANDALONE_MIGRATION_PLAN.md
# Build true standalone app (no Docker)
```

---

## Recommendations

**For Paper Publication (Now):**
- Use `web-app` branch
- Docker Compose deployment
- Proven, reliable approach

**For Clinical Deployment (Later - v2.0):**
- Create `standalone-migration` branch
- Follow migration plan
- Build true standalone app
- No Docker dependency

**For Desktop App (Optional):**
- Continue `desktop-app` branch
- Either fix PATH issues
- Or migrate to standalone

---

## Contact

If you have questions about which branch to use, see:
- Research/paper: Use `web-app`
- End-user desktop: Plan `standalone-migration`
- Continue current desktop: Use `desktop-app`

---

*Last Updated: November 2025*
