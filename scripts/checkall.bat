
@echo off

python "scripts/versionCheck.py" "scripts/VersionFilePattern.txt" %* "scripts/VersioningPatterns.txt"

@echo %ERRORLEVEL% 
EXIT /B %ERRORLEVEL%