@echo off
REM ============================================================
REM Build Script untuk CKLogistik - Optimized Version
REM ============================================================

echo.
echo ============================================================
echo  BUILDING OPTIMIZED CKLogistik Executable
echo ============================================================
echo.

REM Check if PyInstaller installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not found!
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

echo [1/3] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist\CKLogistik rmdir /s /q dist\CKLogistik
if exist dist\CKLogistik.exe del /q dist\CKLogistik.exe
if exist dist\CKLogistik_Fast rmdir /s /q dist\CKLogistik_Fast
echo       Done!
echo.

echo ============================================================
echo Choose build mode:
echo.
echo [1] ONE-FILE MODE (slower startup, portable single exe)
echo [2] ONE-FOLDER MODE (faster startup, RECOMMENDED)
echo ============================================================
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo [2/3] Building ONE-FILE executable...
    echo       This may take a few minutes...
    pyinstaller CKLogistik.spec --clean --noconfirm
    echo       Done!
    echo.
    echo [3/3] Build complete!
    echo.
    echo ============================================================
    echo  BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo Executable: dist\CKLogistik.exe
    echo.
    echo NOTE: One-file mode has slower startup because it needs to
    echo       extract files to temp folder first.
    echo.
    echo TIP:  Use one-folder mode for faster startup!
    echo ============================================================
) else if "%choice%"=="2" (
    echo.
    echo [2/3] Building ONE-FOLDER executable (FAST MODE)...
    echo       This may take a few minutes...
    pyinstaller CKLogistik_Fast.spec --clean --noconfirm
    echo       Done!
    echo.
    echo [3/3] Build complete!
    echo.
    echo ============================================================
    echo  BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo Executable: dist\CKLogistik_Fast\CKLogistik.exe
    echo.
    echo NOTE: One-folder mode is FASTER on startup!
    echo       Distribute the entire CKLogistik_Fast folder.
    echo.
    echo OPTIMIZATIONS APPLIED:
    echo   - Bytecode optimization level 1 (keep docstrings for pandas)
    echo   - UPX compression disabled (faster)
    echo   - Unnecessary modules excluded (scipy, matplotlib, etc)
    echo   - Required modules included (pandas, numpy, openpyxl)
    echo   - Assets properly included
    echo   - No temp extraction needed
    echo ============================================================
    echo.
    echo NOTE: File size akan lebih besar karena include pandas + numpy
    echo       Tapi startup tetap JAUH lebih cepat dari build lama!
    echo ============================================================
) else (
    echo.
    echo [ERROR] Invalid choice! Please run again and choose 1 or 2.
    echo.
    goto end
)

echo.
pause

:end
