@echo off
echo Requesting Administrator Access...
pushd %~dp0
    :: Running prompt elevated
:-------------------------------------
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------
echo.
echo Setting PATHs...
echo.

IF EXIST C:\Python27 (
set PATH2=C:\Python27
) ELSE (
echo Python path not found, please specify or install.
echo.
set /p PATH2= Specify Python path: 
)


echo ;%PATH%; | find /C /I "%PATH2%" > echo.txt
find /c "1" echo.txt
if %errorlevel% equ 1 goto Notfound
goto found

:found
cls
del echo.txt
echo Path is already set, skipping...
goto Continue

:notfound
cls
del echo.txt
setx PATH "%PATH%;%PATH2%;%PATH2%\Scripts;"
echo.
echo Path set, continuing..
goto Continue


:Continue

popd

echo.
echo Installing requirements...
echo. 

"%PATH2%\python" get-pip.py
cd ..\..
"%PATH2%\Scripts\pip" install -r requirements.txt
"%PATH2%\Scripts\pip" install -r requirements.txt --upgrade

call npm install
call npm run build

cd config
set /p API= Enter your Google API key here:
"%PATH2%\python" -c "print open('config.ini.example').read().replace('#gmaps-key:','gmaps-key:%API%')" > config.ini

echo All done!
pause
