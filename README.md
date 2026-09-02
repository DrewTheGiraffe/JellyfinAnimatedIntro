# Jellyfin Logo Intro Renderer

A cross-platform Python renderer for creating a polished three-second entrance animation from the Jellyfin logo.

The animation traces the Jellyfin symbol onto the canvas, sweeps the original gradient into place, and reveals the Jellyfin wordmark from left to right.

The renderer creates both:

* A **transparent ProRes 4444 master** for further processing or animated WebP conversion.
* A **standard H.264 MP4 preview** rendered over a black background.

* Add this one liner css to Jellyfin to use the default Jellyfin logo with subtle animation.
```css
.pageTitleWithDefaultLogo { background-image: url('https://raw.githubusercontent.com/DrewTheGiraffe/JellyfinAnimatedIntro/main/jellyfin_logo_intro_alpha.webp') !important; background-size: contain !important; background-repeat: no-repeat !important; background-position: left center !important; }
```
* When replacing the WebP later, Jellyfin or the browser may continue showing a cached copy. Change a version number at the end of the URL to force a refresh:
```css
.pageTitleWithDefaultLogo { background-image: url('https://raw.githubusercontent.com/DrewTheGiraffe/JellyfinAnimatedIntro/main/jellyfin_logo_intro_alpha.webp?v=2') !important; background-size: contain !important; background-repeat: no-repeat !important; background-position: left center !important; }
```

---

## Output Specifications

| Property                 | Value                |
| ------------------------ | -------------------- |
| Duration                 | 3 seconds            |
| Resolution               | 1004 × 288 pixels    |
| Frame rate               | 30 FPS               |
| Audio                    | None                 |
| Playback                 | One-shot entrance    |
| Transparent master       | ProRes 4444 MOV      |
| Standard preview         | H.264 MP4 over black |
| Animated delivery format | WebP                 |

The renderer creates:

```text
jellyfin_logo_intro_alpha.mov
jellyfin_logo_intro.mp4
```

The transparent MOV should be used when creating the animated WebP.

The MP4 is intended as a convenient preview and **does not contain transparency**.

---

## Project Structure

Keep the renderer and source logo together in the same project directory:

```text
jellyfin-logo-intro/
├── render_jellyfin_intro.py
└── jellyfin_logo.png
```

The recommended source image is:

```text
1004 × 288 PNG
```

A PNG using the same aspect ratio may also be used. The renderer will resize it automatically.

---

## Requirements

| Software           | Requirement                                     |
| ------------------ | ----------------------------------------------- |
| Python             | 3.10 or newer                                   |
| Recommended Python | Python 3.13                                     |
| NumPy              | `>=2.2,<3`                                      |
| Pillow             | `>=12,<13`                                      |
| FFmpeg             | Full build containing `prores_ks` and `libx264` |
| WebP support       | FFmpeg containing `libwebp_anim`                |

The setup instructions create a local Python virtual environment named:

```text
.venv
```

Python dependencies are therefore isolated from the system-wide Python installation.

FFmpeg may simply be installed on the system and available through `PATH`. The Python renderer does not require a hardcoded FFmpeg executable path.

---

# Quick Start

Once the prerequisites are installed, rendering requires only the following command.

### Windows

```powershell
.\.venv\Scripts\python.exe .\render_jellyfin_intro.py .\jellyfin_logo.png --output-directory .\output
```

### macOS / Linux

```bash
.venv/bin/python render_jellyfin_intro.py jellyfin_logo.png --output-directory output
```

The output directory will contain:

```text
output/
├── jellyfin_logo_intro_alpha.mov
└── jellyfin_logo_intro.mp4
```

You can then convert the transparent MOV to animated WebP using the commands later in this README.

---

# Windows

Use **PowerShell**.

## Install Everything

Change the project directory below to the folder containing:

```text
render_jellyfin_intro.py
jellyfin_logo.png
```

Then paste the entire block into PowerShell.

```powershell
$ErrorActionPreference = "Stop"

# Change this to your project folder.
Set-Location "C:\path\to\jellyfin-logo-intro"

# Install Python 3.13.
winget install `
    --exact `
    --id Python.Python.3.13 `
    --source winget `
    --accept-source-agreements `
    --accept-package-agreements

