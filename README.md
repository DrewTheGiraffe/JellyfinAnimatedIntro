# Jellyfin Logo Intro Renderer

This script creates a short, professional entrance animation for the Jellyfin logo.

The animation traces the Jellyfin symbol, sweeps the original gradient through it, and then reveals the Jellyfin wordmark. It produces both a transparent master file and a standard MP4 preview.

## Animation specifications

| Property | Specification |
|---|---|
| Duration | 3 seconds |
| Canvas size | 1004 × 288 pixels |
| Frame rate | 30 frames per second |
| Total frames | 90 |
| Audio | None |
| Playback style | One-shot entrance |
| Transparent output | ProRes 4444 MOV |
| Preview output | H.264 MP4 on black |
| Intended source format | PNG |

## Files created

The script creates two video files:

### `jellyfin_logo_intro_alpha.mov`

This is the transparent master.

It uses Apple ProRes 4444 and retains the transparent background. Use this file when creating an animated WebP or when importing the animation into editing or compositing software.

Some video players display transparency as black. That does not necessarily mean the transparency has been removed.

### `jellyfin_logo_intro.mp4`

This is a standard H.264 preview with the animation placed over a black background.

It is useful for checking the animation in an ordinary media player. This MP4 does not contain transparency.

## Requirements

For the simplest setup, use the following:

| Software | Supported setup |
|---|---|
| Operating system | Windows, macOS, or Linux |
| Python | Python 3.10 or later |
| Recommended Python | Python 3.12, 3.13, or 3.14 |
| NumPy | Version 2.1 or later, below 3.0 |
| Pillow | Version 12 or later, below 13.0 |
| FFmpeg | A recent full build with `prores_ks` and `libx264` |

Use a stable, 64-bit version of Python rather than a beta or preview release.

Python 3.10 and 3.11 can run the script, but `pip` may install an older compatible version of NumPy automatically. Python 3.12 or later provides the most straightforward installation.

### What each dependency does

- **Python** runs the animation script.
- **NumPy** processes the image and animation data.
- **Pillow** reads the logo and creates the individual animation frames.
- **FFmpeg** combines the frames into the MOV and MP4 video files.

FFmpeg is a separate desktop command-line program. Installing a Python package named `ffmpeg` does not install the FFmpeg application required by this script.

---

# Installation

## 1. Create a project folder

Create a folder for the renderer and place these files inside it:

```text
jellyfin-logo-intro/
├── render_jellyfin_intro.py
├── jellyfin_logo.png
└── README.md
```

The logo can have another filename, but the examples in this guide use:

```text
jellyfin_logo.png
```

---

## 2. Install Python

### Windows

