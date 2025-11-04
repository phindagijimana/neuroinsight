/**
 * Docker Manager
 * 
 * Manages Docker Desktop integration and container operations
 */

const Docker = require('dockerode');
const { exec } = require('child_process');
const { promisify } = require('util');
const logger = require('../utils/logger');

const execAsync = promisify(exec);

// Common Docker installation paths (for macOS GUI apps that don't inherit PATH)
const DOCKER_PATHS = [
  '/usr/local/bin',
  '/usr/bin',
  '/opt/homebrew/bin',
  '/Applications/Docker.app/Contents/Resources/bin',
  process.env.PATH || ''
].join(':');

class DockerManager {
  constructor() {
    this.docker = null;
    this.isAvailable = false;
    this.dockerDesktopRunning = false;
  }

  /**
   * Check if Docker is installed
   */
  async isDockerInstalled() {
    try {
      await execAsync('docker --version', { env: { ...process.env, PATH: DOCKER_PATHS } });
      return true;
    } catch (error) {
      logger.debug('Docker not found in PATH:', error.message);
      return false;
    }
  }

  /**
   * Check if Docker Desktop is running
   */
  async isDockerRunning() {
    try {
      const docker = new Docker();
      await docker.ping();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Start Docker Desktop (platform-specific)
   */
  async startDockerDesktop() {
    const platform = process.platform;
    
    try {
      logger.info('Attempting to start Docker Desktop...');
      
      if (platform === 'darwin') {
        // macOS
        await execAsync('open -a Docker', { env: { ...process.env, PATH: DOCKER_PATHS } });
      } else if (platform === 'win32') {
        // Windows
        await execAsync('start "" "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"', { env: { ...process.env, PATH: DOCKER_PATHS } });
      } else if (platform === 'linux') {
        // Linux - Docker daemon
        await execAsync('sudo systemctl start docker', { env: { ...process.env, PATH: DOCKER_PATHS } });
      }
      
      // Wait for Docker to be ready
      return await this.waitForDocker(60000); // 60 second timeout
      
    } catch (error) {
      logger.error('Failed to start Docker Desktop:', error);
      throw new Error(`Failed to start Docker Desktop: ${error.message}`);
    }
  }

  /**
   * Wait for Docker to become available
   */
  async waitForDocker(timeout = 30000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        const docker = new Docker();
        await docker.ping();
        logger.info('Docker is now available');
        this.docker = docker;
        this.isAvailable = true;
        this.dockerDesktopRunning = true;
        return true;
      } catch (error) {
        // Wait 2 seconds before retry
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    throw new Error('Docker did not become available within timeout');
  }

  /**
   * Initialize Docker connection
   */
  async initialize() {
    logger.info('Initializing Docker connection...');
    
    // Check if Docker is installed
    const installed = await this.isDockerInstalled();
    if (!installed) {
      throw new Error('Docker is not installed. Please install Docker Desktop.');
    }
    
    // Check if Docker is running
    const running = await this.isDockerRunning();
    if (!running) {
      logger.warn('Docker is not running, attempting to start...');
      await this.startDockerDesktop();
    } else {
      this.docker = new Docker();
      this.isAvailable = true;
      this.dockerDesktopRunning = true;
      logger.info('Docker is already running');
    }
    
    return this.isAvailable;
  }

  /**
   * Pull a Docker image
   */
  async pullImage(imageName, onProgress) {
    if (!this.docker) {
      throw new Error('Docker is not initialized');
    }
    
    logger.info(`Pulling image: ${imageName}`);
    
    return new Promise((resolve, reject) => {
      this.docker.pull(imageName, (err, stream) => {
        if (err) {
          reject(err);
          return;
        }
        
        this.docker.modem.followProgress(stream, (err, output) => {
          if (err) {
            reject(err);
          } else {
            resolve(output);
          }
        }, (event) => {
          if (onProgress) {
            onProgress(event);
          }
        });
      });
    });
  }

  /**
   * List running containers
   */
  async listContainers(all = false) {
    if (!this.docker) {
      throw new Error('Docker is not initialized');
    }
    
    return await this.docker.listContainers({ all });
  }

  /**
   * Get container by name
   */
  async getContainer(name) {
    const containers = await this.listContainers(true);
    const container = containers.find(c => 
      c.Names.some(n => n.includes(name))
    );
    
    if (container) {
      return this.docker.getContainer(container.Id);
    }
    
    return null;
  }

  /**
   * Check container health
   */
  async checkContainerHealth(name) {
    const container = await this.getContainer(name);
    if (!container) {
      return 'not_found';
    }
    
    const info = await container.inspect();
    
    if (info.State.Running) {
      if (info.State.Health) {
        return info.State.Health.Status;
      }
      return 'running';
    }
    
    return 'stopped';
  }

  /**
   * Get Docker system info
   */
  async getSystemInfo() {
    if (!this.docker) {
      throw new Error('Docker is not initialized');
    }
    
    return await this.docker.info();
  }

  /**
   * Get Docker version
   */
  async getVersion() {
    if (!this.docker) {
      throw new Error('Docker is not initialized');
    }
    
    return await this.docker.version();
  }
}

module.exports = DockerManager;


