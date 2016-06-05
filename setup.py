# ==============================================================================
#     Author: Thomas Rudge
#     Date:   2016-01-01
#     File:  setup.py
#     Description: This is a cx_Freeze setup file for turning the GUI
#                  file into a frozen standalone application
# ==============================================================================

from cx_Freeze import setup, Executable

includefiles = []
includes = []
excludes = []
packages = ['tkinter', 'sys', 'ctypes', 'csv', 'pickle', 'datetime', 'webbrowser', 'os', 'mt940_50']

build_exe_options = {"include_msvcr": True}

exe = Executable(
    script = "mt940_50.py",
    initScript = None,
    base = "Win32GUI",
    targetName = "MTGEN.exe",
    copyDependentFiles = True,
    compress = True,
    appendScriptToExe = True,
    appendScriptToLibrary = True,
    icon = 'mt9_ico.ico'
    )

setup(
    name = "MT940/50 Generator",
    version = "1.1.0",
    description = 'Generates swift MT940 and MT950 cash statements from csv.',
    author = "Thomas Edward Rudge",
    author_email = "thomas.rudge85@gmail.com",
    options = {"build_exe": {"excludes":excludes, "packages":packages, "include_files":includefiles}},
    executables = [exe]
    )
