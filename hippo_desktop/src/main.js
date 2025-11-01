/**
 * NeuroInsight Desktop - Main Process
 * 
 * Electron main process that manages:
 * - Application lifecycle
 * - Docker service management
 * - System tray integration
 * - Window management
 */

const { app, BrowserWindow, Tray, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');
const DockerManager = require('./managers/DockerManager');
const ServiceManager = require('./managers/ServiceManager');
const SystemChecker = require('./utils/SystemChecker');
const logger = require('./utils/logger');

// Store for persisting user settings
const store = new Store();

// Global references
let mainWindow = null;
let tray = null;
let dockerManager = null;
let serviceManager = null;
let isQuitting = false;

// Check if running in development mode
const isDev = process.argv.includes('--dev') || process.env.NODE_ENV === 'development';

// App paths
const appPath = app.isPackaged 
  ? path.join(process.resourcesPath, 'app')
  : path.join(__dirname, '..', '..');

const userDataPath = app.getPath('userData');
const dataDir = path.join(userDataPath, 'data');

// Ensure data directories exist
const ensureDirectories = () => {
  const dirs = [
    dataDir,
    path.join(dataDir, 'uploads'),
    path.join(dataDir, 'outputs'),
    path.join(dataDir, 'logs'),
    path.join(dataDir, 'database')
  ];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
};

/**
 * Create the main application window
 */
const createWindow = () => {
  const windowState = store.get('windowState', {
    width: 1400,
    height: 900,
    x: undefined,
    y: undefined
  });

  mainWindow = new BrowserWindow({
    width: windowState.width,
    height: windowState.height,
    x: windowState.x,
    y: windowState.y,
    minWidth: 1024,
    minHeight: 768,
    title: 'NeuroInsight',
    icon: path.join(__dirname, '../assets/icon.png'),
    backgroundColor: '#1e293b',
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      devTools: isDev
    }
  });

  // Save window state on close
  mainWindow.on('close', (event) => {
    if (!isQuitting && process.platform === 'darwin') {
      event.preventDefault();
      mainWindow.hide();
      return;
    }

    const bounds = mainWindow.getBounds();
    store.set('windowState', bounds);
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Open external links in default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Load the frontend
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadURL('http://localhost:56052/hippo_new_version.html');
  }
};

/**
 * Create system tray icon and menu
 */
const createTray = () => {
  const iconPath = path.join(__dirname, '../assets', 
    process.platform === 'darwin' ? 'tray-icon-Template.png' : 'tray-icon.png'
  );

  tray = new Tray(iconPath);
  tray.setToolTip('NeuroInsight');

  const updateTrayMenu = (status) => {
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'NeuroInsight',
        type: 'normal',
        enabled: false
      },
      {
        type: 'separator'
      },
      {
        label: `Status: ${status}`,
        type: 'normal',
        enabled: false
      },
      {
        type: 'separator'
      },
      {
        label: 'Open NeuroInsight',
        click: () => {
          if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
          } else {
            createWindow();
          }
        }
      },
      {
        label: 'View Logs',
        click: () => {
          shell.openPath(path.join(dataDir, 'logs'));
        }
      },
      {
        type: 'separator'
      },
      {
        label: 'Restart Services',
        click: async () => {
          try {
            await serviceManager.restart();
            updateTrayMenu('Running');
          } catch (error) {
            logger.error('Failed to restart services:', error);
          }
        }
      },
      {
        label: 'Stop Services',
        click: async () => {
          try {
            await serviceManager.stop();
            updateTrayMenu('Stopped');
          } catch (error) {
            logger.error('Failed to stop services:', error);
          }
        }
      },
      {
        type: 'separator'
      },
      {
        label: 'Preferences',
        click: () => {
          // TODO: Open preferences window
        }
      },
      {
        type: 'separator'
      },
      {
        label: 'Quit NeuroInsight',
        click: () => {
          isQuitting = true;
          app.quit();
        }
      }
    ]);

    tray.setContextMenu(contextMenu);
  };

  // Initial menu
  updateTrayMenu('Starting...');

  // Double-click to show window
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  return updateTrayMenu;
};

/**
 * Show first-run setup wizard
 */
