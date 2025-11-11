/**
 * NeuroInsight Desktop - Main Process
 * 
 * Manages application lifecycle and backend process.
 */

const { app, BrowserWindow, ipcMain, Menu, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const log = require('electron-log');
const waitOn = require('wait-on');
const { getLogger } = require('./utils/logger');

// Set up logging
log.transports.file.level = 'info';
log.info('NeuroInsight Desktop starting...');

// Initialize our custom logger
let logger;
try {
  logger = getLogger();
} catch (error) {
  // Fallback to electron-log if custom logger fails
  log.error('Failed to initialize custom logger:', error);
}

// IPC Handler for backend URL
ipcMain.handle('get-backend-url', () => {
  return `http://127.0.0.1:${BACKEND_PORT}`;
});

let mainWindow = null;
let backendProcess = null;
let BACKEND_PORT = 0; // 0 = OS assigns available port dynamically

/**
 * Get path to bundled backend executable
 */
function getBackendPath() {
  if (app.isPackaged) {
    // Production: backend bundled in resources
    const resources = process.resourcesPath;
    const backendDir = path.join(resources, 'backend');
    
    if (process.platform === 'win32') {
      return path.join(backendDir, 'neuroinsight-backend.exe');
    } else {
      return path.join(backendDir, 'neuroinsight-backend');
    }
  } else {
    // Development: use local build
    return path.join(__dirname, '../../dist/neuroinsight-backend/neuroinsight-backend');
  }
}

/**
 * Start the backend process
 */
function startBackend() {
  const backendPath = getBackendPath();
  
  log.info('Starting backend:', backendPath);
  
  // Set environment for desktop mode
  const env = {
    ...process.env,
    DESKTOP_MODE: 'true',
    PORT: String(BACKEND_PORT),
    HOST: '127.0.0.1',
  };
  
  // Spawn backend process
  backendProcess = spawn(backendPath, [], {
    env: env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  // Log backend output and capture actual port
  backendProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    log.info('[Backend]', output);
    if (logger) {
      logger.info('Backend output', { output });
    }
    
    // Capture actual port from Uvicorn output: "Uvicorn running on http://0.0.0.0:PORT"
    // Match both "http://0.0.0.0:PORT" and "http://127.0.0.1:PORT"
    const portMatch = output.match(/Uvicorn running on https?:\/\/(?:0\.0\.0\.0|127\.0\.0\.1|\[::\]):(\d+)/);
    if (portMatch && BACKEND_PORT === 0) {
      BACKEND_PORT = parseInt(portMatch[1], 10);
      log.info(`✅ Backend port captured: ${BACKEND_PORT}`);
      if (logger) {
        logger.info('Backend port captured', { port: BACKEND_PORT });
      }
    }
  });

  backendProcess.stderr.on('data', (data) => {
    const output = data.toString().trim();
    log.error('[Backend Error]', output);
    if (logger) {
      logger.error('Backend error output', null, { output });
    }
    
    // Uvicorn also outputs to stderr, so capture port here too
    const portMatch = output.match(/Uvicorn running on https?:\/\/(?:0\.0\.0\.0|127\.0\.0\.1|\[::\]):(\d+)/);
    if (portMatch && BACKEND_PORT === 0) {
      BACKEND_PORT = parseInt(portMatch[1], 10);
      log.info(`✅ Backend port captured from stderr: ${BACKEND_PORT}`);
      if (logger) {
        logger.info('Backend port captured from stderr', { port: BACKEND_PORT });
      }
    }
  });

  backendProcess.on('error', (error) => {
    log.error('Failed to start backend:', error);
    if (logger) {
      logger.crash('Failed to start backend process', error, {
        backendPath: getBackendPath(),
        port: BACKEND_PORT
      });
    }
  });

  backendProcess.on('close', (code) => {
    log.info(`Backend process exited with code ${code}`);
    
    if (logger) {
      if (code !== 0 && code !== null) {
        logger.error('Backend crashed unexpectedly', null, {
          exitCode: code,
          uptime: process.uptime()
        });
      } else {
        logger.info('Backend process exited normally', { exitCode: code });
      }
    }
  });
  
  log.info('Backend process started (PID: ' + backendProcess.pid + ')');
}

/**
 * Stop the backend process
 */
function stopBackend() {
  if (backendProcess) {
    log.info('Stopping backend...');
    backendProcess.kill('SIGTERM');
    backendProcess = null;
  }
}

/**
 * Create splash screen
 */
function createSplash() {
  const splash = new BrowserWindow({
    width: 500,
    height: 400,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: false,
    },
  });
  
  splash.loadFile(path.join(__dirname, 'splash.html'));
  return splash;
}

