/**
 * NeuroInsight Desktop - Preload Script
 * 
 * Exposes safe APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // System information
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Service management
  getServiceStatus: () => ipcRenderer.invoke('get-service-status'),
  restartServices: () => ipcRenderer.invoke('restart-services'),
  stopServices: () => ipcRenderer.invoke('stop-services'),
  
  // File operations
  openDataFolder: () => ipcRenderer.invoke('open-data-folder'),
  getLogs: (logType) => ipcRenderer.invoke('get-logs', logType),
  
  // Platform info
  platform: process.platform,
  version: process.env.npm_package_version || '1.0.0'
});


