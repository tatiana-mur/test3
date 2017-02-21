 # This script is used in Teamcity by the Agent > CI (Windows) to commit version.txt and cut release branch from master
 # it is accepts branch name and mode parrern(master or PS_Release_* as inputs)
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
    $newVersion = [version] (Get-Content -Path ".\version.txt" -Raw) 
    $modifiedVersion = (git status --porcelain version.txt) | Out-String     
    $modifiedVersion = $modifiedVersion.Trim()
    if ($modifiedVersion.contains("version.txt")) { 
        $gitTagVersion = [string]::Format("{0}.{1}.{2}", $newVersion.Major, $newVersion.Minor, $newVersion.Build) 
        echo "Updating [$gitTagVersion]"
        # Git setup - key, name, email
        git config user.name "TeamCity Agent"
        git config user.email "gc-ci@grabcad.com"
    
        git add version.txt
        if ($LastExitCode -ne 0) {
            throw "Failed to add version.txt $LastExitCode."
        }
        git commit -m "Automatic update of $gitTagVersion"
        if ($LastExitCode -ne 0) {
            throw "Failed to commit version.txt $LastExitCode."
        }
        git tag -a $gitTagVersion -m $gitTagVersion
        if ($LastExitCode -ne 0) {
            throw "Failed to tag commit version.txt with tag: [$gitTagVersion] error:[$LastExitCode]."
        }
        # Push changes back to GitHub
        git push --set-upstream origin --tags HEAD
        if ($LastExitCode -ne 0) {
            throw "Failed to push updates for: [$gitTagVersion] error:[$LastExitCode]."
        }
        # Create a branch if on master
        if ($branch -cmatch 'master') {
            try {
                $newGitTagBranch = [string]::Format("PS_Release_{0}", $gitTagVersion)
                $existingBranches = (git ls-remote --heads -q) | Out-String
                $branchList = $existingBranches.Trim() -split "[\r\n]+"
                foreach ($branch in $branchList) {
                    if ($branch.contains($newGitTagBranch)) {
                        throw "Branch already exists: [$branch] [$newGitTagBranch]."
                    }
                }
                git checkout -b $newGitTagBranch
                if ($LastExitCode -ne 0) {
                    throw "Failed to create: [$newGitTagBranch] error:[$LastExitCode]."
                }
                git push origin $newGitTagBranch
                if ($LastExitCode -ne 0) {
                    throw "Failed to push : [$newGitTagBranch] error:[$LastExitCode]."
                }
            } Finally {
               git checkout master
            }
        }
   } else {
        echo "Version already  defined [$newVersion]."
   }
  
} catch {
    echo $_.Exception.Message
    exit 1
}