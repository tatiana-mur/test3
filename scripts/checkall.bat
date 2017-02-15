
@echo off

python "scripts/versionCheck.py" %* "scripts/InstallerPatterns.txt" "scripts/AssembliesPatterns.txt"

@echo %ERRORLEVEL% 
EXIT /B %ERRORLEVEL%