# Install a full FFmpeg build.
winget install `
    --exact `
    --id Gyan.FFmpeg `
    --source winget `
    --accept-source-agreements `
    --accept-package-agreements

# Reload the machine and user PATH into this PowerShell session.
$env:Path = `
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
    [Environment]::GetEnvironmentVariable("Path", "User")

# Verify that the renderer exists.
if (-not (Test-Path ".\render_jellyfin_intro.py")) {
    throw "render_jellyfin_intro.py was not found in the current folder."
}

# Verify that the source logo exists.
if (-not (Test-Path ".\jellyfin_logo.png")) {
    throw "jellyfin_logo.png was not found in the current folder."
}

# Create a private Python virtual environment.
py -3.13 -m venv .venv

# Upgrade pip.
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# Install Python dependencies.
.\.venv\Scripts\python.exe -m pip install `
    "numpy>=2.2,<3" `
    "Pillow>=12,<13"

# Verify Python and package versions.
.\.venv\Scripts\python.exe -c "import sys, numpy, PIL; print(f'Python {sys.version.split()[0]} | NumPy {numpy.__version__} | Pillow {PIL.__version__}')"

# Verify FFmpeg.
ffmpeg -version | Select-Object -First 1

# Read the available FFmpeg encoders.
$encoders = ffmpeg -hide_banner -encoders 2>&1 | Out-String

# Verify the encoders required by this project.
foreach ($encoder in @("prores_ks", "libx264", "libwebp_anim")) {
    if ($encoders -notmatch [regex]::Escape($encoder)) {
        throw "The installed FFmpeg build does not contain the '$encoder' encoder."
    }
}

Write-Host "`nSetup completed successfully." -ForegroundColor Green
```

---

## Render on Windows

From the project directory, run:

```powershell
.\.venv\Scripts\python.exe `
    .\render_jellyfin_intro.py `
    .\jellyfin_logo.png `
    --output-directory .\output
```

The completed videos will be written to:

```text
output\jellyfin_logo_intro_alpha.mov
output\jellyfin_logo_intro.mp4
```

---

## Convert to Animated WebP on Windows

The transparent ProRes MOV should be used as the input.

### Lossless WebP

This creates a high-fidelity lossless animated WebP with transparency:

```powershell
ffmpeg -y `
    -i ".\output\jellyfin_logo_intro_alpha.mov" `
    -vf "fps=30,format=bgra" `
    -c:v libwebp_anim `
    -lossless 1 `
    -compression_level 6 `
    -loop 1 `
    -an `
    ".\output\jellyfin_logo_intro.webp"
```

### Smaller WebP

For websites where file size matters more than completely lossless compression:

```powershell
ffmpeg -y `
    -i ".\output\jellyfin_logo_intro_alpha.mov" `
    -vf "fps=30,format=bgra" `
    -c:v libwebp_anim `
    -lossless 0 `
    -q:v 85 `
    -compression_level 6 `
    -loop 1 `
    -an `
    ".\output\jellyfin_logo_intro.webp"
```

Display the generated files:

```powershell
Get-ChildItem ".\output\jellyfin_logo_intro*" |
    Select-Object Name, Length, LastWriteTime
```

---

# macOS

Use **Terminal**.

The following setup automatically installs Homebrew when it is not already installed.

The Homebrew installer may request the local Mac account password.

## Install Everything

Change the first path to your project directory and paste the entire block into Terminal.

```bash
set -e

# Change this to your project folder.
cd "/path/to/jellyfin-logo-intro"

# Install Homebrew when it is not already installed.
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Locate Homebrew.
if [ -x /opt/homebrew/bin/brew ]; then
  BREW="/opt/homebrew/bin/brew"
elif [ -x /usr/local/bin/brew ]; then
  BREW="/usr/local/bin/brew"
else
  echo "Homebrew could not be found after installation." >&2
  exit 1
fi

# Make Homebrew available in the current terminal.
eval "$("$BREW" shellenv)"

# Determine the appropriate shell profile.
case "${SHELL:-}" in
  */zsh)
    PROFILE="$HOME/.zprofile"
    ;;
  *)
    PROFILE="$HOME/.bash_profile"
    ;;
