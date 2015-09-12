@echo off

IF "%1"=="-f" GOTO 1

echo Before you start the building, please make sure that all dependencies have been installed.
echo The easiest way to check this - run swapy-ob.py
echo Also check PyInstaller installed for 32/64 bit python.
echo Use "build -f" to ignore this interactive mode.
echo.
echo.
pause

:1
set home=%cd%
C:\Python27\Scripts\pyinstaller.exe --clean swapy.spec
copy dist\swapy.exe %home%\swapy32bit.exe

C:\Python27x64\Scripts\pyinstaller.exe --clean swapy.spec
copy dist\swapy.exe %home%\swapy64bit.exe
