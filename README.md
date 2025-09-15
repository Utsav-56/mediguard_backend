# 🛠️ MediGuard Backend Setup Guide

This guide will walk you through setting up the backend for **MediGuard software** so you can run it locally without errors. It is written in a **beginner-friendly** way and covers **Windows, macOS, and Linux**.

---

## 📑 Table of Contents

- [🚀 Quick Start (Automated Setup)](#-quick-start-automated-setup)
  - [Windows (PowerShell)](#windows-powershell)
  - [Linux/macOS (Bash)](#linuxmacos-bash)
- [� Using Development Environment Scripts](#-using-development-environment-scripts)
  - [Windows Environment Script](#windows-environment-script)
  - [Linux/macOS Environment Script](#linuxmacos-environment-script)
  - [Available Commands](#available-commands)
  - [Script Options](#script-options)
- [�📋 Prerequisites](#-prerequisites)
- [📖 Manual Setup](#-manual-setup)
  - [Step 1: Check if Python and UV are installed](#step-1-check-if-python-and-uv-are-installed)
  - [Step 2: Install Missing Dependencies](#step-2-install-missing-dependencies)
  - [Step 3: Setup MediGuard Backend](#step-3-setup-mediguard-backend)
  - [Step 4: Run the Django Server](#step-4-run-the-django-server)
- [✅ Success!](#-success)
- [⚠️ Troubleshooting](#️-troubleshooting)

---

## Cloning the Repository

To get started, you need to clone the MediGuard backend repository from GitHub. Run the following command in your terminal:

```bash
git clone https://github.com/utsav-56/mediguard_backend.git
```

After cloning, navigate into the project directory:

```bash
cd mediguard_backend
```

`Note: The server wont run automatically after cloning. You need to follow the setup steps below. 
steps are both for automated and manual setup.
So feel free to choose any of them.`

---

## 🚀 Quick Start (Automated Setup)

**Recommended for beginners!** Use our automated setup scripts to install everything automatically.

### Windows (PowerShell)

1. Open **PowerShell** as Administrator
2. Navigate to the project directory:
   ```powershell
   cd path\to\mediguard_backend
   ```
3. Run the automated setup script:
   ```powershell
   .\setup.ps1
   ```

### Linux/macOS (Bash)

1. Open **Terminal**
2. Navigate to the project directory:
   ```bash
   cd path/to/mediguard_backend
   ```
3. Make the script executable and run it:
   ```bash
   chmod +x setup
   ./setup
   ```

The automated scripts will:
- ✅ Check if Python is installed (install if missing)
- ✅ Check if UV is installed (install if missing)
- ✅ Set up the virtual environment
- ✅ Install all dependencies
- ✅ Start the Django development server

**Skip to [Success!](#-success) section if the automated setup works!**

---

## � Using Development Environment Scripts

After the initial setup, we provide convenient environment scripts that automatically activate your virtual environment and set up useful command shortcuts. These scripts make development much easier!

### Windows Environment Script

**For Windows users**, use the PowerShell environment script:

```powershell
# Navigate to your project directory
cd path\to\mediguard_backend

# Run the environment script
.\venvshell.ps1
```

**What this script does:**
- ✅ Automatically activates the Python virtual environment
- ✅ Sets up convenient command shortcuts (aliases)
- ✅ Creates the virtual environment if it doesn't exist
- ✅ Provides colored output for better readability

### Linux/macOS Environment Script

**For Linux/macOS users**, use the bash environment script:

```bash
# Navigate to your project directory
cd path/to/mediguard_backend

# Make the script executable (only needed once)
chmod +x venvshell

# Source the script (important: use source or .)
source ./venvshell
# OR
. ./venvshell
```

**⚠️ Important for Linux/macOS:** Always use `source` or `.` before the script name. This ensures the virtual environment and aliases remain active in your current shell session.

### Available Commands

After running the environment script, you'll have access to these convenient shortcuts:

| Command | What it does | Example |
|---------|--------------|---------|
| `py <command>` | Run Python commands via UV | `py --version` |
| `dj <command>` | Run Django management commands | `dj runserver` |
| `createsu` | Create a Django superuser | `createsu` |
| `makemig` | Make migrations and apply them | `makemig` |

**Common Django commands made easy:**

```bash
# Start the development server
dj runserver

# Start server on a different port
dj runserver 8080

# Run database migrations
dj migrate

# Create new migrations
dj makemigrations

# Create and apply migrations in one go
makemig

# Create a new Django app
dj startapp myapp

# Open Django shell
dj shell

# Run tests
dj test

# Create a superuser account
createsu

# Collect static files
dj collectstatic

# Check for any issues
dj check
```

### Script Options

Both scripts support several options for different use cases:

#### Windows (PowerShell)
```powershell
# Show help
.\venvshell.ps1 -Help

# Only set up aliases (skip virtual environment activation)
.\venvshell.ps1 -AliasOnly

# Skip alias creation (only activate virtual environment)
.\venvshell.ps1 -NoAlias

# Enable verbose output for debugging
.\venvshell.ps1 -Verbose
```

#### Linux/macOS (Bash)
```bash
# Show help
source ./venvshell --help

# Only set up aliases (skip virtual environment activation)
source ./venvshell --alias-only

# Skip alias creation (only activate virtual environment)
source ./venvshell --no-alias

# Enable verbose output for debugging
source ./venvshell --verbose
```

**💡 Pro Tips:**

1. **Daily Development Workflow:**
   ```bash
   # Open terminal, navigate to project
   cd path/to/mediguard_backend
   
   # Source the environment script
   source ./venvshell    # Linux/macOS
   # OR
   .\venvshell.ps1       # Windows
   
   # Start coding with shortcuts!
   dj runserver
   ```

2. **Quick Commands:**
   - Use `dj runserver` instead of `uv run manage.py runserver`
   - Use `makemig` instead of running makemigrations + migrate separately
   - Use `py` for any Python commands that need the virtual environment

3. **Troubleshooting:**
   - If commands don't work, make sure you sourced the script (Linux/macOS)
   - Use `--verbose` flag to see what the script is doing
   - Check that your virtual environment exists with `ls .venv`

---

## �📋 Prerequisites

You will need the following installed on your system:

1. **Python (version 3.10 or above recommended)**
2. **UV (Python dependency manager, faster than pip)**

The backend is built in **Python**, and **UV** is used instead of pip for dependency management.

---

## 📖 Manual Setup

### Step 1: Check if Python and UV are installed

#### 🪟 Windows
1. Open **PowerShell** or **CMD**
2. Check Python:
   ```powershell
   python --version
   ```
   **✔️ Expected output:** `Python 3.12.x` (or similar)

3. Check UV:
   ```powershell
   uv --version
   ```
   **✔️ Expected output:** Version number

#### 🐧 Linux / 🍏 macOS
1. Open **Terminal**
2. Check Python:
   ```bash
   python3 --version
   ```
   **✔️ Expected output:** `Python 3.x.x`

3. Check UV:
   ```bash
   uv --version
   ```
   **✔️ Expected output:** Version number

**❌ If either command gives an error (`command not found`), follow the installation steps below.**

---

### Step 2: Install Missing Dependencies

#### 🪟 Windows (using Winget)

**Install Python:**
```powershell
winget install Python.Python.3.12
```

**Install UV:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 🍏 macOS

**1. Install Homebrew (if not installed):**
<details>
<summary><strong>Check if Homebrew is installed</strong></summary>

Check if Homebrew is already installed run the following command:
```bash
brew --version
```

**✔️ Expected output:** Version number

**❌ If you get `brew: command not found`, Homebrew is not installed.**

**❌ If you get `command not found`, follow the installation steps below.**
</details>

<details>
<summary><strong>Install Homebrew</strong></summary>

To install Homebrew, run the following command in your terminal:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, add it to your shell profile:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```
</details>

<br>

**2. Install Python and UV:**
```bash
brew install python
brew install uv
```

#### 🐧 Linux
For different linux distributions, use the appropriate package manager to install Python and pip, then install UV using the provided script.

Some popular distributions are covered below:

<details>
<summary><strong>Debian/Ubuntu-based</strong></summary>
This includes **Ubuntu**, **Linux Mint**, **Pop!_OS**, **Debian**, and other Debian/Ubuntu derivatives.

<details>
<summary><strong>See More</strong></summary>

**Popular Derivatives:**
Elementary OS, Zorin OS, Kali Linux, Parrot OS, MX Linux, antiX

**Ubuntu Flavors:**
Lubuntu, Kubuntu, Xubuntu, Ubuntu MATE, Ubuntu Budgie, Ubuntu Studio

**Specialized Distros:**
Raspbian, Linux Lite, Bodhi Linux, Q4OS, SparkyLinux, Peppermint OS

**Security & Rescue:**
BackBox, BlackArch, SystemRescue, GParted Live, Clonezilla Live, Tails

**Lightweight Options:**
Puppy Linux, TinyCore, AntiX, SliTaz, Porteus, Slax

**Others:**
Deepin, KDE neon, Proxmox VE, Turnkey Linux, Nitrux, Voyager Live
</details>

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Fedora/Red Hat-based</strong></summary>
This includes **Fedora**, **Red Hat Enterprise Linux (RHEL)**, **CentOS**, **AlmaLinux**, **Rocky Linux**, and other Red Hat derivatives.

<details>
<summary><strong>See More</strong></summary>

**Popular Derivatives:**
Oracle Linux, Scientific Linux, CloudLinux, ClearOS, Qubes OS, Nobara Project

**Enterprise Variants:**
Red Hat Enterprise Linux (RHEL), CentOS Stream, AlmaLinux, Rocky Linux, Oracle Linux

**Community & Specialized:**
Fedora Workstation, Fedora Server, Fedora Silverblue, Fedora CoreOS, Fedora IoT

**Security & Labs:**
Fedora Security Lab, Qubes OS, CentOS Atomic Host, Red Hat Atomic Host

**Lightweight Options:**
Fedora LXDE, Fedora XFCE, CentOS Minimal, Scientific Linux

**Cloud & Container:**
Fedora CoreOS, Red Hat CoreOS, CentOS Cloud, Amazon Linux, Photon OS

**Others:**
OpenMandriva, PCLinuxOS, Mageia, ROSA Linux, Unity Linux, Berry Linux
</details>

```bash
sudo dnf install python3 python3-venv python3-pip -y
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Arch Linux-based</strong></summary>
This includes **Arch Linux**, **Manjaro**, **EndeavourOS**, **ArcoLinux**, and other Arch derivatives.

<details>
<summary><strong>See More</strong></summary>

**Popular Derivatives:**
Manjaro, EndeavourOS, ArcoLinux, Garuda Linux, Artix Linux, Parabola GNU/Linux

**User-Friendly Variants:**
Manjaro KDE, Manjaro GNOME, Manjaro XFCE, EndeavourOS, Garuda Linux, CachyOS

**Minimal & Advanced:**
Arch Linux, Artix Linux (systemd-free), Hyperbola GNU/Linux, Obarun Linux

**Gaming & Performance:**
Garuda Linux, CachyOS, SteamOS 3.0, ChimeraOS, Drauger OS

**Security & Privacy:**
BlackArch Linux, ArchStrike, Pentoo (Arch-based), Parabola GNU/Linux

**Lightweight Options:**
ArchBang, Architect Linux, Archcraft, ArchLabs, Mabox Linux

**Specialized:**
RebornOS, Crystal Linux, XeroLinux, ArchEX, Bluestar Linux, Chakra Linux

**Others:**
Antergos (discontinued), Bridge Linux, CTKArch, LinHES, Archphile
</details>

```bash
sudo pacman -Syu python python-virtualenv python-pip
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>openSUSE-based</strong></summary>
This includes **openSUSE Leap**, **openSUSE Tumbleweed**, **SUSE Linux Enterprise**, and other SUSE derivatives.

<details>
<summary><strong>See More</strong></summary>

**Official Variants:**
openSUSE Leap, openSUSE Tumbleweed, openSUSE MicroOS, SUSE Linux Enterprise Server (SLES)

**Enterprise & Commercial:**
SUSE Linux Enterprise Desktop (SLED), SUSE Linux Enterprise Server (SLES), SUSE Manager

**Community Derivatives:**
GeckoLinux, Regata OS, ALT Linux (SUSE-compatible), Calculate Linux

**Specialized:**
openSUSE Kubic, SUSE CaaS Platform, SUSE Cloud Application Platform

**Desktop Environments:**
openSUSE KDE, openSUSE GNOME, openSUSE XFCE, openSUSE LXDE, openSUSE Cinnamon

**Rolling vs Stable:**
openSUSE Tumbleweed (rolling), openSUSE Leap (stable), openSUSE MicroOS (immutable)

**Others:**
SUSE Studio Express, openSUSE Education, openSUSE Medical, SUSE Linux Enterprise Real Time
</details>

```bash
sudo zypper install python3 python3-venv python3-pip
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>NixOS & Nix-based</strong></summary>
This includes **NixOS**, **NixOS unstable**, and systems using the **Nix package manager**.

<details>
<summary><strong>See More</strong></summary>

**Official Variants:**
NixOS Stable, NixOS Unstable, NixOS Small, NixOS Minimal

**Specialized Configurations:**
NixOS with GNOME, NixOS with KDE, NixOS with i3, NixOS with Sway

**Enterprise & Server:**
NixOS Server, NixOS Cloud, NixOS Docker, NixOS WSL

**Development Focused:**
NixOS with development tools, NixOS for DevOps, NixOS for containers

**Derivative Projects:**
Determinate Systems Nix Installer, Flox, DevOS, NixOS generators

**Package Manager on Other Systems:**
Nix on macOS, Nix on Ubuntu, Nix on other Linux distributions

**Others:**
NixOS Live, NixOS ISO, Home Manager, Nix Darwin, NixOps
</details>

```bash
nix-env -iA nixpkgs.python3 nixpkgs.python3Packages.pip
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or add to your `configuration.nix`:
```nix
environment.systemPackages = with pkgs; [
    python3
    python3Packages.pip
];
```
</details>

<details>
<summary><strong>Alpine Linux-based</strong></summary>
This includes **Alpine Linux**, **Postmarket OS**, and other Alpine derivatives.

<details>
<summary><strong>See More</strong></summary>

**Official Variants:**
Alpine Linux Standard, Alpine Linux Extended, Alpine Linux Virtual, Alpine Linux Mini Root

**Mobile & Embedded:**
postmarketOS, Alpine Linux for embedded systems, Alpine Linux for IoT

**Container & Cloud:**
Alpine Linux Docker images, Alpine Linux LXC, Alpine Linux for Kubernetes

**Security & Minimal:**
Alpine Linux Hardened, Alpine Linux Security, Alpine Linux Firewall

**Development:**
Alpine Linux Edge (development), Alpine Linux testing repositories

**Specialized Builds:**
Alpine Linux for Raspberry Pi, Alpine Linux for ARM, Alpine Linux for x86

**Community Projects:**
Adélie Linux (Alpine-based), Chimera Linux (partially Alpine-inspired)

**Others:**
Alpine Linux Live, Alpine Linux Netboot, Alpine Linux Diskless, Alpine Linux Encrypted
</details>

```bash
sudo apk update
sudo apk add python3 python3-dev py3-pip py3-virtualenv
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>CentOS/RHEL Legacy</strong></summary>
This includes **CentOS 7**, **Red Hat Enterprise Linux 7/8**, and other legacy Red Hat systems.

<details>
<summary><strong>See More</strong></summary>

**Legacy Enterprise:**
CentOS 7, CentOS 8 (EOL), Red Hat Enterprise Linux 7, Red Hat Enterprise Linux 8

**Community Rebuilds:**
CentOS Stream, Rocky Linux, AlmaLinux, CloudLinux OS, Scientific Linux (EOL)

**Oracle & Commercial:**
Oracle Linux 7/8, Oracle Linux Unbreakable, Amazon Linux 2

**Specialized Legacy:**
CentOS Atomic Host (EOL), Red Hat Atomic Host (EOL), CentOS Plus repository

**Community Variants:**
Scientific Linux (discontinued), Springdale Linux, White Box Enterprise Linux

**Container & Cloud Legacy:**
CentOS Docker images, CentOS Cloud images, CentOS Vagrant boxes

**Others:**
ClearOS, SME Server, NethServer, Elastix (EOL), PBX in a Flash
</details>

```bash
sudo yum install python3 python3-venv python3-pip -y
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Gentoo-based</strong></summary>
This includes **Gentoo Linux**, **Funtoo**, **Calculate Linux**, and other Gentoo derivatives.

<details>
<summary><strong>See More</strong></summary>

**Official Variants:**
Gentoo Linux, Gentoo Hardened, Gentoo Prefix, Gentoo Live

**Community Derivatives:**
Funtoo Linux, Calculate Linux, Sabayon Linux (discontinued), RedCore Linux

**Specialized Builds:**
Gentoo Hardened, Gentoo SELinux, Gentoo for embedded systems

**Gaming & Desktop:**
RedCore Linux, Sabayon Linux (EOL), Pentoo (security), SystemRescue

**Binary-based:**
Calculate Linux, Redcore Linux, Sabayon Linux (was binary-based)

**Security Focused:**
Gentoo Hardened, Pentoo Linux, Hardened Gentoo with Grsecurity

**Others:**
Chromium OS (Gentoo-based), Container Linux (CoreOS, Gentoo-based), Exherbo Linux
</details>

```bash
sudo emerge dev-lang/python
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Void Linux-based</strong></summary>
This includes **Void Linux** and its variants.

<details>
<summary><strong>See More</strong></summary>

**Official Variants:**
Void Linux (glibc), Void Linux (musl), Void Linux Live

**Desktop Environments:**
Void Linux XFCE, Void Linux with various WMs, Void Linux minimal

**Specialized:**
Void Linux musl (alternative libc), Void Linux for embedded systems

**Community Projects:**
Projects using Void as base, Void Linux derivatives (limited)

**Architecture Support:**
Void Linux x86_64, Void Linux i686, Void Linux ARM, Void Linux AArch64

**Others:**
Void Linux containers, Void Linux for servers, Void Linux runit-based
</details>

```bash
sudo xbps-install -S python3 python3-pip
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Slackware-based</strong></summary>
This includes **Slackware**, **Salix OS**, **Zenwalk**, and other Slackware derivatives.

<details>
<summary><strong>See More</strong></summary>

**Official Variants:**
Slackware Linux, Slackware64, Slackware Current, Slackware ARM

**Community Derivatives:**
Salix OS, Zenwalk Linux, Vector Linux (discontinued), Absolute Linux

**Simplified Variants:**
Salix OS (simple package management), Zenwalk (optimized), Slackel Linux

**Specialized:**
Austrumi Linux, Kongoni Linux, Wolvix (discontinued), Bluewhite64

**Legacy & Historical:**
SUSE Linux (originally Slackware-based), S.u.S.E. Linux, early distributions

**International:**
Plamo Linux (Japanese), Kondara MNU/Linux (Japanese, discontinued)

**Others:**
Slax (live distro), Porteus, Puppy Linux (some variants), Kate OS
</details>

```bash
# Install Python (usually pre-installed)
# For package management, use slackpkg or sbopkg
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Clear Linux</strong></summary>
This includes **Clear Linux OS** by Intel and its derivatives.

<details>
<summary><strong>See More</strong></summary>

**Official Variants:**
Clear Linux OS, Clear Linux for Cloud, Clear Linux for Containers

**Performance Optimized:**
Clear Linux with Intel optimizations, Clear Linux for machine learning

**Development:**
Clear Linux with development tools, Clear Linux for cloud-native development

**Specialized:**
Clear Linux for IoT, Clear Linux for edge computing, Clear Linux minimal

**Architecture:**
Clear Linux x86_64 (Intel optimized), Clear Linux for Intel hardware

**Others:**
Clear Linux live, Clear Linux installer, Clear Linux cloud images
</details>

```bash
sudo swupd bundle-add python3-basic dev-utils
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Solus</strong></summary>
This includes **Solus** and its editions.

<details>
<summary><strong>See More</strong></summary>

**Official Editions:**
Solus Budgie, Solus GNOME, Solus KDE Plasma, Solus MATE

**Desktop Focused:**
Solus (gaming optimized), Solus for developers, Solus multimedia

**Rolling Release:**
Solus rolling release model, Solus weekly snapshots

**Specialized:**
Solus for content creators, Solus for programming, Solus minimal

**Community:**
Solus community packages, Solus third-party software

**Others:**
Solus live ISO, Solus virtual machine images, Solus development builds
</details>

```bash
sudo eopkg install python3 python3-devel pip
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary><strong>Other Distros</strong></summary>

Refer to your distribution's documentation for installing Python 3 and pip, then run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

---

### Step 3: Setup MediGuard Backend

1. **Navigate to the project directory:**
   ```bash
   cd path/to/mediguard_backend
   ```

2. **Sync dependencies with UV:**
   ```bash
   uv sync
   ```

3. **Activate the virtual environment:**

   **Windows (PowerShell):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **Linux / macOS:**
   ```bash
   source .venv/bin/activate
   ```

---

### Step 4: Run the Django Server

Once the virtual environment is activated, run the server:

```bash
uv run manage.py runserver
```

**✅ Expected output:**
```
Django version X.X, using settings 'main_app.settings'
Starting development server at http://127.0.0.1:8000/
```

---

## ✅ Success!

🎉 **Congratulations!** You have successfully set up the MediGuard backend locally.

**👉 Open your browser and visit:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## ⚠️ Troubleshooting

### Common Issues & Solutions

**❌ `python not recognized` (Windows)**
- **Solution:** Try `py --version` instead. If it works, use `py` instead of `python`.

**❌ `uv not recognized`**
- **Solution:** Restart your terminal after installing UV, or add it to PATH manually.

**❌ `Port already in use` (when running server)**
- **Solution:** Stop the process using port 8000 or run Django on a different port:
  ```bash
  uv run manage.py runserver 5969
  ```

**❌ Virtual environment not activating**
<details>
<summary>See full solution</summary>

1. Run:
    ```bash
    uv venv
    ```
2. Then activate the virtual environment again:
    ```bash
    source .venv/bin/activate
    ```
</details>

**❌ Environment script commands not working (Linux/macOS)**
- **Solution:** Make sure you used `source ./venvshell` instead of `./venvshell`
- **Alternative:** Try `. ./venvshell` (note the dot and space before the script name)

**❌ Environment script not found**
- **Solution:** Make sure you're in the correct directory and the file exists:
  ```bash
  ls -la venvshell*
  ```

**❌ Permission denied (Linux/macOS)**
- **Solution:** Use `sudo` for system-wide installations or check file permissions.