esac

touch "$PROFILE"

# Make Homebrew available automatically in future terminal sessions.
BREW_LINE="eval \"\$($BREW shellenv)\""

grep -Fqx "$BREW_LINE" "$PROFILE" 2>/dev/null ||
  printf '%s\n' "$BREW_LINE" >> "$PROFILE"

# Install Python 3.13 and a full FFmpeg build.
"$BREW" install python@3.13 ffmpeg-full

# Put ffmpeg-full first on PATH.
FFMPEG_BIN="$("$BREW" --prefix ffmpeg-full)/bin"
export PATH="$FFMPEG_BIN:$PATH"

# Save the FFmpeg PATH configuration.
FFMPEG_LINE="export PATH=\"$FFMPEG_BIN:\$PATH\""

grep -Fqx "$FFMPEG_LINE" "$PROFILE" 2>/dev/null ||
  printf '%s\n' "$FFMPEG_LINE" >> "$PROFILE"

# Verify project files.
test -f "render_jellyfin_intro.py" || {
  echo "render_jellyfin_intro.py was not found in the current folder." >&2
  exit 1
}

test -f "jellyfin_logo.png" || {
  echo "jellyfin_logo.png was not found in the current folder." >&2
  exit 1
}

# Locate the Homebrew Python 3.13 executable.
PYTHON="$("$BREW" --prefix python@3.13)/bin/python3.13"

# Create the virtual environment.
"$PYTHON" -m venv .venv

# Install Python dependencies.
.venv/bin/python -m pip install --upgrade pip

.venv/bin/python -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"

# Verify Python and installed dependencies.
.venv/bin/python -c \
  'import sys, numpy, PIL; print(f"Python {sys.version.split()[0]} | NumPy {numpy.__version__} | Pillow {PIL.__version__}")'

# Verify FFmpeg.
ffmpeg -version | head -n 1

# Verify required FFmpeg encoders.
ENCODERS="$(ffmpeg -hide_banner -encoders 2>&1)"

for ENCODER in prores_ks libx264 libwebp_anim; do
  printf '%s\n' "$ENCODERS" | grep -q "$ENCODER" || {
    echo "The installed FFmpeg build does not contain the '$ENCODER' encoder." >&2
    exit 1
  }
done

printf '\nSetup completed successfully.\n'
```

---

## Render on macOS

```bash
.venv/bin/python \
  render_jellyfin_intro.py \
  jellyfin_logo.png \
  --output-directory output
```

---

## Convert to Animated WebP on macOS

### Lossless

```bash
ffmpeg -y \
  -i "output/jellyfin_logo_intro_alpha.mov" \
  -vf "fps=30,format=bgra" \
  -c:v libwebp_anim \
  -lossless 1 \
  -compression_level 6 \
  -loop 1 \
  -an \
  "output/jellyfin_logo_intro.webp"
```

### Smaller High-Quality Version

```bash
ffmpeg -y \
  -i "output/jellyfin_logo_intro_alpha.mov" \
  -vf "fps=30,format=bgra" \
  -c:v libwebp_anim \
  -lossless 0 \
  -q:v 85 \
  -compression_level 6 \
  -loop 1 \
  -an \
  "output/jellyfin_logo_intro.webp"
```

Display the generated files:

```bash
ls -lh output/jellyfin_logo_intro*
```

---

# Linux

Python 3.10 or newer is required.

The installation commands below verify the installed Python version before creating the virtual environment.

Choose the section for your Linux distribution.

---

## Ubuntu / Linux Mint

```bash
set -e

# Change this to your project folder.
cd "/path/to/jellyfin-logo-intro"

# Update package information.
sudo apt-get update

# Install repository management tools.
sudo apt-get install -y software-properties-common

# Enable Ubuntu Universe.
sudo add-apt-repository -y universe

# Refresh repository information.
sudo apt-get update

# Install Python and FFmpeg.
sudo apt-get install -y \
  python3 \
  python3-venv \
  python3-pip \
  ffmpeg