1. Open the official [Python download page](https://www.python.org/downloads/).
2. Download a stable 64-bit Python release. Python 3.12, 3.13, or 3.14 is recommended.
3. Run the installer.
4. Enable the option that adds Python to `PATH`, when that option is shown.
5. Complete the installation.
6. Close and reopen Command Prompt or PowerShell.

Check the installation with:

```powershell
py --version
```

A result similar to the following confirms that Python is available:

```text
Python 3.13.7
```

The exact version number may be different.

When the `py` command is unavailable, try:

```powershell
python --version
```

### macOS

Python can be installed from the official [Python download page](https://www.python.org/downloads/) or through Homebrew.

Using the official installer:

1. Download a stable macOS installer.
2. Open the downloaded package.
3. Follow the installation prompts.
4. Close and reopen Terminal.

Check the installation with:

```bash
python3 --version
```

Using Homebrew instead:

```bash
brew install python
```

Then check the installation:

```bash
python3 --version
```

### Linux

Many Linux distributions already include Python. Check the installed version first:

```bash
python3 --version
```

A version of Python 3.10 or later is required. Python 3.12 or later is recommended.

#### Ubuntu or Debian

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Fedora

```bash
sudo dnf install python3 python3-pip
```

#### Arch Linux or Manjaro

```bash
sudo pacman -S python python-pip
```

Do not replace or remove the operating system's built-in Python installation. Install an additional supported Python version when the system version is too old.

---

## 3. Install FFmpeg

FFmpeg can be installed anywhere, provided the folder containing the FFmpeg executable is included in the system `PATH`.

The script searches for the command named `ffmpeg` automatically. A direct file reference is not required.

After installation, this command must work:

```text
ffmpeg -version
```

### Windows — recommended Winget installation

On current versions of Windows 10 and Windows 11, FFmpeg can be installed from Command Prompt or PowerShell with Winget:

```powershell
winget install --id Gyan.FFmpeg -e
```

This installs the full Gyan FFmpeg build.

After the installation:

1. Close Command Prompt, PowerShell, and any open code editors.
2. Open a new Command Prompt or PowerShell window.
3. Run:

```powershell
ffmpeg -version
```

When version information appears, FFmpeg is ready.

#### When Winget is unavailable

Winget is normally supplied through Microsoft App Installer on current Windows installations. A manual FFmpeg installation can be used instead.

### Windows — manual installation

1. Open the official [FFmpeg download page](https://ffmpeg.org/download.html).
2. Select the Windows builds link for [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
3. Download the **release full** ZIP build.
4. Create this folder:

```text
C:\Tools\ffmpeg
```

5. Extract or move the downloaded files so the executable is located here:

```text
C:\Tools\ffmpeg\bin\ffmpeg.exe
```

The important part is that the final folder contains:

```text
C:\Tools\ffmpeg\bin\ffmpeg.exe
C:\Tools\ffmpeg\bin\ffprobe.exe
C:\Tools\ffmpeg\bin\ffplay.exe
```

#### Add FFmpeg to the Windows PATH

1. Open the Windows Start menu.
2. Search for **environment variables**.
3. Open **Edit environment variables for your account**.
4. Select the variable named **Path**.
5. Select **Edit**.
6. Select **New**.
7. Enter:

```text
C:\Tools\ffmpeg\bin
```

8. Confirm each window with **OK**.
9. Close and reopen Command Prompt or PowerShell.
10. Test the installation:

```powershell
ffmpeg -version
```

Add the folder containing `ffmpeg.exe` to `PATH`, not the path to the `.exe` file itself.

### macOS — recommended Homebrew installation

Homebrew provides the easiest FFmpeg installation on macOS.

Install Homebrew from its official website when it is not already installed:

[https://brew.sh/](https://brew.sh/)

After Homebrew is installed, run:

```bash
brew install ffmpeg
```

Homebrew manages the installation location and normally makes FFmpeg available on `PATH` automatically.

Check the installation:

```bash
ffmpeg -version
```

Homebrew may display additional shell setup commands after its own installation. Run those commands when prompted before installing FFmpeg.

The current Homebrew package information is available at:

[Homebrew FFmpeg formula](https://formulae.brew.sh/formula/ffmpeg)

### Linux

Linux package managers normally install FFmpeg into a standard location such as `/usr/bin/ffmpeg`, which is already on `PATH`.

#### Ubuntu or Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

#### Arch Linux or Manjaro

```bash
sudo pacman -S ffmpeg
```

#### Fedora

The standard Fedora `ffmpeg-free` package may not contain the H.264 `libx264` encoder required for the MP4 preview.

For the complete FFmpeg package:

1. Configure RPM Fusion using its official instructions:

   [RPM Fusion configuration](https://rpmfusion.org/Configuration)

2. When `ffmpeg-free` is already installed, replace it with the complete package:

```bash
sudo dnf swap ffmpeg-free ffmpeg --allowerasing
```

When `ffmpeg-free` is not installed, use:

```bash
sudo dnf install ffmpeg --allowerasing
```

RPM Fusion also provides current multimedia guidance here:

[RPM Fusion multimedia guide](https://rpmfusion.org/Howto/Multimedia)

#### Other Linux distributions

Use the distribution's normal package manager or select a Linux package from the official [FFmpeg download page](https://ffmpeg.org/download.html).

---

## 4. Check the required FFmpeg encoders

The renderer requires these FFmpeg encoders:

- `prores_ks` for the transparent ProRes 4444 MOV
- `libx264` for the H.264 MP4 preview

The optional WebP conversion also uses:

- `libwebp_anim`

### Windows

Run:

```powershell
ffmpeg -hide_banner -encoders | findstr /I "prores_ks libx264 libwebp_anim"
```

### macOS or Linux

Run:

```bash
ffmpeg -hide_banner -encoders | grep -E "prores_ks|libx264|libwebp_anim"
```

At minimum, `prores_ks` and `libx264` should appear in the results.

`libwebp_anim` is only required when using the WebP conversion command later in this guide.

When an encoder is missing, install a complete or full FFmpeg build rather than a minimal build.

---

# Project setup

## 5. Open a terminal in the project folder

Open Command Prompt, PowerShell, or Terminal and change to the folder containing the script.

### Windows example

```powershell
cd "C:\Users\YourName\Desktop\jellyfin-logo-intro"
```

### macOS example

```bash
cd "/Users/YourName/Desktop/jellyfin-logo-intro"
```

### Linux example

```bash
cd "/home/YourName/jellyfin-logo-intro"
```

Use quotation marks when a folder or filename contains spaces.

---

## 6. Create a Python virtual environment

A virtual environment keeps the required Python packages inside the project folder instead of installing them across the whole computer.

This step is recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, the terminal usually displays `(.venv)` at the start of the command line.

Example:

```text
(.venv) C:\Users\YourName\Desktop\jellyfin-logo-intro>
```

---

## 7. Install the Python dependencies

With the virtual environment active, upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install NumPy and Pillow:

```bash
python -m pip install "numpy>=2.1,<3" "Pillow>=12,<13"
```

No other Python packages are required.

### Optional `requirements.txt`

For a reusable project setup, create a file named `requirements.txt` containing:

```text
numpy>=2.1,<3
Pillow>=12,<13
```

The dependencies can then be installed with:

```bash
python -m pip install -r requirements.txt
```

### Confirm the packages are installed

Run:

```bash
python -c "import numpy; import PIL; print('NumPy:', numpy.__version__); print('Pillow:', PIL.__version__)"
```

The command should print the installed NumPy and Pillow versions without an error.

---

# Preparing the logo

## 8. Check the source image

The recommended source is:

```text
jellyfin_logo.png
```

For the best result, the image should meet these requirements:

- PNG format
- 1004 × 288 pixels
- Full Jellyfin symbol and wordmark
- No cropping
- Transparent background preferred
- Original purple-to-blue symbol gradient
- White wordmark

The script can also process a logo with an opaque black background. It detects a solid black background from the image corners and converts it to transparency.

An image with another resolution can be used when it has the same aspect ratio as 1004 × 288. The script resizes it to 1004 × 288 automatically.

An image with a different aspect ratio will be rejected to prevent the logo from being stretched or distorted.

The animation timing and reveal areas are tuned to the supplied Jellyfin logo layout. A substantially different arrangement may require changes to the script.

---

# Rendering the animation

## 9. Run the script

With the virtual environment active, run:

```bash
python render_jellyfin_intro.py "jellyfin_logo.png"
```

The script will:

1. Read and prepare the logo.
2. Render 90 transparent PNG frames in a temporary folder.
3. Create the transparent ProRes 4444 MOV.
4. Create the H.264 MP4 preview.
5. Remove the temporary frames.
6. Print the locations of the completed files.

The completed files are written to the current folder.

### Use a separate output folder

To place the results in a folder named `output`, run:

```bash
python render_jellyfin_intro.py "jellyfin_logo.png" --output-directory "output"
```

The output folder is created automatically when it does not already exist.

### Use a logo stored elsewhere

Provide the complete path to the logo:

```bash
python render_jellyfin_intro.py "/path/to/jellyfin_logo.png"
```

Windows example:

```powershell
python render_jellyfin_intro.py "C:\Users\YourName\Pictures\jellyfin_logo.png"
```

Existing files with the same output names are overwritten when the script is run again.

---

# Converting the transparent master to WebP

Use the transparent MOV rather than the MP4:

```text
jellyfin_logo_intro_alpha.mov
```

The following command creates a high-quality, lossless animated WebP with transparency:

```bash
ffmpeg -y -i "jellyfin_logo_intro_alpha.mov" -vf "fps=30,format=bgra" -c:v libwebp_anim -lossless 1 -compression_level 6 -loop 1 -an "jellyfin_logo_intro.webp"
```

The resulting WebP retains:

- 1004 × 288 dimensions
- 30 frames per second
- Transparent background
- Silent playback
- One complete play

The `-loop 1` setting means the animation is played once. Use `-loop 0` only when an infinite loop is required.

Some websites, applications, or preview tools may ignore an animation's finite-loop setting and replay it automatically.

## Smaller WebP alternative

Lossless WebP can be relatively large. The following version uses high-quality lossy compression:

```bash
ffmpeg -y -i "jellyfin_logo_intro_alpha.mov" -vf "fps=30,format=bgra" -c:v libwebp_anim -lossless 0 -q:v 85 -compression_level 6 -loop 1 -an "jellyfin_logo_intro.webp"
```

Increase `-q:v 85` toward `100` for higher quality and a larger file. Lower it for a smaller file.

---

# Troubleshooting

## `ffmpeg` is not recognized or cannot be found

Run:

```text
ffmpeg -version
```

When the command fails:

1. Confirm FFmpeg is installed.
2. Confirm the folder containing the executable is on `PATH`.
3. Close and reopen the terminal after changing `PATH`.
4. Restart an open code editor or development environment.

### Find FFmpeg on Windows

```powershell
where ffmpeg
```

### Find FFmpeg on macOS or Linux

```bash
which ffmpeg
```

The script does not need a direct FFmpeg file reference when either command returns an executable location.

## `No module named numpy`

Activate the virtual environment and run:

```bash
python -m pip install "numpy>=2.1,<3"
```

## `No module named PIL`

The import name is `PIL`, but the package is installed as `Pillow`.

Run:

```bash
python -m pip install "Pillow>=12,<13"
```

Do not install the old package named `PIL`.

## PowerShell will not activate the virtual environment

PowerShell may display a message stating that script execution is disabled.

Use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Alternatively, run the virtual environment's Python directly without activating it:

```powershell
.venv\Scripts\python.exe -m pip install "numpy>=2.1,<3" "Pillow>=12,<13"
```

Then render with:

```powershell
.venv\Scripts\python.exe render_jellyfin_intro.py "jellyfin_logo.png"
```

This does not require changing the PowerShell execution policy.

## `Unknown encoder 'libx264'`

The installed FFmpeg build does not contain the H.264 encoder needed for the MP4 preview.

Install a full FFmpeg build:

- Windows: use `Gyan.FFmpeg`
- macOS: use the Homebrew `ffmpeg` formula
- Fedora: use the complete RPM Fusion package
- Other Linux distributions: use a package that includes `libx264`

## `Unknown encoder 'prores_ks'`

The installed FFmpeg build is incomplete or unusually minimal. Replace it with a complete FFmpeg build.

## `Unknown encoder 'libwebp_anim'`

The video renderer can still create the MOV and MP4, but the optional WebP conversion command requires an FFmpeg build with libwebp animation support.

Install a full FFmpeg build and check again with:

```text
ffmpeg -hide_banner -encoders
```

## The transparent MOV appears to have a black background

Many ordinary video players do not show transparency. They display transparent areas as black.

Use the MOV in an application that supports alpha channels, or convert it to WebP using the command in this guide.

The MP4 preview always has a black background by design.

## The script reports an aspect-ratio error

Use a source image measuring exactly 1004 × 288 pixels, or resize it to another resolution with the same aspect ratio.

Do not stretch the image to force it into the required dimensions.

## A path containing spaces does not work

Place quotation marks around the complete path:

```bash
python render_jellyfin_intro.py "C:\My Logo Files\jellyfin_logo.png"
```

## The script cannot write the output files

Choose a folder where the current user has permission to create files:

```bash
python render_jellyfin_intro.py "jellyfin_logo.png" --output-directory "output"
```

Avoid protected operating-system folders such as `C:\Windows`, `/System`, or `/usr`.

---

# Closing the virtual environment

After rendering is complete, leave the virtual environment with:

```bash
deactivate
```

The `.venv` folder can be deleted later to remove the locally installed Python packages. It can be recreated at any time by following the setup instructions again.

---

# Official references

- [Python downloads](https://www.python.org/downloads/)
- [FFmpeg downloads](https://ffmpeg.org/download.html)
- [Gyan FFmpeg builds for Windows](https://www.gyan.dev/ffmpeg/builds/)
- [Homebrew](https://brew.sh/)
- [Homebrew FFmpeg formula](https://formulae.brew.sh/formula/ffmpeg)
- [NumPy installation guide](https://numpy.org/install/)
- [Pillow installation guide](https://pillow.readthedocs.io/en/stable/installation/basic-installation.html)
- [Pillow Python-version support](https://pillow.readthedocs.io/en/stable/installation/python-support.html)
- [RPM Fusion configuration](https://rpmfusion.org/Configuration)
- [RPM Fusion multimedia guide](https://rpmfusion.org/Howto/Multimedia)
- [WebP container specification](https://developers.google.com/speed/webp/docs/riff_container)

---

Dependency and installation guidance last reviewed in September 2026.
