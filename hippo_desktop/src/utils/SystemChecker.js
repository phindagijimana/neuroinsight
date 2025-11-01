/**
 * System Requirements Checker
 * 
 * Verifies system meets minimum requirements for NeuroInsight
 */

const os = require('os');
const { exec } = require('child_process');
const { promisify } = require('util');
const si = require('systeminformation');
const logger = require('./logger');

const execAsync = promisify(exec);

class SystemChecker {
  constructor() {
    this.requirements = {
      minCores: 4,
      minRamGB: 16,
      minDiskGB: 30,
      supportedPlatforms: ['darwin', 'win32', 'linux']
    };
  }

  /**
   * Check all system requirements
   */
  async checkAll() {
    logger.info('Checking system requirements...');
    
    const checks = {
      platform: await this.checkPlatform(),
      cpu: await this.checkCPU(),
      ram: await this.checkRAM(),
      disk: await this.checkDisk(),
      docker: await this.checkDocker(),
      gpu: await this.checkGPU()
    };
    
    const failures = [];
    const warnings = [];
    
    // Evaluate results
    if (!checks.platform.passed) {
      failures.push(`Platform: ${checks.platform.message}`);
    }
    
    if (!checks.cpu.passed) {
      if (checks.cpu.cores >= 2) {
        warnings.push(`CPU: ${checks.cpu.message}`);
      } else {
        failures.push(`CPU: ${checks.cpu.message}`);
      }
    }
    
    if (!checks.ram.passed) {
      if (checks.ram.totalGB >= 8) {
        warnings.push(`RAM: ${checks.ram.message}`);
      } else {
        failures.push(`RAM: ${checks.ram.message}`);
      }
    }
    
    if (!checks.disk.passed) {
      warnings.push(`Disk: ${checks.disk.message}`);
    }
    
    if (!checks.docker.passed) {
      failures.push(`Docker: ${checks.docker.message}`);
    }
    
    if (!checks.gpu.passed) {
      warnings.push(`GPU: ${checks.gpu.message} (Processing will be slower on CPU)`);
    }
    
    const passed = failures.length === 0;
    
    logger.info(`System check ${passed ? 'passed' : 'failed'}`, {
      failures: failures.length,
      warnings: warnings.length
    });
    
    return {
      passed,
      checks,
      failures,
      warnings,
      summary: this.generateSummary(checks)
    };
  }

  /**
   * Check platform compatibility
   */
  async checkPlatform() {
    const platform = process.platform;
    const supported = this.requirements.supportedPlatforms.includes(platform);
    
    return {
      passed: supported,
      platform,
      message: supported 
        ? `Platform ${platform} is supported`
        : `Platform ${platform} is not officially supported`
    };
  }

  /**
   * Check CPU cores
   */
  async checkCPU() {
    const cores = os.cpus().length;
    const passed = cores >= this.requirements.minCores;
    
    return {
      passed,
      cores,
      message: passed
        ? `${cores} CPU cores detected (required: ${this.requirements.minCores})`
        : `Only ${cores} CPU cores detected (required: ${this.requirements.minCores})`
    };
  }

  /**
   * Check RAM
   */
  async checkRAM() {
    const totalBytes = os.totalmem();
    const totalGB = Math.round(totalBytes / (1024 ** 3));
    const passed = totalGB >= this.requirements.minRamGB;
    
    return {
      passed,
      totalGB,
      freeGB: Math.round(os.freemem() / (1024 ** 3)),
      message: passed
        ? `${totalGB}GB RAM detected (required: ${this.requirements.minRamGB}GB)`
        : `Only ${totalGB}GB RAM detected (required: ${this.requirements.minRamGB}GB)`
    };
  }

  /**
   * Check disk space
   */
  async checkDisk() {
    try {
      const fsSize = await si.fsSize();
      const mainDisk = fsSize[0];
      const freeGB = Math.round(mainDisk.available / (1024 ** 3));
      const passed = freeGB >= this.requirements.minDiskGB;
      
      return {
        passed,
        freeGB,
        totalGB: Math.round(mainDisk.size / (1024 ** 3)),
        message: passed
          ? `${freeGB}GB free disk space (required: ${this.requirements.minDiskGB}GB)`
          : `Only ${freeGB}GB free disk space (required: ${this.requirements.minDiskGB}GB)`
      };
    } catch (error) {
      return {
        passed: false,
        message: `Could not check disk space: ${error.message}`
      };
    }
  }

  /**
   * Check Docker availability
   */
  async checkDocker() {
    try {
      const { stdout } = await execAsync('docker --version');
      const version = stdout.trim();
      
      return {
        passed: true,
        installed: true,
        version,
        message: `Docker installed: ${version}`
      };
    } catch (error) {
      return {
        passed: false,
        installed: false,
        message: 'Docker Desktop is not installed'
      };
    }
  }

  /**
   * Check GPU availability
   */
  async checkGPU() {
    try {
      // Try to detect NVIDIA GPU
      const { stdout } = await execAsync('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader');
      const [name, memory] = stdout.trim().split(',');
      
      return {
        passed: true,
        available: true,
        name: name.trim(),
        memory: memory.trim(),
        message: `NVIDIA GPU detected: ${name.trim()}`
      };
    } catch (error) {
      // No NVIDIA GPU found
      return {
        passed: false,
        available: false,
        message: 'No NVIDIA GPU detected'
      };
    }
  }

  /**
   * Get detailed system information
   */
  async getInfo() {
    try {
      const [cpu, mem, os, graphics] = await Promise.all([
        si.cpu(),
        si.mem(),
        si.osInfo(),
        si.graphics()
      ]);
      
      return {
        cpu: {
          manufacturer: cpu.manufacturer,
          brand: cpu.brand,
          cores: cpu.cores,
          speed: cpu.speed
        },
        memory: {
          total: Math.round(mem.total / (1024 ** 3)),
          free: Math.round(mem.free / (1024 ** 3)),
          used: Math.round(mem.used / (1024 ** 3))
        },
        os: {
          platform: os.platform,
          distro: os.distro,
          release: os.release,
          arch: os.arch
        },
        gpu: graphics.controllers.map(gpu => ({
          vendor: gpu.vendor,
          model: gpu.model,
          vram: gpu.vram
        }))
      };
    } catch (error) {
      logger.error('Failed to get system info:', error);
      return null;
    }
  }

  /**
   * Generate summary report
   */
  generateSummary(checks) {
    const lines = [];
    
    lines.push('System Requirements Summary');
    lines.push('='.repeat(50));
    lines.push('');
    lines.push(`Platform: ${checks.platform.message}`);
    lines.push(`CPU: ${checks.cpu.message}`);
    lines.push(`RAM: ${checks.ram.message}`);
    lines.push(`Disk: ${checks.disk.message}`);
    lines.push(`Docker: ${checks.docker.message}`);
    lines.push(`GPU: ${checks.gpu.message}`);
    lines.push('');
    
    if (checks.gpu.available) {
      lines.push('⚡ GPU acceleration available - processing will be 10-20x faster!');
    } else {
      lines.push('ℹ️  No GPU detected - processing will use CPU (slower but functional)');
    }
    
    return lines.join('\n');
  }
}

module.exports = SystemChecker;


