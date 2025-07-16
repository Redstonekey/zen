const { contextBridge, ipcRenderer } = require('electron');

// Optionally expose secure APIs to renderer
contextBridge.exposeInMainWorld('electronAPI', {});
