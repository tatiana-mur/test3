
# NB: This script is shared with the FDM_Build repo. If you make changes to it
# here, you should also change it there.
# TODO: Make a repo/package for tools like this to avoid redundancy.

Usage = """
    python versioncheck.py [versionFile] [--release]? [patternsFile]...
    versionFile : string
        Master version file
    --release : optional string
        Switches to release versioning check (does not ignore 3rd number)
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
    
    options = []
    files = []
    # triage non-scriptname args
    for arg in sys.argv[1:]:
        (options if arg in checkOptions else files).append(arg)
    
    exitCode = 0
    if len(files) > 1:
        patterns = versionUtils.loadVersionLocations(files)
        exitCode = versionUtils.checkVersions(patterns[0], patterns[1:], len(options) != 0)
    exit(exitCode)

