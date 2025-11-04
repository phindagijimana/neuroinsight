/**
 * Service Manager
 * 
 * Manages NeuroInsight services via Docker Compose
 */

const compose = require('../utils/ComposeWrapper');
const path = require('path');
const fs = require('fs');
const fetch = require('node-fetch');
const logger = require('../utils/logger');

class ServiceManager {
  constructor(dockerManager, options = {}) {
    this.dockerManager = dockerManager;
    this.appPath = options.appPath;
    this.dataDir = options.dataDir;
    this.isDev = options.isDev || false;
    this.services = [
      'db',
      'redis',
      'minio',
      'backend',
      'worker',
      'frontend'
    ];
    this.healthCheckUrls = {
      backend: 'http://localhost:8000/health',
      frontend: 'http://localhost:56052'
    };
  }

  /**
   * Start all services
   */
  async start() {
    logger.info('Starting NeuroInsight services...');
    
    // Ensure Docker is running
    if (!this.dockerManager.isAvailable) {
      await this.dockerManager.initialize();
    }
    
    // Set environment variables
    this.setupEnvironment();
    
    // Start services using docker-compose
    const composeOptions = {
      cwd: this.appPath,
      config: 'docker-compose.yml'
    };
    
    try {
      logger.info('Running docker-compose up...');
      
      const result = await compose.up(composeOptions);
      logger.info('Docker Compose result:', result);
      
      // Wait for services to be healthy
      logger.info('Waiting for services to be healthy...');
      await this.waitForServices();
      
      logger.info('All services started successfully');
      return true;
      
    } catch (error) {
      logger.error('Failed to start services:', error);
      throw error;
    }
  }

  /**
   * Stop all services
   */
  async stop() {
    logger.info('Stopping NeuroInsight services...');
    
    const composeOptions = {
      cwd: this.appPath,
      config: 'docker-compose.yml'
    };
    
    try {
      await compose.down(composeOptions);
      logger.info('Services stopped successfully');
      return true;
    } catch (error) {
      logger.error('Failed to stop services:', error);
      throw error;
    }
  }

  /**
   * Restart all services
   */
  async restart() {
    logger.info('Restarting NeuroInsight services...');
    
    await this.stop();
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
    await this.start();
    
    return true;
  }

  /**
   * Get service status
   */
  async getStatus() {
    try {
      const composeOptions = {
        cwd: this.appPath
      };
      
      const psResult = await compose.ps(composeOptions);
      
      const status = {
        running: false,
        services: {}
      };
      
      // Parse docker-compose ps output
      for (const service of this.services) {
        const health = await this.dockerManager.checkContainerHealth(service);
        status.services[service] = {
          status: health,
          healthy: health === 'healthy' || health === 'running'
        };
      }
      
      // Check if all services are running
      status.running = Object.values(status.services).every(s => s.healthy);
      
      return status;
      
    } catch (error) {
      logger.error('Failed to get service status:', error);
      return {
        running: false,
        services: {},
        error: error.message
      };
    }
  }

  /**
   * Setup environment variables
   */
  setupEnvironment() {
    // Set data directory paths
    process.env.NEUROINSIGHT_DATA_DIR = this.dataDir;
    process.env.UPLOADS_DIR = path.join(this.dataDir, 'uploads');
    process.env.OUTPUTS_DIR = path.join(this.dataDir, 'outputs');
    process.env.DB_PATH = path.join(this.dataDir, 'database');
    
    // Database settings
    process.env.POSTGRES_USER = 'neuroinsight';
    process.env.POSTGRES_PASSWORD = 'neuroinsight_desktop';
    process.env.POSTGRES_DB = 'neuroinsight';
    process.env.POSTGRES_HOST = 'localhost';
    process.env.POSTGRES_PORT = '5432';
    
    // Redis settings
    process.env.REDIS_HOST = 'localhost';
    process.env.REDIS_PORT = '6379';
    
    // MinIO settings
    process.env.MINIO_ACCESS_KEY = 'minioadmin';
    process.env.MINIO_SECRET_KEY = 'minioadmin';
    process.env.MINIO_ENDPOINT = 'localhost:9000';
    
    // Application settings
    process.env.ENVIRONMENT = this.isDev ? 'development' : 'production';
    process.env.LOG_LEVEL = this.isDev ? 'DEBUG' : 'INFO';
    
    logger.info('Environment variables configured');
  }

  /**
   * Wait for services to be healthy
   */
  async waitForServices(timeout = 120000) {
    const startTime = Date.now();
    const checkInterval = 3000; // Check every 3 seconds
    
    logger.info('Waiting for services to be healthy...');
    
    while (Date.now() - startTime < timeout) {
      try {
        // Check backend health
        const backendHealthy = await this.checkHealth(this.healthCheckUrls.backend);
        
        if (backendHealthy) {
          logger.info('Backend is healthy');
          
          // Give frontend a bit more time
          await new Promise(resolve => setTimeout(resolve, 5000));
          
          const frontendHealthy = await this.checkHealth(this.healthCheckUrls.frontend);
          
          if (frontendHealthy) {
            logger.info('All services are healthy');
            return true;
          }
        }
        
      } catch (error) {
        // Service not ready yet
      }
      
      // Wait before next check
      await new Promise(resolve => setTimeout(resolve, checkInterval));
      logger.info('Still waiting for services...');
    }
    
    throw new Error('Services did not become healthy within timeout');
  }

  /**
   * Check if a service is healthy
   */
  async checkHealth(url, retries = 3) {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, {
          method: 'GET',
          timeout: 5000
        });
        
        if (response.ok) {
          return true;
        }
      } catch (error) {
        if (i === retries - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    return false;
  }

  /**
   * Get service logs
   */
  async getLogs(serviceName, lines = 100) {
    const composeOptions = {
      cwd: this.appPath,
      config: 'docker-compose.yml',
      service: serviceName,
      tail: lines
    };
    
    try {
      const result = await compose.logs(composeOptions);
      return result.out;
    } catch (error) {
      logger.error(`Failed to get logs for ${serviceName}:`, error);
      return '';
    }
  }
}

module.exports = ServiceManager;


