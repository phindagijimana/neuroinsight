/**
 * NeuroInsight Desktop - Main Process
 * 
 * Manages application lifecycle and backend process.
 */

const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const log = require('electron-log');
const waitOn = require('wait-on');

// Set up logging
log.transports.file.level = 'info';
log.info('NeuroInsight Desktop starting...');

let mainWindow = null;
let backendProcess = null;
const BACKEND_PORT = 8000;

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

  // Log backend output
  backendProcess.stdout.on('data', (data) => {
    log.info('[Backend]', data.toString().trim());
  });

  backendProcess.stderr.on('data', (data) => {
    log.error('[Backend Error]', data.toString().trim());
  });

  backendProcess.on('error', (error) => {
    log.error('Failed to start backend:', error);
  });

  backendProcess.on('close', (code) => {
    log.info(`Backend process exited with code ${code}`);
    if (code !== 0 && code !== null) {
      log.error('Backend crashed unexpectedly');
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
    },
    show: false,  // Don't show until ready
    backgroundColor: '#1a1a1a',
    title: 'NeuroInsight',
  });

  // Wait for backend to be ready
  try {
    log.info('Waiting for backend to be ready...');
    
    await waitOn({
      resources: [`http://localhost:${BACKEND_PORT}/health`],
      timeout: 30000,  // 30 seconds
      interval: 1000,   // Check every second
    });
    
    log.info('Backend is ready!');
    
    // Load the application
    mainWindow.loadURL(`http://localhost:${BACKEND_PORT}`);
    
    // Show window when ready, close splash
    mainWindow.once('ready-to-show', () => {
      splash.close();
      mainWindow.show();
      log.info('Application window shown');
    });
    
  } catch (error) {
    log.error('Backend failed to start within timeout:', error);
    
    // Show error dialog
    const { dialog } = require('electron');
    dialog.showErrorBox(
      'NeuroInsight Startup Error',
      'Failed to start NeuroInsight backend.\n\nPlease check if:\n' +
      '- You have sufficient disk space\n' +
      '- Antivirus is not blocking the application\n\n' +
      'Error: ' + error.message
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
            await shell.openExternal('https://github.com/yourorg/neuroinsight');
          }
        },
        { type: 'separator' },
        {
          label: 'About NeuroInsight',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About NeuroInsight',
              message: 'NeuroInsight Desktop',
              detail: 'Version 1.0.0\n\nAutomated hippocampal asymmetry analysis\nfrom T1-weighted MRI scans.',
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

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  log.error('Uncaught exception:', error);
});

