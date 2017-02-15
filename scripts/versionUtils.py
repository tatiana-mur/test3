
# NB: This script is shared with the eagle-printer-service repo. If you make
# changes to it here, you should also change it there.
# TODO: Make a repo/package for tools like this to avoid redundancy.
import re
import sys

versionLimit = 65536
versionBits = [
    ('M', 'major', 0),
    ('m', 'minor', 1),
    ('p', 'patch', 2),
    ('b', 'build', 3),
    ('c', 'copy', -1)
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
    'versionFilePattern': "\A{versionNumber}\Z"
}

# loads versions files and maps it to tuples using versionsDictionary
def loadVersionsPatterns(versionsfiles):
    patterns = []
    for versionsfile in versionsfiles:
        with open(versionsfile, "r") as text_file:
            for line in text_file:
                line = line.strip()
                if (not line.startswith("##")) and (',' in line):
                    pattern = line.split(',', 1)
                    if pattern[1] not in versionsDictionary.keys():
                          sys.exit("Invalid pattern." + pattern[1]);
                    patternTuple = (pattern[0], versionsDictionary[pattern[1]])
                    patterns.append(patternTuple)
    return patterns

# copy version numbers from sourceLocation to versionLocations
def setAssemblyVersions(versionLocations, sourceLocation):
    version = getVersionFromFile(sourceLocation[0], sourceLocation[1])
    for location in versionLocations:
        # location[0] is filepath, location[1] is pattern to match
        oldversion = getVersionFromFile(location[0], location[1])
        replacementVersion = writeVersionToFile(location[0], location[1], version)
        print location[0] + ':'
        print '  ' + versionStr(oldversion) + ' -> ' + versionStr(replacementVersion)

# assign build version to each of versionLocations, modulo 2^16
def addBuildVersion(versionLocations, buildNumber):
    buildNumber %= versionLimit
    versions = [{ 'filePath': v[0], 'number': getVersionFromFile(v[0], v[1]), 'pattern': v[1] } for v in versionLocations]
    bumpIndex = 2

    for version in versions:
        newNumber = [x for x in version['number']]
        #create minor version numbers if there aren't enough
        if len(newNumber) <= bumpIndex:
            newNumber = newNumber + [0 for i in range(bumpIndex - len(newNumber) + 1)]

        newNumber[bumpIndex] = buildNumber

        for i in range(bumpIndex + 1, len(newNumber)):
            newNumber[i] = 0

        replacementVersion = writeVersionToFile(version['filePath'], version['pattern'], newNumber)

        print version['filePath'] + ':'
        print '  ' + versionStr(version['number']) + ' -> ' + versionStr(replacementVersion)

# increment version number in each of versionLocations, modulo 2^16
def bumpVersions(versionLocations, bumpType):
    versions = [{ 'filePath': v[0], 'number': getVersionFromFile(v[0], v[1]), 'pattern': v[1] } for v in versionLocations]
    longestVersion = sorted(versions, lambda x, y: len(y['number']) - len(x['number']))[0]
    bumpIndex = None

    for bit in versionBits:
        if bit[0] == bumpType:
            bumpIndex = bit[2]

    if bumpIndex is None:
        for version in versions:
            print version['filePath'] + ':'
            print '    ' + '.'.join(map(str, version['number']))

        print 'What number do you want to bump?'
        for bit in versionBits[:len(longestVersion['number'])]:
            print '  ' + bit[0] + ' - ' + bit[1]

        choice = raw_input()
        choice = next((bit for bit in versionBits if choice == bit[0]), None)
        if choice is None:
            print 'Never mind.'
            return

        bumpIndex = choice[2]

    for version in versions:
        newNumber = [x for x in version['number']]
        if len(newNumber) > bumpIndex:
            newNumber[bumpIndex] += 1
            newNumber[bumpIndex] %= versionLimit
            for i in range(bumpIndex + 1, len(newNumber)):
                newNumber[i] = 0
        replacementVersion = writeVersionToFile(version['filePath'], version['pattern'], newNumber)

        print version['filePath'] + ':'
        print '  ' + versionStr(version['number']) + ' -> ' + versionStr(replacementVersion)

# checks version number in each of versionLocations against shortest version
def checkVersions(versionLocations):
    versions = [{ 'filePath': v[0], 'number': getVersionFromFile(v[0], v[1]), 'pattern': v[1] } for v in versionLocations]
    shortestVersion = min(versions, key=lambda k: len(k['number']))['number']
    if len(shortestVersion) < 2:
        print 'Shortest version should have at lest major minor:' + versionStr(shortestVersion)
        return -1
    for version in versions:
        verNumber = version['number']
        if verNumber[:len(shortestVersion)] != shortestVersion:
            print version['filePath'] + ' version:' + versionStr(verNumber) + ' failed to match:' + versionStr(shortestVersion)
            return -1
    print 'version check is completed against:' + versionStr(shortestVersion)
    return 0

# checks version number in each of versionLocations against longest version
def checkReleaseVersions(versionLocations):
    versions = [{ 'filePath': v[0], 'number': getVersionFromFile(v[0], v[1]), 'pattern': v[1] } for v in versionLocations]
    longestVersion = max(versions, key=lambda k: len(k['number']))['number']
    if len(longestVersion) < 2:
        print 'Longest version should have at lest major minor:' + versionStr(longestVersion)
        return -1
    for version in versions:
        verNumber = version['number']
        if longestVersion[:len(verNumber)] != verNumber:
            print version['filePath'] + ' version:' + versionStr(verNumber) + ' failed to match:' + versionStr(longestVersion)
            return -1
    print 'Release version check is completed against:' + versionStr(longestVersion)
    return 0

def findVersionInFile(filePath, versionPattern):
    content = ''
    with open(filePath, 'r') as inFile:
        content = inFile.read()

    result = re.search(versionPattern.format(versionNumber='([\d\.]*\d)'), content)
    if (result is None) or (len(result.groups()) != 1):
        print 'No version found in "' + filePath + '"'
        exit(1)

    return (content, result)

def getVersionFromFile(filePath, versionPattern):
    (content, result) = findVersionInFile(filePath, versionPattern)
    return map(int, result.groups()[0].split('.'))

def writeVersionToFile(filePath, versionPattern, newVersion):
    (content, result) = findVersionInFile(filePath, versionPattern)
    existingVersion = result.groups()[0].split('.')
    replacementVersion = newVersion[:len(existingVersion)]
    content = content[:result.start(1)] + versionStr(replacementVersion) + content[result.end(1):]
    with open(filePath, 'w') as outFile:
        outFile.write(content)
    return replacementVersion

def versionStr(versionNumber):
    return '.'.join(map(str, versionNumber))
