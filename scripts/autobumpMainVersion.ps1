#
# This script is used in Teamcity by the Agent > CI (Windows) to update version.txt
# it is accepts branch name and mode parrern(master or PS_Release_* as inputs)
#
try {
    $branch = $args[0]
    $mode = $args[1]
    if (!($mode -cmatch 'master' -Or $mode -cmatch 'PS_Release_*')) {
        echo "Invalid autobump mode [$mode]"
        exit 1
    }
    $modeRegex = [regex] $mode
    if (!($branch -cmatch $modeRegex)) {
        echo "Branch does [$branch] not match mode [$mode]"
        exit 0
    }
    $currentBranch = (git rev-parse --abbrev-ref HEAD) | Out-String
    $currentBranch = $currentBranch.Trim()
    if (!($branch -cmatch $currentBranch)) {
        echo "Branch does [$branch] not match [$currentBranch]"
        exit 0
    }
    $content = (Get-Content -Path ".\version.txt" -Raw);
    $currentVersion = [version] $content.Trim();
    echo "Current version [$currentVersion]"
    if ($branch -cmatch 'master') {
        $newMajorVersion = $currentVersion.Major
        $newMinorVersion = $currentVersion.Minor + 1
		# using 254 to match cloud versioning limits, though 255 is the hard limit
		# this also allows us to create an installer that overrides all other production versions
        if($newMinorVersion -gt 254) {
            $newMinorVersion = 0
            $newMajorVersion = $currentVersion.Major + 1
			if ($newMajorVersion -gt 254) {
				throw "Exceeded maximum allowed version"
			}
        }
        $newVersion = [string]::Format("{0}.{1}.{2}.{3}", $newMajorVersion, $newMinorVersion, $currentVersion.Build, $currentVersion.Revision)
    } else { 
        $desiredBranchName =  [string]::Format("PS_Release_{0}.{1}.{2}", $currentVersion.Major, $currentVersion.Minor, $currentVersion.Build)
        if ($branch -cmatch $desiredBranchName) { 
            exit 0
        }
		# the developer workflow for patch releases is to branch from release branch with a name that has an incemented build number
        $updatedBranchName =  [string]::Format("PS_Release_{0}.{1}.{2}", $currentVersion.Major, $currentVersion.Minor, $currentVersion.Build + 1)
        if ($branch -cmatch $updatedBranchName) {
            $newVersion = [string]::Format("{0}.{1}.{2}.{3}",$currentVersion.Major, $currentVersion.Minor, $currentVersion.Build + 1, $currentVersion.Revision) 
        } else {
           throw "Unexpected Release branch  [$branch] expected  [$updatedBranchName]"
        }
    }
    echo "Bumping version from [$currentVersion] to [$newVersion]"
    
    "##teamcity[setParameter name='RELEASE_VERSION' value='$newVersion']"
     Out-File -FilePath ".\version.txt" -InputObject $newVersion -Encoding ascii
} catch {
    echo $_.Exception.Message
    exit 1
}