# Require Python 3.10 or newer.
python3 -c \
  'import sys; assert sys.version_info >= (3, 10), "Python 3.10 or newer is required."; print(sys.version)'

# Verify project files.
test -f "render_jellyfin_intro.py" || {
  echo "render_jellyfin_intro.py was not found in the current folder." >&2
  exit 1
}

test -f "jellyfin_logo.png" || {
  echo "jellyfin_logo.png was not found in the current folder." >&2
  exit 1
}

# Create the virtual environment.
python3 -m venv .venv

# Install dependencies.
.venv/bin/python -m pip install --upgrade pip

.venv/bin/python -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"

# Verify Python and package versions.
.venv/bin/python -c \
  'import sys, numpy, PIL; print(f"Python {sys.version.split()[0]} | NumPy {numpy.__version__} | Pillow {PIL.__version__}")'

# Verify FFmpeg.
ffmpeg -version | head -n 1

# Verify required encoders.
ENCODERS="$(ffmpeg -hide_banner -encoders 2>&1)"

for ENCODER in prores_ks libx264 libwebp_anim; do
  printf '%s\n' "$ENCODERS" | grep -q "$ENCODER" || {
    echo "The installed FFmpeg build does not contain the '$ENCODER' encoder." >&2
    exit 1
  }
done

printf '\nSetup completed successfully.\n'
```

---

## Debian

```bash
set -e

# Change this to your project folder.
cd "/path/to/jellyfin-logo-intro"

# Install Python and FFmpeg.
sudo apt-get update

sudo apt-get install -y \
  python3 \
  python3-venv \
  python3-pip \
  ffmpeg

# Require Python 3.10 or newer.
python3 -c \
  'import sys; assert sys.version_info >= (3, 10), "Python 3.10 or newer is required."; print(sys.version)'

# Verify project files.
test -f "render_jellyfin_intro.py" || {
  echo "render_jellyfin_intro.py was not found in the current folder." >&2
  exit 1
}

test -f "jellyfin_logo.png" || {
  echo "jellyfin_logo.png was not found in the current folder." >&2
  exit 1
}

# Create the virtual environment.
python3 -m venv .venv

# Install dependencies.
.venv/bin/python -m pip install --upgrade pip

.venv/bin/python -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"

# Verify Python and package versions.
.venv/bin/python -c \
  'import sys, numpy, PIL; print(f"Python {sys.version.split()[0]} | NumPy {numpy.__version__} | Pillow {PIL.__version__}")'

# Verify FFmpeg.
ffmpeg -version | head -n 1

# Verify required encoders.
ENCODERS="$(ffmpeg -hide_banner -encoders 2>&1)"

for ENCODER in prores_ks libx264 libwebp_anim; do
  printf '%s\n' "$ENCODERS" | grep -q "$ENCODER" || {
    echo "The installed FFmpeg build does not contain the '$ENCODER' encoder." >&2
    exit 1
  }
done

printf '\nSetup completed successfully.\n'
```

---

## Fedora

Fedora's standard `ffmpeg-free` package may not contain everything required for the H.264 preview.

The following commands enable **RPM Fusion Free** and install its full FFmpeg package.

```bash
set -e

# Change this to your project folder.
cd "/path/to/jellyfin-logo-intro"

# Install Python.
sudo dnf install -y \
  python3 \
  python3-pip

# Enable RPM Fusion Free.
sudo dnf install -y \
  "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm"

# Replace Fedora's limited FFmpeg package when installed.
if rpm -q ffmpeg-free >/dev/null 2>&1; then
  sudo dnf swap -y ffmpeg-free ffmpeg --allowerasing
else
  sudo dnf install -y ffmpeg --allowerasing
fi

# Require Python 3.10 or newer.
python3 -c \
  'import sys; assert sys.version_info >= (3, 10), "Python 3.10 or newer is required."; print(sys.version)'

# Verify project files.
test -f "render_jellyfin_intro.py" || {
  echo "render_jellyfin_intro.py was not found in the current folder." >&2
  exit 1
}

test -f "jellyfin_logo.png" || {
  echo "jellyfin_logo.png was not found in the current folder." >&2
  exit 1
}

# Create the virtual environment.
python3 -m venv .venv

