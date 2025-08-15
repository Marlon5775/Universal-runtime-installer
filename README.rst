.. image:: https://img.shields.io/badge/Download%20now-green?style=plastic&link=https%3A%2F%2Fgithub.com%2FManily04%2FUniversal-runtime-installer%2Freleases%2Flatest
.. image:: https://img.shields.io/github/downloads/Manily04/Universal-runtime-installer/total?style=plastic&label=Downloads&color=blue




New and Improved with a GUI
=============================== 
This version is a complete rework of my old project now in Python instead of Batch and PowerShell.

Universal runtime installer
===============================
This installer allows to install the latest Visual C++ Runtime of all years (2008-2022), Full DirectX Runtime, Microsoft XNA Framework, .Net Runtime, Java and OpenAL at once.

updates
===============================
The `latest version <https://github.com/Manily04/Universal-runtime-installer/releases/latest>`_ downloads all runtimes independently, which means that when the tool is run, the latest available version of the runtime is always installed. (An internet connection is required for this tool)

offline setup
===============================
If you don't have an internet connection on the PC to be installed, you can use the old `offline setup <https://github.com/Manily04/Universal-runtime-installer-EN/releases/tag/v1>`__ because they still have all Visual Studio 2008 - 2022 Runtimes in the installer, but no more - Update status of `v1 <https://github.com/Manily04/Universal-runtime-installer-EN/releases/tag/v1>`_ - April 2022 (OUTDATET CMD TOOL)

Silent / Unattended Mode
==================================
From the GUI version onward you can run the installer fully unattended. Launch the EXE with one of these switches to install all bundled runtimes without any user interaction (all packages are selected automatically):

``/silent`` ``-silent`` ``--silent`` ``/s`` ``-s``

Example (PowerShell):

```powershell
./Universal runtime installer.exe /silent
```

Return codes:

* 0 – All installations succeeded
* 1 – winget not found (aborted)
* 2 – Some packages failed (check log)

Silent mode log file (with error details):
``%TEMP%/universal_runtime_silent/installer_log.txt``

Notes:
* Administrator rights required (the program auto-elevates if needed).
* The flags ``--accept-source-agreements`` and ``--accept-package-agreements`` are added automatically to winget commands.
* Already installed packages are skipped or upgraded when possible.

