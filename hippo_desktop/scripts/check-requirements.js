#!/usr/bin/env node

/**
 * Pre-build requirements checker
 * 
 * Verifies that the build environment meets requirements
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('='.repeat(70));
console.log('NeuroInsight Desktop - Build Requirements Check');
console.log('='.repeat(70));
console.log('');

const checks = {
  passed: [],
  warnings: [],
  failed: []
};

// Check Node.js version
try {
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
  
  if (majorVersion >= 18) {
    checks.passed.push(`Node.js ${nodeVersion} ✓`);
  } else {
    checks.failed.push(`Node.js ${nodeVersion} (need 18+)`);
  }
} catch (error) {
  checks.failed.push('Could not check Node.js version');
}

// Check npm
try {
  const npmVersion = execSync('npm --version', { encoding: 'utf-8' }).trim();
  checks.passed.push(`npm ${npmVersion} ✓`);
} catch (error) {
  checks.failed.push('npm not found');
}

// Check Docker
try {
  const dockerVersion = execSync('docker --version', { encoding: 'utf-8' }).trim();
  checks.passed.push(`${dockerVersion} ✓`);
} catch (error) {
  checks.warnings.push('Docker not found (required for testing)');
}

// Check if parent directories exist
const requiredDirs = [
  path.join(__dirname, '../../backend'),
  path.join(__dirname, '../../frontend'),
  path.join(__dirname, '../../workers'),
  path.join(__dirname, '../../pipeline')
];

let dirsExist = true;
requiredDirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    checks.failed.push(`Missing directory: ${path.basename(dir)}`);
    dirsExist = false;
  }
});

if (dirsExist) {
  checks.passed.push('All source directories found ✓');
}

// Check node_modules
if (fs.existsSync(path.join(__dirname, '../node_modules'))) {
  checks.passed.push('Dependencies installed ✓');
} else {
  checks.warnings.push('Dependencies not installed (run: npm install)');
}

// Check for code signing certificates (optional)
if (process.env.CSC_LINK) {
  if (fs.existsSync(process.env.CSC_LINK)) {
    checks.passed.push('Code signing certificate found ✓');
  } else {
    checks.warnings.push('Code signing certificate configured but file not found');
  }
} else {
  checks.warnings.push('No code signing certificate (builds will be unsigned)');
}

// Print results
console.log('✓ PASSED:');
checks.passed.forEach(msg => console.log(`  ✓ ${msg}`));
console.log('');

if (checks.warnings.length > 0) {
  console.log('WARNINGS:');
  checks.warnings.forEach(msg => console.log(`  WARNING: ${msg}`));
  console.log('');
}

if (checks.failed.length > 0) {
  console.log('✗ FAILED:');
  checks.failed.forEach(msg => console.log(`  ✗ ${msg}`));
  console.log('');
  console.log('='.repeat(70));
  console.log('ERROR: Build requirements not met');
  console.log('='.repeat(70));
  process.exit(1);
}

console.log('='.repeat(70));
console.log('SUCCESS: All requirements met - ready to build!');
console.log('='.repeat(70));
console.log('');
console.log('Next steps:');
console.log('  npm run pack      - Package without creating installer');
console.log('  npm run dist      - Create installer for current platform');
console.log('  npm run dist:mac  - Create macOS DMG');
console.log('  npm run dist:win  - Create Windows installer');
console.log('  npm run dist:linux- Create Linux packages');
console.log('');