# Install dependencies.
.venv/bin/python -m pip install --upgrade pip

.venv/bin/python -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"

# Verify Python and installed dependencies.
.venv/bin/python -c \
  'import sys, numpy, PIL; print(f"Python {sys.version.split()[0]} | NumPy {numpy.__version__} | Pillow {PIL.__version__}")'

# Verify FFmpeg.
ffmpeg -version | head -n 1

# Verify required encoders.
ENCODERS="$(ffmpeg -hide_banner -encoders 2>&1)"

for ENCODER in prores_ks libx264 libwebp_anim; do
  printf '%s\n' "$ENCODERS" | grep -q "$ENCODER" || {
    echo "The installed FFmpeg build does not contain the '$ENCODER' encoder." >&2
    exit 1
  }
done

printf '\nSetup completed successfully.\n'
```

---

## Arch Linux / Manjaro

```bash
set -e

# Change this to your project folder.
cd "/path/to/jellyfin-logo-intro"

# Install Python and FFmpeg.
sudo pacman -Syu --needed \
  python \
  python-pip \
  ffmpeg

# Require Python 3.10 or newer.
python -c \
  'import sys; assert sys.version_info >= (3, 10), "Python 3.10 or newer is required."; print(sys.version)'

# Verify project files.
test -f "render_jellyfin_intro.py" || {
  echo "render_jellyfin_intro.py was not found in the current folder." >&2
  exit 1
}

test -f "jellyfin_logo.png" || {
  echo "jellyfin_logo.png was not found in the current folder." >&2
  exit 1
}

# Create the virtual environment.
python -m venv .venv

# Install dependencies.
.venv/bin/python -m pip install --upgrade pip

.venv/bin/python -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"

# Verify Python and installed dependencies.
.venv/bin/python -c \
  'import sys, numpy, PIL; print(f"Python {sys.version.split()[0]} | NumPy {numpy.__version__} | Pillow {PIL.__version__}")'

# Verify FFmpeg.
ffmpeg -version | head -n 1

# Verify required encoders.
ENCODERS="$(ffmpeg -hide_banner -encoders 2>&1)"

for ENCODER in prores_ks libx264 libwebp_anim; do
  printf '%s\n' "$ENCODERS" | grep -q "$ENCODER" || {
    echo "The installed FFmpeg build does not contain the '$ENCODER' encoder." >&2
    exit 1
  }
done

printf '\nSetup completed successfully.\n'
```

---

# Render on Linux

After completing the setup for your distribution:

```bash
.venv/bin/python \
  render_jellyfin_intro.py \
  jellyfin_logo.png \
  --output-directory output
```

---

# Convert to Animated WebP on Linux

## Lossless

```bash
ffmpeg -y \
  -i "output/jellyfin_logo_intro_alpha.mov" \
  -vf "fps=30,format=bgra" \
  -c:v libwebp_anim \
  -lossless 1 \
  -compression_level 6 \
  -loop 1 \
  -an \
  "output/jellyfin_logo_intro.webp"
```

## Smaller High-Quality Version

```bash
ffmpeg -y \
  -i "output/jellyfin_logo_intro_alpha.mov" \
  -vf "fps=30,format=bgra" \
  -c:v libwebp_anim \
  -lossless 0 \
  -q:v 85 \
  -compression_level 6 \
  -loop 1 \
  -an \
  "output/jellyfin_logo_intro.webp"
```

Display the generated files:

```bash
ls -lh output/jellyfin_logo_intro*
```

---

# WebP Loop Behavior

The WebP commands use:

```text
-loop 1
```

This produces finite playback rather than continuously looping forever.

A value of:

```text
-loop 0
```

is reserved for infinite looping.

For this project, `-loop 1` is used because the logo animation is designed as a **one-shot entrance**.

---

# Verify Your Installation

These commands can be useful when diagnosing setup problems.

---

## Windows

### Locate Python and FFmpeg

```powershell
Get-Command py
Get-Command ffmpeg
```

### Check Installed Python Packages

```powershell
.\.venv\Scripts\python.exe -m pip show numpy Pillow
```

### Check Required FFmpeg Encoders

```powershell
ffmpeg -hide_banner -encoders 2>&1 |
    Select-String "prores_ks|libx264|libwebp_anim"
