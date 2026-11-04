# Troubleshooting Guide

This guide covers common setup and runtime problems you may encounter while using PingPanda.

## 1. Unsupported Python Version

**Symptom:** The application fails to run or reports Python syntax or compatibility errors.

**Likely cause:** PingPanda requires Python 3.10 or newer, but an older version is installed or being used.

**Resolution:**
- Check your Python version:
  ```bash
  python --version
  ```
- Install Python 3.10 or newer if necessary.
- If multiple Python versions are installed, make sure you use the supported version when creating your virtual environment.

## 2. Virtual Environment Not Activated

**Symptom:** Python cannot find installed packages, even after installing the dependencies.

**Likely cause:** The virtual environment is not activated, or the packages were installed in a different Python environment.

**Resolution:**

Activate the virtual environment from the project directory.

- **Windows PowerShell:**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

If the environment does not exist, create it first:

```bash
python -m venv .venv
```

## 3. Dependency Installation Fails

**Symptom:** Installing dependencies produces errors, or the application reports that a required module cannot be found.

**Likely cause:** Dependencies were not installed successfully, or the wrong requirements file was used.

**Resolution:**

1. Activate your virtual environment.
2. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```
3. Install the project dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

For development and testing, install:

```bash
python -m pip install -r requirements-dev.txt
```

The development requirements file also installs the runtime dependencies.

## 4. Terminal Colours Are Missing or Incorrect

**Symptom:** Terminal output appears without colours or the colours look different from expected.

**Likely cause:** The terminal may not support colour output, or its colour settings may be disabled or limited.

**Resolution:**
- Try running PingPanda in a terminal that supports ANSI colour output.
- Check whether colour output is disabled in your terminal settings.
- On Windows, try using Windows Terminal or a recent PowerShell version.

## 5. Progress Bar or Special Characters Display Incorrectly

**Symptom:** Progress indicators or special characters appear incorrectly, as boxes, question marks, or unreadable symbols.

**Likely cause:** The terminal may have limited character encoding or display support.

**Resolution:**
- Use a terminal with UTF-8 encoding support.
- On Windows, try Windows Terminal or a recent PowerShell version.
- Make sure your terminal uses a compatible font.
- If the issue persists, try running the tool in another terminal.

## Still Having Problems?

If none of these solutions work, open an issue on the [PingPanda GitHub repository](https://github.com/tkmfoss/pingpanda).

Include your operating system, Python version, the command you ran, and the complete error message so the issue can be investigated.