const showSetupWizard = async () => {
  const setupWindow = new BrowserWindow({
    width: 800,
    height: 600,
    resizable: false,
    title: 'NeuroInsight Setup',
    icon: path.join(__dirname, '../assets/icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  setupWindow.loadFile(path.join(__dirname, 'setup.html'));
  
  return new Promise((resolve) => {
    setupWindow.on('closed', () => {
      resolve();
    });
  });
};

/**
 * Initialize the application
 */
const initialize = async () => {
  try {
    logger.info('Starting NeuroInsight Desktop...');
    
    // Ensure directories exist
    ensureDirectories();
    
    // Check system requirements
    logger.info('Checking system requirements...');
    const systemChecker = new SystemChecker();
    const requirements = await systemChecker.checkAll();
    
    if (!requirements.passed) {
      logger.error('System requirements not met');
      
      const result = await dialog.showMessageBox({
        type: 'error',
        title: 'System Requirements Not Met',
        message: 'Your system does not meet the minimum requirements for NeuroInsight.',
        detail: requirements.failures.join('\n'),
        buttons: ['View Requirements', 'Exit'],
        defaultId: 0
      });
      
      if (result.response === 0) {
        shell.openExternal('https://neuroinsight.app/requirements');
      }
      
      app.quit();
      return;
    }
    
    // Check if first run
    const isFirstRun = !store.has('setupCompleted');
    
    if (isFirstRun) {
      logger.info('First run detected, showing setup wizard...');
      await showSetupWizard();
      store.set('setupCompleted', true);
    }
    
    // Initialize managers
    logger.info('Initializing Docker manager...');
    dockerManager = new DockerManager();
    
    logger.info('Initializing service manager...');
    serviceManager = new ServiceManager(dockerManager, {
      appPath,
      dataDir,
      isDev
    });
    
    // Create tray
    logger.info('Creating system tray...');
    const updateTrayMenu = createTray();
    
    // Start services
    logger.info('Starting services...');
    updateTrayMenu('Starting services...');
    
    try {
      await serviceManager.start();
      updateTrayMenu('Running');
      logger.info('Services started successfully');
      
      // Create main window
      createWindow();
      
    } catch (error) {
      logger.error('Failed to start services:', error);
      updateTrayMenu('Error');
      
      const result = await dialog.showMessageBox({
        type: 'error',
        title: 'Failed to Start Services',
        message: 'NeuroInsight could not start the required services.',
        detail: error.message,
        buttons: ['View Logs', 'Retry', 'Exit'],
        defaultId: 1
      });
      
      if (result.response === 0) {
        shell.openPath(path.join(dataDir, 'logs'));
      } else if (result.response === 1) {
        await initialize();
        return;
      } else {
        app.quit();
        return;
      }
    }
    
  } catch (error) {
    logger.error('Initialization error:', error);
    
    dialog.showErrorBox(
      'Initialization Error',
      `Failed to initialize NeuroInsight:\n\n${error.message}`
    );
    
    app.quit();
  }
};

/**
 * Handle IPC messages
 */
ipcMain.handle('get-system-info', async () => {
  const systemChecker = new SystemChecker();
  return await systemChecker.getInfo();
});

ipcMain.handle('get-service-status', async () => {
  if (!serviceManager) return { running: false };
  return await serviceManager.getStatus();
});

ipcMain.handle('restart-services', async () => {
  if (!serviceManager) throw new Error('Service manager not initialized');
  return await serviceManager.restart();
});

ipcMain.handle('stop-services', async () => {
  if (!serviceManager) throw new Error('Service manager not initialized');
  return await serviceManager.stop();
});

ipcMain.handle('open-data-folder', () => {
  shell.openPath(dataDir);
});

ipcMain.handle('get-logs', async (event, logType) => {
  const logPath = path.join(dataDir, 'logs', `${logType}.log`);
  if (fs.existsSync(logPath)) {
    return fs.readFileSync(logPath, 'utf-8');
  }
  return '';
});

/**
 * App lifecycle events
 */
app.whenReady().then(initialize);

app.on('window-all-closed', () => {
  // On macOS, keep app running in dock
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS, recreate window when dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', async (event) => {
  if (!isQuitting) {
    event.preventDefault();
    isQuitting = true;
    
    logger.info('Shutting down NeuroInsight...');
    
    // Stop services
    if (serviceManager) {
      try {
        await serviceManager.stop();
        logger.info('Services stopped successfully');
      } catch (error) {
        logger.error('Error stopping services:', error);
      }
    }
    
    app.quit();
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception:', error);
  dialog.showErrorBox('Error', `An unexpected error occurred:\n\n${error.message}`);
});

process.on('unhandledRejection', (error) => {
  logger.error('Unhandled rejection:', error);
});


