
# NB: This script is shared with the FDM_Build repo. If you make changes to it
# here, you should also change it there.
# TODO: Make a repo/package for tools like this to avoid redundancy.

Usage = """
    python versionbump.py [filePath]... [bumpType] [buildNumber]?
    filePath : string
        Path to a file containing files associated with pattern types. Every file has
        a regex pattern containing exactly one instance of the {versionNumber}
        replacement field, which must not be preceded by any groups.
    bumpType : character
        What kind of operation to do. Five version changes are supported: 
        Major ('M'), minor ('m'), patch ('p'), build ('b'), and copy ('c').
        Options ('M'), ('m'), and ('p') are used to increment the 1st, 2nd, and 3rd
        version numbers. 
        Option ('b') sets the 3rd version number to match the following int arg.
        Option ('c') uses the first file/pattern argument pair as the version 
        number source, copying this number to all the other file/patterns listed.
"""

import re
import sys
import versionUtils

options = [b[0] for b in versionUtils.versionBits] + ['c', 'b']

if __name__ == '__main__':
    if '--help' in sys.argv:
        print 'Usage:' + Usage
        exit()

    optionArgs = []
    files = []
    buildNumberArg = None
    lastArg = None
    for arg in sys.argv[1:]:
        if (lastArg == 'b'):
            #then treat the next argument as the specific build number to add
            try:
                buildNumberArg = int(arg)
            except:
                print 'No valid build number supplied'
                exit(-1)
        else:
            (optionArgs if arg in options else files).append(arg)
        lastArg = arg
    
    bumpType = optionArgs[0] if len(optionArgs) > 0 else None
    
    if bumpType == 'b':
        if buildNumberArg == None:
            print 'No build argument'
            exit(-1)
        print('Setting build number to ' + str(buildNumberArg))
        inputs = versionUtils.loadVersionLocations(files)
        versionUtils.addBuildVersion(inputs, buildNumberArg)
    elif bumpType == 'c':
        #then copy the version number from the first file,pattern specified to all other files listed
        print('Copying version in file ' + files[0])
        inputs = versionUtils.loadVersionLocations(files)
        versionUtils.setAssemblyVersions(inputs[1:], inputs[0])
    else:
        # let the interactive bump options decide what to do
        inputs = versionUtils.loadVersionLocations(files)
        versionUtils.bumpVersions(inputs, bumpType)
    exit()
