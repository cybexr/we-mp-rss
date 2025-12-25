# Scripts Directory Documentation

## Overview

The `script` directory contains shell scripts and automation utilities for system setup, development environment preparation, and maintenance tasks in the WeChat Mini Program RSS Reader project.

## Script Components

### System Setup Scripts

#### install_firefox.sh
- Firefox browser installation
- Dependency setup for web scraping
- Headless browser configuration
- WebDriver setup for automated testing

#### pip.sh
- Python package manager setup
- Virtual environment configuration
- Dependency installation automation
- Package version management

#### gtk.sh
- GTK library installation
- GUI dependency setup
- Display server configuration
- Graphics library support

### Utility Scripts

#### .gitignore
- Version control ignore rules
- Temporary file exclusions
- Build artifact filtering
- Sensitive file protection

## Script Usage

### Execution Patterns
```bash
# Make scripts executable
chmod +x script/*.sh

# Run installation scripts
./script/install_firefox.sh
./script/pip.sh
./script/gtk.sh
```

### Environment Setup
The scripts automate:
- System dependency installation
- Development environment preparation
- Build tool configuration
- Runtime environment setup

## Platform Support

### Linux Systems
- Ubuntu/Debian package management
- RedHat/CentOS support
- Arch Linux compatibility
- Package repository configuration

### WSL Support
- Windows Subsystem for Linux compatibility
- Path handling adjustments
- Service integration
- Display configuration

## Maintenance

### Script Updates
- Regular package version updates
- Security patch application
- Compatibility testing
- Documentation maintenance

### Error Handling
- Exit code management
- Error logging
- Rollback mechanisms
- User feedback