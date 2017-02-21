
# NB: This script is shared with the FDM_Build repo. If you make changes to it
# here, you should also change it there.
# TODO: Make a repo/package for tools like this to avoid redundancy.
import re
import sys

versionLimit = 65536
versionBits = [
    ('M', 'first', 0),
    ('m', 'second', 1),
    ('p', 'third', 2),
]


# Regex patterns dictionary with types of patterns applicable for matching
# Regex pattern containing exactly one instance of the {versionNumber}
# replacement field, which must not be preceded by any groups.
versionsDictionary = { 
    'wixInstallerPattern': "<Product.*Version=\"{versionNumber}\"",
    'installedPathPattern': "<Directory Id='Version' Name='{versionNumber}'>",
    'assemblyVersionPattern': "AssemblyVersion\(\"{versionNumber}\"\)",
    'msiManifestPattern': "\"version\": \"{versionNumber}\",",
    'assemblyProductVersionPattern': "AssemblyInformationalVersion\(\"{versionNumber}\"\)",
    'versionFilePattern': "{versionNumber}"
}

# loads versions files and maps it to version path objects using versionsDictionary
# objects contain a filePath and a pattern property
def loadVersionLocations(versionsfiles):
    locations = []
    for versionsfile in versionsfiles:
        with open(versionsfile, "r") as text_file:
            for line in text_file:
                line = line.strip()
                if (not line.startswith("##")) and (',' in line):
                    pattern = line.split(',', 1) # splits only on first comma
                    if pattern[1] not in versionsDictionary.keys():
                        sys.exit("Invalid pattern." + pattern[1]);
                    locations.append({'filePath': pattern[0], 'pattern': versionsDictionary[pattern[1]]})
    return locations


# adds a 'version' field (int array) to every location entry
def reloadVersionsFromFiles(versionLocations):
    for location in versionLocations:
        location['number'] = getVersionFromFile(location)


# outputs file contents as string and version regex result
def findVersionInFile(versionLocation):
    filePath = versionLocation['filePath']
    versionPattern = versionLocation['pattern']
    content = ''
    with open(filePath, 'r') as inFile:
        content = inFile.read()

    result = re.search(versionPattern.format(versionNumber='([\d\.]*\d)'), content)
    if (result is None) or (len(result.groups()) != 1):
        print 'No valid version format in "' + filePath + '"'
        exit(1)

    return (content, result)


# outputs version as array of integers
def getVersionFromFile(versionLocation):
    (content, result) = findVersionInFile(versionLocation)
    return map(int, result.groups()[0].split('.'))


# writes new version to location with the same precision
# outputs written version
def writeVersionToFile(versionLocation, newVersion):
    (content, result) = findVersionInFile(versionLocation)
    existingVersion = result.groups()[0].split('.')
    replacementVersion = newVersion[:len(existingVersion)]
    content = content[:result.start(1)] + versionStr(replacementVersion) + content[result.end(1):]
    with open(versionLocation['filePath'], 'w') as outFile:
        outFile.write(content)
    return replacementVersion


def versionStr(versionNumber):
    return '.'.join(map(str, versionNumber))



# ----------------- higher level operations ----------------- #

# copy version numbers from sourceLocation to versionLocations
def setAssemblyVersions(versionLocations, sourceLocation):
    targetVersion = getVersionFromFile(sourceLocation)
    reloadVersionsFromFiles(versionLocations)
    for location in versionLocations:
        replacementVersion = writeVersionToFile(location, targetVersion)
        print location['filePath'] + ':'
        print '  ' + versionStr(location['number']) + ' -> ' + versionStr(replacementVersion)


