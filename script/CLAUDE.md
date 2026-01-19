# `script` Directory

## Purpose and Scope
This directory serves as a collection of various utility shell scripts designed to automate common development and system administration tasks. Its primary purpose is to provide ready-to-use scripts for software installation, configuration, and specific system operations, such as mounting cloud storage.

## Structure Overview
The `script` directory contains several standalone shell scripts and one subdirectory, `obs`, which has its own dedicated documentation. Each script focuses on a specific task, promoting modularity.

## Key Components

### `20251225_add_feed_cache_fields.sql`
- Description: A SQL script likely used for database migrations or schema updates, specifically to add fields related to a feed cache.
- Responsibilities: Modifies a database schema.
- Key Methods: Not applicable, as this is a SQL script, not an executable function. Its "execution" is applying the SQL commands.

### `gtk.sh`
- Description: A shell script to install GTK development libraries (version 3.24.33) on Debian-based or RedHat-based Linux systems.
- Responsibilities: Automates the download, compilation, and installation of GTK.
- Key Methods:
  #### `main()`
  - Purpose: Checks for root privileges, identifies the Linux distribution, and then proceeds to download, extract, configure, compile, and install GTK 3.24.33. It handles dependencies like `wget`, `build-essential`, `gcc`, and `make` based on the detected OS.
  - Parameters: None
  - Returns: (void) Exits if not run as root, if the Linux distribution is unsupported, or if any step of the installation fails.

### `install_firefox.sh`
- Description: A shell script to download, extract, and install a specific version of Firefox (139.0) to `/opt/firefox`. It also configures the system's PATH.
- Responsibilities: Provides an automated way to install Firefox.
- Key Methods:
  #### `main()`
  - Purpose: Downloads the `firefox-139.0.tar.xz` archive, creates the `/opt/firefox` installation directory, extracts the Firefox files into it, cleans up the downloaded archive, sets appropriate file permissions, and adds the Firefox binary to the system's `PATH` by modifying `~/.bashrc` and creating a symlink in `/usr/local/bin/`.
  - Parameters: None
  - Returns: (void)

### `pip.sh`
- Description: A shell script that allows the user to interactively select a PyPI (Python Package Index) mirror source and then configures `pip` to use the chosen mirror by creating or updating the `~/.pip/pip.conf` file.
- Responsibilities: Simplifies changing `pip`'s package source for faster downloads.
- Key Methods:
  #### `main()`
  - Purpose: Displays a numbered list of common PyPI mirror sources (Tsinghua, Aliyun, USTC, Douban, Huawei Cloud). It prompts the user to select a source, then creates the `~/.pip` directory if it doesn't exist, and generates a `pip.conf` file with the selected mirror's `index-url` and `trusted-host`. Finally, it displays the updated `pip` configuration.
  - Parameters: None
  - Returns: (void)

### `obs/CLAUDE.md`
- Description: Documentation for the scripts located in the `obs` subdirectory.
- Responsibilities: Details the purpose, structure, components, dependencies, integration, and implementation notes for OBS related scripts.
- Key Methods: Not applicable, this is a documentation file. Refer to `obs/CLAUDE.md` for details.

## Dependencies

### Internal Dependencies
- `obs/` - This subdirectory contains scripts and configuration related to mounting Huawei Cloud OBS buckets. Refer to `obs/CLAUDE.md` for specific details.

### External Dependencies
- `wget` - Used by `gtk.sh` and `install_firefox.sh` for downloading files.
- `build-essential` (Debian/Ubuntu) - Used by `gtk.sh` for compiling software.
- `gcc`, `make` (RedHat/CentOS) - Used by `gtk.sh` for compiling software.
- `apt-get` (Debian/Ubuntu) - Package manager used by `gtk.sh`.
- `yum` (RedHat/CentOS) - Package manager used by `gtk.sh`.
- `tar` - Used by `gtk.sh` and `install_firefox.sh` for extracting archives.
- `mkdir` - Used by `install_firefox.sh` and `pip.sh` for creating directories.
- `rm` - Used by `install_firefox.sh` for removing temporary files.
- `chmod` - Used by `install_firefox.sh` for setting file permissions.
- `grep` - Used by `install_firefox.sh` and `pip.sh` for searching text.
- `echo` - Used by all scripts for displaying output.
- `source` - Used by `install_firefox.sh` for applying `.bashrc` changes.
- `ln` - Used by `install_firefox.sh` for creating symlinks.
- `cat` - Used by `pip.sh` for writing to `pip.conf`.
- `sed` - Used by `pip.sh` for text manipulation (extracting trusted host).
- `pip` - Used by `pip.sh` to display configuration.
- `bash` - The shell interpreter for all shell scripts in this directory.

## Integration Points

### Command Line Interface
- All shell scripts are designed to be executed directly from the command line.
- Some scripts (`obs.sh` within `obs/`) accept arguments (e.g., `mount`, `umount`, `-f`).

### Configuration Files
- `pip.sh` interacts with `~/.pip/pip.conf` for pip mirror configuration.
- The `obs` subdirectory contains `obs.conf` for OBS bucket configuration.

## Implementation Notes

### Design Patterns
- **Procedural Scripting**: Most scripts follow a linear execution flow, performing steps in sequence.
- **Conditional Logic**: Scripts like `gtk.sh` use `if/else` statements for OS-specific actions.
- **Interactive Input**: `pip.sh` uses `select` for interactive user choices.

### Technical Decisions
- **Shell Scripting**: Bash is primarily used due to its ubiquity in Linux environments for system automation.
- **OS Detection**: `gtk.sh` includes basic OS detection to adapt to different package managers.
- **PATH Modification**: `install_firefox.sh` modifies `~/.bashrc` and uses symlinks for user convenience.
- **Credential Handling (OBS)**: As documented in `obs/CLAUDE.md`, OBS credentials are handled by writing to `/etc/passwd-s3fs` with restricted permissions for security.

### Considerations
- **Portability**: While some scripts attempt OS detection, most are primarily designed for Linux environments. Windows compatibility is generally not a primary concern, or specific instructions are provided for Windows users (as seen in `obs/CLAUDE.md`).
- **User Privileges**: Scripts like `gtk.sh` and those in `obs/` require root privileges for certain operations (e.g., system-wide installations, mounting filesystems).
- **Environment Variables**: Scripts may rely on or modify environment variables (e.g., `PATH`).
- **Idempotency**: Some scripts are not fully idempotent; repeated execution without prior cleanup might lead to issues (e.g., `install_firefox.sh` appending to `.bashrc` multiple times if not checked properly).
- **Security**: For scripts handling credentials or performing system-level changes, appropriate permission settings and secure handling of sensitive information are critical (e.g., `obs/CLAUDE.md` details `chmod 600` for `passwd-s3fs`).
