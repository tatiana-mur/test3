
@echo off

python "scripts/versionbump.py" %* "scripts/VersionFilePattern.txt"

@echo %ERRORLEVEL%
EXIT /B %ERRORLEVEL%