# assign build version to each of versionLocations, modulo 2^16
def addBuildVersion(versionLocations, buildNumber):
    buildNumber %= versionLimit
    reloadVersionsFromFiles(versionLocations)
    bumpIndex = 2 # third version number
    
    for version in versionLocations:
        newNumber = [x for x in version['number']]
        #create minor version numbers if there aren't enough
        while len(newNumber) <= bumpIndex:
            newNumber.append(0)

        newNumber[bumpIndex] = buildNumber

        for i in range(bumpIndex + 1, len(newNumber)):
            newNumber[i] = 0

        replacementVersion = writeVersionToFile(version, newNumber)

        print version['filePath'] + ':'
        print '  ' + versionStr(version['number']) + ' -> ' + versionStr(replacementVersion)


# increment version number in each of versionLocations, modulo 2^16
# if version number is shorter than the desired bump, it is unchanged
# if longer, the numbers following the bump are reset to zero
def bumpVersions(versionLocations, bumpArg):
    reloadVersionsFromFiles(versionLocations)
    
    bumpIndex = None
    for bit in versionBits:
        if bit[0] == bumpArg:
            bumpIndex = bit[2]

    if bumpIndex is None:
        for version in versionLocations:
            print version['filePath'] + ':'
            print '    ' + '.'.join(map(str, version['number']))

        print 'What number do you want to bump?'
        for bit in versionBits:
            print '  ' + bit[0] + ' - ' + bit[1]

        choice = raw_input()
        choice = next((bit for bit in versionBits if choice == bit[0]), None)
        if choice is None:
            print 'Never mind.'
            return
        else:
            bumpIndex = choice[2]
    
    for version in versionLocations:
        newNumber = [x for x in version['number']]
        if len(newNumber) > bumpIndex:
            newNumber[bumpIndex] += 1
            newNumber[bumpIndex] %= versionLimit # for 3rd and 4th numbers
            for i in range(bumpIndex + 1, len(newNumber)):
                newNumber[i] = 0
        replacementVersion = writeVersionToFile(version, newNumber)

        print version['filePath'] + ':'
        print '  ' + versionStr(version['number']) + ' -> ' + versionStr(replacementVersion)


# checks the main version number against the other versions
# if releaseCheck is not set, ignores third main version number
# enforces that non-main version numbers match exactly to precision
def checkVersions(mainVersionLocation, buildVersionLocations, releaseCheck):
    reloadVersionsFromFiles([mainVersionLocation])
    reloadVersionsFromFiles(buildVersionLocations)
    
    print 'Main version file: ' + mainVersionLocation['filePath']
    mainVersion = mainVersionLocation['number']
    if mainVersion[0] > 255 or mainVersion[1] > 255:
        print 'Major and minor versions must be >=0 and <255, found: ' + versionStr(mainVersion)
        return -1
    
    # match all versions against longest version number used in builds
    longestBuildVersion = max(buildVersionLocations, key=lambda k: len(k['number']))['number']
    
    # check that main version number matches the highest precision build version
    # ignore third number for non-release builds
    # always ignore fourth number
    if releaseCheck:
        print 'Enforcing 3rd version number from main version'
    for i in ([0, 1, 2] if releaseCheck else [0, 1]):
        if mainVersion[i] != longestBuildVersion[i]:
            print 'Main version number does not match other numbers: ' + versionStr(mainVersion) + ' vs ' + versionStr(longestBuildVersion)
            return -1
    print 'Longest build version = ' + versionStr(longestBuildVersion) + ' satisfies main version = '  + versionStr(mainVersion)
    
    # check that all non-main version numbers match each other (up to precision of at least 2)
    for version in buildVersionLocations:
        verNumber = version['number']
        lengthHere = len(verNumber)
        if lengthHere < 2:
            print 'All versions are expected to have at least two numbers, see file ' + version['filePath']
            return -1
        if verNumber != longestBuildVersion[0:lengthHere]:
            print version['filePath'] + ' version: ' + versionStr(verNumber) + ' failed to match: ' + versionStr(longestBuildVersion)
            return -1
    print 'All versions used in builds match longest build version = ' + versionStr(longestBuildVersion)
    return 0