```

Expected encoder names include:

```text
prores_ks
libx264
libwebp_anim
```

### Show Renderer Help

```powershell
.\.venv\Scripts\python.exe .\render_jellyfin_intro.py --help
```

---

## macOS / Linux

### Locate Python and FFmpeg

```bash
command -v python3 || command -v python
command -v ffmpeg
```

### Check Installed Python Packages

```bash
.venv/bin/python -m pip show numpy Pillow
```

### Check Required FFmpeg Encoders

```bash
ffmpeg -hide_banner -encoders 2>&1 |
  grep -E "prores_ks|libx264|libwebp_anim"
```

Expected encoder names include:

```text
prores_ks
libx264
libwebp_anim
```

### Show Renderer Help

```bash
.venv/bin/python render_jellyfin_intro.py --help
```

---

# Rebuild the Python Environment

If the `.venv` directory becomes damaged, dependencies become corrupted, or you simply want a clean Python environment, delete it and recreate it.

---

## Windows PowerShell

```powershell
Remove-Item `
    -Recurse `
    -Force `
    .\.venv `
    -ErrorAction SilentlyContinue

py -3.13 -m venv .venv

.\.venv\Scripts\python.exe -m pip install --upgrade pip

.\.venv\Scripts\python.exe -m pip install `
    "numpy>=2.2,<3" `
    "Pillow>=12,<13"
```

---

## macOS

Using the Homebrew Python installed by the setup instructions:

```bash
rm -rf .venv

"$(brew --prefix python@3.13)/bin/python3.13" \
  -m venv .venv

.venv/bin/python \
  -m pip install --upgrade pip

.venv/bin/python \
  -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"
```

---

## Linux

```bash
rm -rf .venv

python3 -m venv .venv

.venv/bin/python \
  -m pip install --upgrade pip

.venv/bin/python \
  -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"
```

---

# Expected Final Output

After rendering the animation and converting the transparent MOV to WebP, the project should contain:

```text
jellyfin-logo-intro/
├── render_jellyfin_intro.py
├── jellyfin_logo.png
├── .venv/
└── output/
    ├── jellyfin_logo_intro_alpha.mov
    ├── jellyfin_logo_intro.mp4
    └── jellyfin_logo_intro.webp
```

---

## Transparent Editing Master

Use:

```text
output/jellyfin_logo_intro_alpha.mov
```

for:

* Animated WebP conversion
* Further editing
* Compositing
* Transparent-background workflows
* Archival master output

The file uses **ProRes 4444** so the alpha channel can be retained.

---

## Standard Preview

Use:

```text
output/jellyfin_logo_intro.mp4
```

for:

* Easy local playback
* Sharing a preview
* Browser-compatible testing
* Reviewing animation timing

The MP4 uses H.264 and is rendered over a black background.

It does **not** contain transparency.

---

## Web Delivery

Use:

```text
output/jellyfin_logo_intro.webp
```

for:

* Websites
* Web applications
* Animated logo entrances
* Transparent browser-based presentation

For maximum image fidelity, use the lossless WebP command.

For a smaller website asset, use:

```text
-lossless 0
-q:v 85
-compression_level 6
```

---

# FFmpeg Encoder Requirements

The renderer and conversion workflow rely on three primary FFmpeg encoders.

## `prores_ks`

Used for:

```text
jellyfin_logo_intro_alpha.mov
```

This provides the transparent ProRes 4444 master.

---

## `libx264`

Used for:

```text
jellyfin_logo_intro.mp4
```

This produces the standard H.264 preview.

---

## `libwebp_anim`

Used when converting the transparent MOV into:

```text
jellyfin_logo_intro.webp
```

This encoder provides animated WebP output.

You can verify all three at once.

### Windows

```powershell
ffmpeg -hide_banner -encoders 2>&1 |
    Select-String "prores_ks|libx264|libwebp_anim"
```

### macOS / Linux

```bash
ffmpeg -hide_banner -encoders 2>&1 |
  grep -E "prores_ks|libx264|libwebp_anim"
