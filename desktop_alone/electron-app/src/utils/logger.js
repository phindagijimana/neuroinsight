/**
 * NeuroInsight Desktop - Crash & Error Logger
 * 
 * Logs all errors, crashes, and important events to local files.
 * Users can send these logs for debugging support.
 */

const fs = require('fs');
const path = require('path');
const { app } = require('electron');

class Logger {
  constructor() {
    // Create logs directory
    const userDataPath = app.getPath('userData');
    this.logDir = path.join(userDataPath, 'logs');
    this.ensureLogDirectory();
    
    // Log file paths
    this.mainLogPath = path.join(this.logDir, 'neuroinsight.log');
    this.errorLogPath = path.join(this.logDir, 'errors.log');
    this.crashLogPath = path.join(this.logDir, 'crashes.log');
    
    // Rotate logs if they're too large (>10 MB)
    this.rotateLogs();
    
    // Log startup
    this.info('Application started', {
      version: app.getVersion(),
      platform: process.platform,
      arch: process.arch,
      electronVersion: process.versions.electron,
      nodeVersion: process.versions.node
    });
  }
  
  /**
   * Ensure log directory exists
   */
  ensureLogDirectory() {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }
  }
  
  /**
   * Rotate logs if they exceed size limit
   */
  rotateLogs() {
    const maxSize = 10 * 1024 * 1024; // 10 MB
    const logFiles = [this.mainLogPath, this.errorLogPath, this.crashLogPath];
    
    logFiles.forEach(logPath => {
      if (fs.existsSync(logPath)) {
        const stats = fs.statSync(logPath);
        if (stats.size > maxSize) {
          const backupPath = `${logPath}.old`;
          if (fs.existsSync(backupPath)) {
            fs.unlinkSync(backupPath);
          }
          fs.renameSync(logPath, backupPath);
        }
      }
    });
  }
  
  /**
   * Format log entry
   */
  formatEntry(level, message, data = null) {
    const entry = {
      timestamp: new Date().toISOString(),
      level: level.toUpperCase(),
      message,
      pid: process.pid,
      ...(data && { data })
    };
    return JSON.stringify(entry) + '\n';
  }
  
  /**
   * Write to log file
   */
  writeToFile(filePath, entry) {
    try {
      fs.appendFileSync(filePath, entry);
    } catch (err) {
      // If we can't write logs, at least console.error
      console.error('Failed to write to log file:', err);
    }
  }
  
  /**
   * INFO level logging
   */
  info(message, data = null) {
    const entry = this.formatEntry('info', message, data);
    this.writeToFile(this.mainLogPath, entry);
    console.log(`[INFO] ${message}`, data || '');
  }
  
  /**
   * WARN level logging
   */
  warn(message, data = null) {
    const entry = this.formatEntry('warn', message, data);
    this.writeToFile(this.mainLogPath, entry);
    console.warn(`[WARN] ${message}`, data || '');
  }
  
  /**
   * ERROR level logging
   */
  error(message, error = null, data = null) {
    const errorData = {
      ...(data || {}),
      ...(error && {
        error: {
          message: error.message,
          stack: error.stack,
          code: error.code,
          name: error.name
        }
      })
    };
    
    const entry = this.formatEntry('error', message, errorData);
    this.writeToFile(this.mainLogPath, entry);
    this.writeToFile(this.errorLogPath, entry);
    console.error(`[ERROR] ${message}`, error || '', data || '');
  }
  
  /**
   * CRASH level logging (critical errors)
   */
  crash(message, error = null, data = null) {
    const crashData = {
      ...(data || {}),
      ...(error && {
        error: {
          message: error.message,
          stack: error.stack,
          code: error.code,
          name: error.name
        }
      }),
      // Capture system state at crash time
      memory: process.memoryUsage(),
      uptime: process.uptime(),
      cwd: process.cwd()
    };
    
    const entry = this.formatEntry('crash', message, crashData);
    this.writeToFile(this.mainLogPath, entry);
    this.writeToFile(this.errorLogPath, entry);
    this.writeToFile(this.crashLogPath, entry);
    console.error(`[CRASH] ${message}`, error || '', crashData);
  }
  
  /**
   * Get log directory path (for showing to users)
   */
  getLogDirectory() {
    return this.logDir;
  }
  
  /**
   * Get recent log entries (for in-app display)
   */
  getRecentLogs(count = 50) {
    try {
      if (!fs.existsSync(this.mainLogPath)) {
        return [];
      }
      
      const content = fs.readFileSync(this.mainLogPath, 'utf-8');
      const lines = content.trim().split('\n').filter(line => line);
      const recent = lines.slice(-count);
      
      return recent.map(line => {
        try {
          return JSON.parse(line);
        } catch (e) {
          return { raw: line };
        }
      });
    } catch (err) {
      console.error('Failed to read logs:', err);
      return [];
    }
  }
  
  /**
   * Clear all logs
   */
  clearLogs() {
    const logFiles = [this.mainLogPath, this.errorLogPath, this.crashLogPath];
    logFiles.forEach(logPath => {
      if (fs.existsSync(logPath)) {
        fs.unlinkSync(logPath);
      }
    });
    this.info('Logs cleared');
  }
}

// Singleton instance
let loggerInstance = null;

/**
 * Get logger instance
 */
function getLogger() {
  if (!loggerInstance) {
    loggerInstance = new Logger();
  }
  return loggerInstance;
}

module.exports = { getLogger };

