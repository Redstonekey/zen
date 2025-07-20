const { app, BrowserWindow, ipcMain, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

// Python backend server integration
let pyProc = null;
const pyPort = 5000;

function startServer() {
  // Launch the Python server at project root
  const script = path.join(__dirname, '..', 'server.py');
  // Run server.py in project root so config paths resolve
  pyProc = spawn('python', [script], { cwd: path.join(__dirname, '..') });
  if (pyProc) {
    console.log('Python server started on port', pyPort);
    pyProc.stdout.on('data', data => console.log(`PYTHON: ${data}`));
    pyProc.stderr.on('data', data => console.error(`PYTHON ERR: ${data}`));
  }
}

function stopServer() {
  if (pyProc) {
    pyProc.kill();
    pyProc = null;
  }
}

function createWindow() {
  // Create high-quality icon
  const iconPath = path.join(__dirname, 'icon.png');
  const icon = nativeImage.createFromPath(iconPath);
  
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    frame: false, // Remove the default title bar and window controls
    icon: icon, // Use nativeImage for better quality
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Load the app from the local Flask backend
  win.loadURL(`http://127.0.0.1:${pyPort}`);
  
  return win;
}

// IPC handlers for window controls
ipcMain.handle('window-minimize', () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) win.minimize();
});

ipcMain.handle('window-maximize', () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) {
    if (win.isMaximized()) {
      win.unmaximize();
    } else {
      win.maximize();
    }
  }
});

ipcMain.handle('window-close', () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) win.close();
});

// Start backend and wait for it before opening the window
app.whenReady().then(() => {
  startServer();
  // Poll the Python server until it's ready
  const waitForServer = () => new Promise((resolve, reject) => {
    const tryConnect = () => {
      http.get({ host: '127.0.0.1', port: pyPort, path: '/' }, res => resolve())
        .on('error', () => setTimeout(tryConnect, 500));
    };
    tryConnect();
  });
  waitForServer()
    .then(() => createWindow())
    .catch(err => console.error('Server failed to start:', err));
});

// Stop backend on all windows closed and quit
app.on('window-all-closed', () => {
  stopServer();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

// Ensure Python server is stopped on quit
app.on('quit', stopServer);