```

---

# Troubleshooting

## `ffmpeg` Is Not Recognized

### Windows

Reload the system and user `PATH`:

```powershell
$env:Path = `
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
    [Environment]::GetEnvironmentVariable("Path", "User")
```

Then test:

```powershell
ffmpeg -version
```

If necessary, close PowerShell, open a new PowerShell window, and run:

```powershell
ffmpeg -version
```

---

## Python Is Not Recognized on Windows

Test the Python launcher:

```powershell
py --version
```

Test Python 3.13 specifically:

```powershell
py -3.13 --version
```

If Python 3.13 is not installed:

```powershell
winget install `
    --exact `
    --id Python.Python.3.13 `
    --source winget `
    --accept-source-agreements `
    --accept-package-agreements
```

---

## Virtual Environment Is Missing

### Windows

```powershell
py -3.13 -m venv .venv
```

### macOS

```bash
"$(brew --prefix python@3.13)/bin/python3.13" \
  -m venv .venv
```

### Linux

```bash
python3 -m venv .venv
```

---

## NumPy or Pillow Is Missing

### Windows

```powershell
.\.venv\Scripts\python.exe -m pip install `
    "numpy>=2.2,<3" `
    "Pillow>=12,<13"
```

### macOS / Linux

```bash
.venv/bin/python -m pip install \
  "numpy>=2.2,<3" \
  "Pillow>=12,<13"
```

---

## Required FFmpeg Encoder Is Missing

Check the installed encoders:

### Windows

```powershell
ffmpeg -hide_banner -encoders 2>&1 |
    Select-String "prores_ks|libx264|libwebp_anim"
```

### macOS / Linux

```bash
ffmpeg -hide_banner -encoders 2>&1 |
  grep -E "prores_ks|libx264|libwebp_anim"
```

If one of the following is missing:

```text
prores_ks
libx264
libwebp_anim
```

install a fuller FFmpeg distribution using the platform-specific setup instructions above.

---

## Source Logo Cannot Be Found

Confirm the expected project structure:

```text
jellyfin-logo-intro/
├── render_jellyfin_intro.py
└── jellyfin_logo.png
```

### Windows

```powershell
Get-ChildItem
```

### macOS / Linux

```bash
ls -la
```

The default render commands expect the source file to be named:

```text
jellyfin_logo.png
```

---

## Output Directory Does Not Exist

The renderer should create the requested output directory as part of its normal workflow.

Use:

```text
--output-directory output
```

For example:

### Windows

```powershell
.\.venv\Scripts\python.exe `
    .\render_jellyfin_intro.py `
    .\jellyfin_logo.png `
    --output-directory .\output
```

### macOS / Linux

```bash
.venv/bin/python \
  render_jellyfin_intro.py \
  jellyfin_logo.png \
  --output-directory output
```

---

# Complete Workflow

The complete process is:

```text
jellyfin_logo.png
        │
        ▼
render_jellyfin_intro.py
        │
        ├──────────────► jellyfin_logo_intro.mp4
        │                H.264 preview
        │                black background
        │
        ▼
jellyfin_logo_intro_alpha.mov
ProRes 4444
transparent master
        │
        ▼
FFmpeg libwebp_anim
        │
        ▼
jellyfin_logo_intro.webp
transparent animated WebP
```

---

# Recommended Workflow

For normal use:

1. Keep `render_jellyfin_intro.py` and `jellyfin_logo.png` in the same project folder.
2. Install Python and FFmpeg using the setup instructions for your operating system.
3. Create the `.venv` environment.
4. Install NumPy and Pillow.
5. Verify the required FFmpeg encoders.
6. Run the renderer.
7. Preview `jellyfin_logo_intro.mp4`.
8. Convert `jellyfin_logo_intro_alpha.mov` to WebP.
9. Use `jellyfin_logo_intro.webp` for website delivery.

For maximum-quality WebP output, use:

```text
-lossless 1
```

For a smaller high-quality WebP, use:

```text
-lossless 0
-q:v 85
-compression_level 6
```

---

# License

Add the appropriate license for your project here.

If this repository contains Jellyfin trademarks, branding, or other upstream assets, make sure your usage complies with the applicable Jellyfin trademark and licensing requirements.
