
# NB: This script is shared with the eagle-printer-service repo. If you make
# changes to it here, you should also change it there.
# TODO: Make a repo/package for tools like this to avoid redundancy.

Usage = """
    python versionbump.py [filePath]... [bumpType]
    filePath : string
        Path to a file containing files associated with pattern types.
        Regex pattern containing exactly one instance of the {versionNumber}
        replacement field, which must not be preceded by any groups.
    bumpType : character
        What kind of operation to do. Five version changes are
        supported: major ('M'), minor ('m'), patch ('p'), build ('b'), and copy
        ('c'). The first four are used to increment version numbers. Adding a
        number after 'b' sets the build to that number instead of incrementing
        the current number. The final operation, copy ('c'), uses the first
        file/pattern argument pair as the version number source, copying this
        number to all the other file/patterns listed
"""

import re
import sys
import versionUtils


if __name__ == '__main__':
    if '--help' in sys.argv:
        print 'Usage:' + Usage
        exit()

    versionBitNames = [x[0] for x in versionUtils.versionBits]
    bumpType = None
    typeArgIndex = -1
    for i in range(1,len(sys.argv)):
        if sys.argv[i] in versionBitNames:
            bumpType = sys.argv[i]
            typeArgIndex = i
            break

    if bumpType == None:
        print 'Usage:' + Usage
 
    if bumpType == 'b' and len(sys.argv) > typeArgIndex and str.isdigit(sys.argv[1+typeArgIndex]):
        #then treat the next argument as the specific build number to add
        nonVersionArgs = sys.argv[1:typeArgIndex] + sys.argv[typeArgIndex+2:]
        files = [arg for arg in nonVersionArgs if arg not in versionBitNames]
        inputs = versionUtils.loadVersionsPatterns(files)
        versionUtils.addBuildVersion(inputs, int(sys.argv[typeArgIndex+1]))
    elif bumpType == 'c':
        #then copy the version number from the first file|pattern specified
        #to all other files listed
        otherArgs = sys.argv[1:typeArgIndex] + sys.argv[typeArgIndex+1:]
        files = [arg for arg in otherArgs if arg not in versionBitNames]
        inputs = versionUtils.loadVersionsPatterns(files)
        versionUtils.setAssemblyVersions(inputs[1:], inputs[0])
    else:
        #do the original script logic
        files = [arg for arg in sys.argv[1:] if arg not in versionBitNames]
        if len(files) > 0:
            inputs = versionUtils.loadVersionsPatterns(files)
            versionUtils.bumpVersions(inputs, bumpType)
    exit()
