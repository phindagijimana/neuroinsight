/**
 * Custom Logger for NeuroInsight Desktop
 * 
 * Provides structured logging with separate files for different log levels.
 * Logs are stored in the user's application data directory.
 */

const { app } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');

class Logger {
  constructor() {
    // Get log directory in user's app data
    this.logDir = path.join(app.getPath('userData'), 'logs');
    
    // Create log directory if it doesn't exist
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }
    
    // Define log file paths
    this.logFiles = {
      main: path.join(this.logDir, 'neuroinsight.log'),
      errors: path.join(this.logDir, 'errors.log'),
      crashes: path.join(this.logDir, 'crashes.log')
    };
    
    // In-memory log buffer for UI display (last 1000 entries)
    this.logBuffer = [];
    this.maxBufferSize = 1000;
  }
  
  /**
   * Get the log directory path
   */
  getLogDirectory() {
    return this.logDir;
  }
  
  /**
   * Write a log entry
   */
  writeLog(level, message, error = null, extraData = {}) {
    const timestamp = new Date().toISOString();
    const pid = process.pid;
    
    // Build log entry
    const logEntry = {
      timestamp,
      level: level.toUpperCase(),
      message,
      pid,
      ...extraData
    };
    
    // Add error details if present
    if (error) {
      logEntry.error = {
        message: error.message,
        stack: error.stack,
        name: error.name
      };
    }
    
    // Add to in-memory buffer
    this.logBuffer.push(logEntry);
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift(); // Remove oldest entry
    }
    
    // Format for file writing
    const logLine = JSON.stringify(logEntry) + '\n';
    
    // Write to main log
    try {
      fs.appendFileSync(this.logFiles.main, logLine);
    } catch (err) {
      console.error('Failed to write to main log:', err);
    }
    
    // Write to specific log files based on level
    if (level === 'error' || level === 'crash') {
      try {
        fs.appendFileSync(this.logFiles.errors, logLine);
      } catch (err) {
        console.error('Failed to write to error log:', err);
      }
    }
    
    if (level === 'crash') {
      try {
        fs.appendFileSync(this.logFiles.crashes, logLine);
      } catch (err) {
        console.error('Failed to write to crash log:', err);
      }
    }
  }
  
  /**
   * Log info message
   */
  info(message, extraData = {}) {
    this.writeLog('info', message, null, { data: extraData });
  }
  
  /**
   * Log error message
   */
  error(message, error = null, extraData = {}) {
    this.writeLog('error', message, error, { data: extraData });
  }
  
  /**
   * Log crash/critical error
   */
  crash(message, error = null, extraData = {}) {
    // Add system info to crash logs
    const systemInfo = {
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      electronVersion: process.versions.electron,
      totalMemory: os.totalmem(),
      freeMemory: os.freemem(),
      uptime: process.uptime(),
      cwd: process.cwd(),
      ...extraData
    };
    
    this.writeLog('crash', message, error, systemInfo);
  }
  
  /**
   * Get recent log entries from memory
   */
  getRecentLogs(count = 50) {
    const start = Math.max(0, this.logBuffer.length - count);
    return this.logBuffer.slice(start);
  }
  
  /**
   * Clear all log files
   */
  clearLogs() {
    try {
      Object.values(this.logFiles).forEach(logFile => {
        if (fs.existsSync(logFile)) {
          fs.unlinkSync(logFile);
        }
      });
      this.logBuffer = [];
      this.info('Logs cleared');
      return true;
    } catch (error) {
      console.error('Failed to clear logs:', error);
      return false;
    }
  }
}

// Singleton instance
let loggerInstance = null;

/**
 * Get the logger instance
 */
function getLogger() {
  if (!loggerInstance) {
    loggerInstance = new Logger();
  }
  return loggerInstance;
}

module.exports = { getLogger, Logger };

