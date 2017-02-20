# This script is used in Teamcity by the Agent > CI (Windows) to update version.txt
try {
    $branch = $args[0]
    $releaseRegex = [regex] 'FDMBS_Release_*'
    if (!($branch -match 'master' -Or $branch -cmatch $releaseRegex)) {
        exit 0
    }
    $currentVersion = [version] (Get-Content -Path ".\version.txt" -Raw);

    if ($branch -match 'master') {
        $newMajorVersion = $currentVersion.Major
        $newMinorVersion = $currentVersion.Minor + 1
        if($newMinorVersion -gt 254) {
            $newMinorVersion = 0
            $newMajorVersion = $currentVersion.Major + 1
       }
        $newVersion = ("{0}.{1}.{2}.{3}" -f $newMajorVersion, $newMinorVersion, $currentVersion.Build, $currentVersion.Revision)
    } else { 
        $expectedBranchName =  ("FDMBS_Release_{0}.{1}.{2}" -f $currentVersion.Major, $currentVersion.Minor, $currentVersion.Build + 1) 
        if($branch -match $expectedBranchName) {
            $newVersion = ("{0}.{1}.{2}.{3}" -f $currentVersion.Major, $currentVersion.Minor, $currentVersion.Build + 1, $currentVersion.Revision) 
        }
        else {
           throw "Unexpected Release branch  [$branch]"
        }
    }
    echo "Bumping version from [$currentVersion] to [$newVersion]"
    
    "##teamcity[setParameter name='RELEASE_VERSION' value='$newVersion']"
    Out-File -FilePath ".\version.txt" -InputObject $newVersion -Encoding ascii
} catch {
    echo $_.Exception.Message
    exit 1
}