/**
 * Create the main application window
 */
async function createWindow() {
  // Show splash screen
  const splash = createSplash();
  
  // Create browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    show: false,  // Don't show until ready
    backgroundColor: '#1a1a1a',
    title: 'NeuroInsight',
  });

  // Wait for backend port to be captured (max 5 seconds)
  let portWaitTime = 0;
  while (BACKEND_PORT === 0 && portWaitTime < 5000) {
    await new Promise(resolve => setTimeout(resolve, 100));
    portWaitTime += 100;
  }
  
  if (BACKEND_PORT === 0) {
    throw new Error('Failed to capture backend port from output');
  }
  
  log.info(`Backend port captured: ${BACKEND_PORT}`);
  
  // Wait for backend to be ready
  try {
    log.info('Waiting for backend to be ready...');
    
    await waitOn({
      resources: [`http://127.0.0.1:${BACKEND_PORT}/health`],
      timeout: 30000,  // 30 seconds
      interval: 1000,   // Check every second
    });
    
    log.info('Backend is ready!');
    
    // Load the frontend HTML file (bundled with Electron)
    // The frontend is now in extraResources (outside app.asar, like backend)
    const frontendPath = app.isPackaged
      ? path.join(process.resourcesPath, 'frontend', 'index.html')
      : path.join(__dirname, '..', 'frontend', 'index.html');
    log.info(`Loading frontend from: ${frontendPath}`);
    
    // First, set the backend URL before loading the page
    // This makes it available synchronously when the page loads
    mainWindow.loadFile(frontendPath).then(() => {
      log.info('Frontend loaded successfully');
    }).catch((err) => {
      log.error('Failed to load frontend:', err);
    });
    
    // Backend URL is now exposed via IPC in preload script
    // No need to inject via executeJavaScript
    
    // Show window when ready, close splash
    mainWindow.once('ready-to-show', () => {
      splash.close();
      mainWindow.show();
      log.info('Application window shown');
    });
    
  } catch (error) {
    log.error('Backend failed to start within timeout:', error);
    
    if (logger) {
      logger.crash('Backend failed to start within timeout', error, {
        timeout: 30000,
        port: BACKEND_PORT
      });
    }
    
    // Show error dialog
    const logLocation = logger ? logger.getLogDirectory() : 'unknown';
    dialog.showErrorBox(
      'NeuroInsight Startup Error',
      'Failed to start NeuroInsight backend.\n\nPlease check if:\n' +
      '- You have sufficient disk space\n' +
      '- Antivirus is not blocking the application\n\n' +
      `Error: ${error.message}\n\n` +
      `Logs saved to: ${logLocation}`
    );
    
    app.quit();
    return;
  }

  // Open DevTools in development
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Create application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forcereload' },
        { type: 'separator' },
        { role: 'resetzoom' },
        { role: 'zoomin' },
        { role: 'zoomout' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: async () => {
            const { shell } = require('electron');
            await shell.openExternal('https://github.com/phindagijimana/neuroinsight');
          }
        },
        { type: 'separator' },
        {
          label: 'View Logs',
          accelerator: 'CmdOrCtrl+L',
          click: async () => {
            if (logger) {
              const { shell } = require('electron');
              await shell.openPath(logger.getLogDirectory());
            }
          }
        },
        {
          label: 'Clear Logs',
          click: () => {
            if (logger) {
              dialog.showMessageBox(mainWindow, {
                type: 'warning',
                title: 'Clear Logs',
                message: 'Are you sure you want to clear all logs?',
                detail: 'This action cannot be undone.',
                buttons: ['Cancel', 'Clear Logs'],
                defaultId: 0,
                cancelId: 0
              }).then(result => {
                if (result.response === 1) {
                  logger.clearLogs();
                  dialog.showMessageBox(mainWindow, {
                    type: 'info',
                    title: 'Logs Cleared',
                    message: 'All log files have been cleared.'
                  });
                }
              });
            }
          }
        },
        { type: 'separator' },
        {
          label: 'About NeuroInsight',
          click: () => {
            const logDir = logger ? logger.getLogDirectory() : 'Not available';
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About NeuroInsight',
              message: 'NeuroInsight Desktop',
              detail: `Version 1.0.0\n\nAutomated hippocampal asymmetry analysis\nfrom T1-weighted MRI scans.\n\nLogs: ${logDir}`,
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Application lifecycle

app.whenReady().then(async () => {
  log.info('App ready, starting backend...');
  
  // Start backend
  startBackend();
  
  // Create menu
  createMenu();
  
  // Create window
  await createWindow();
  
  log.info('NeuroInsight fully started');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  log.info('Application quitting, stopping backend...');
  stopBackend();
});

app.on('will-quit', (event) => {
  // Ensure backend is stopped
  if (backendProcess) {
    event.preventDefault();
    stopBackend();
    setTimeout(() => {
      app.exit(0);
    }, 1000);
  }
});

// ============================================================================
// CRASH HANDLERS & ERROR LOGGING
// ============================================================================

/**
 * Handle uncaught exceptions in main process
 */
process.on('uncaughtException', (error) => {
  log.error('Uncaught exception:', error);
  
  if (logger) {
    logger.crash('Uncaught exception in main process', error, {
      location: 'main-process',
      action: 'uncaughtException'
    });
  }
  
  // Show error dialog to user
  dialog.showErrorBox(
    'NeuroInsight Error',
    'An unexpected error occurred in the application.\n\n' +
    `Error: ${error.message}\n\n` +
    `Logs saved to: ${logger ? logger.getLogDirectory() : 'unknown'}\n\n` +
    'Please report this issue with the log files.'
  );
});

/**
 * Handle unhandled promise rejections
 */
process.on('unhandledRejection', (reason, promise) => {
  log.error('Unhandled promise rejection:', reason);
  
  if (logger) {
    logger.error('Unhandled promise rejection', reason instanceof Error ? reason : null, {
      location: 'main-process',
      action: 'unhandledRejection',
      reason: String(reason)
    });
  }
});

/**
 * Handle renderer process crashes
 */
app.on('render-process-gone', (event, webContents, details) => {
  log.error('Renderer process gone:', details);
  
  if (logger) {
    logger.crash('Renderer process crashed', null, {
      location: 'renderer-process',
      reason: details.reason,
      exitCode: details.exitCode
    });
  }
  
  // Show error dialog
  dialog.showErrorBox(
    'NeuroInsight Crashed',
    'The application window crashed.\n\n' +
    `Reason: ${details.reason}\n` +
    `Exit Code: ${details.exitCode}\n\n` +
    `Logs saved to: ${logger ? logger.getLogDirectory() : 'unknown'}\n\n` +
    'The application will restart.'
  );
  
  // Restart the app
  if (mainWindow) {
    mainWindow.reload();
  }
});

/**
 * Handle GPU process crashes
 */
app.on('gpu-process-crashed', (event, killed) => {
  log.error('GPU process crashed, killed:', killed);
  
  if (logger) {
    logger.error('GPU process crashed', null, {
      location: 'gpu-process',
      killed: killed
    });
  }
});

// ============================================================================
// IPC HANDLERS FOR LOG ACCESS
// ============================================================================

/**
 * Get log directory path (for showing to users)
 */
ipcMain.handle('get-log-directory', () => {
  return logger ? logger.getLogDirectory() : null;
});

/**
 * Get recent log entries (for in-app display)
 */
ipcMain.handle('get-recent-logs', (event, count = 50) => {
  return logger ? logger.getRecentLogs(count) : [];
});

/**
 * Open log directory in file explorer
 */
ipcMain.handle('open-log-directory', async () => {
  if (logger) {
    const { shell } = require('electron');
    await shell.openPath(logger.getLogDirectory());
  }
});

/**
 * Clear all logs
 */
ipcMain.handle('clear-logs', () => {
  if (logger) {
    logger.clearLogs();
    return true;
  }
  return false;
});

