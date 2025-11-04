/**
 * Docker Compose Wrapper
 * 
 * Handles both docker-compose (v1) and docker compose (v2)
 * Automatically detects which version is available and uses it
 */

const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const logger = require('./logger');

const execAsync = promisify(exec);

class ComposeWrapper {
  constructor() {
    this.composeCommand = null;
    this.composeArgs = null;
  }

  /**
   * Detect which Docker Compose version is available
   */
  async detect() {
    if (this.composeCommand) {
      return this.composeCommand;
    }

    // Try docker compose (v2 - built into Docker CLI)
    try {
      await execAsync('docker compose version');
      this.composeCommand = 'docker';
      this.composeArgs = ['compose'];
      logger.info('Detected Docker Compose v2 (docker compose)');
      return 'docker compose';
    } catch (error) {
      // v2 not available
    }

    // Try docker-compose (v1 - standalone binary)
    try {
      await execAsync('docker-compose version');
      this.composeCommand = 'docker-compose';
      this.composeArgs = [];
      logger.info('Detected Docker Compose v1 (docker-compose)');
      return 'docker-compose';
    } catch (error) {
      // v1 not available
    }

    throw new Error(
      'Docker Compose not found. Please ensure Docker Desktop is installed and running.\n\n' +
      'macOS: Install Docker Desktop from https://www.docker.com/products/docker-desktop\n' +
      'Windows: Install Docker Desktop from https://www.docker.com/products/docker-desktop\n' +
      'Linux: Install docker-compose or docker-compose-plugin'
    );
  }

  /**
   * Run docker-compose up
   */
  async up(options = {}) {
    await this.detect();

    const args = [
      ...this.composeArgs,
      '-f', options.config || 'docker-compose.yml',
      'up', '-d'
    ];

    if (options.build) {
      args.push('--build');
    }

    return this.run(args, options.cwd);
  }

  /**
   * Run docker-compose down
   */
  async down(options = {}) {
    await this.detect();

    const args = [
      ...this.composeArgs,
      '-f', options.config || 'docker-compose.yml',
      'down'
    ];

    if (options.volumes) {
      args.push('-v');
    }

    return this.run(args, options.cwd);
  }

  /**
   * Run docker-compose ps
   */
  async ps(options = {}) {
    await this.detect();

    const args = [
      ...this.composeArgs,
      '-f', options.config || 'docker-compose.yml',
      'ps'
    ];

    return this.run(args, options.cwd);
  }

  /**
   * Run docker-compose logs
   */
  async logs(options = {}) {
    await this.detect();

    const args = [
      ...this.composeArgs,
      '-f', options.config || 'docker-compose.yml',
      'logs'
    ];

    if (options.service) {
      args.push(options.service);
    }

    if (options.tail) {
      args.push('--tail', options.tail.toString());
    }

    if (options.follow) {
      args.push('-f');
    }

    return this.run(args, options.cwd);
  }

  /**
   * Run docker-compose restart
   */
  async restart(options = {}) {
    await this.detect();

    const args = [
      ...this.composeArgs,
      '-f', options.config || 'docker-compose.yml',
      'restart'
    ];

    if (options.service) {
      args.push(options.service);
    }

    return this.run(args, options.cwd);
  }

  /**
   * Run a docker-compose command
   */
  async run(args, cwd) {
    return new Promise((resolve, reject) => {
      const childProcess = spawn(this.composeCommand, args, {
        cwd: cwd || process.cwd(),
        env: { ...process.env }
      });

      let stdout = '';
      let stderr = '';

      childProcess.stdout.on('data', (data) => {
        const output = data.toString();
        stdout += output;
        if (logger) {
          logger.debug('[docker-compose]', output.trim());
        }
      });

      childProcess.stderr.on('data', (data) => {
        const output = data.toString();
        stderr += output;
        if (logger) {
          logger.debug('[docker-compose]', output.trim());
        }
      });

      childProcess.on('close', (code) => {
        if (code === 0) {
          resolve({ out: stdout, err: stderr, exitCode: code });
        } else {
          const error = new Error(`Docker Compose command failed with exit code ${code}`);
          error.stdout = stdout;
          error.stderr = stderr;
          error.exitCode = code;
          reject(error);
        }
      });

      childProcess.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Check if Docker Compose is available
   */
  async isAvailable() {
    try {
      await this.detect();
      return true;
    } catch (error) {
      return false;
    }
  }
}

module.exports = new ComposeWrapper();

