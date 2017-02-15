
# NB: This script is shared with the eagle-printer-service repo. If you make
# changes to it here, you should also change it there.
# TODO: Make a repo/package for tools like this to avoid redundancy.

Usage = """
    python versioncheck.py patternsFile
    patternsFile : string
        Path to a file containing a version patterns.
"""

import sys
import versionUtils

checkOptions = ['--release' ]

if __name__ == '__main__':
    if '--help' in sys.argv:
        print 'Usage:' + Usage
        exit(0)
    checkType = None
    for i in range(1,len(sys.argv)):
        if sys.argv[i] in checkOptions:
            checkType = sys.argv[i]
            break
    #get list of all files with patterns
    files = [arg for arg in sys.argv[1:] if arg not in checkOptions]
    code = 0
    if len(files) > 0:
        patterns = versionUtils.loadVersionsPatterns(files)
        if checkType == None:
             code = versionUtils.checkVersions(patterns)
        else:
             code = versionUtils.checkReleaseVersions(patterns)
    exit(code)

