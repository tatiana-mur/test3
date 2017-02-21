try {
    $branch = $args[0]
    $mode = $args[1]
    if (!($mode -cmatch 'master' -Or $mode -cmatch 'PS_Release_*')) {
        echo "Invalid autobump mode [$mode]"
        exit 1
    }
    $modeRegex = [regex] $mode
    if (!($branch -cmatch $modeRegex)) {
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
        git commit -m "Automatic update of $gitTagVersion"
        git tag -a $gitTagVersion -m $gitTagVersion
        # Push changes back to GitHub
        git push --set-upstream origin --tags HEAD
        # Create a branch if on master
        if ($branch -cmatch 'master') {
           $newGitTagBranch = [string]::Format("PS_Release_{0}", $gitTagVersion)
           git checkout -b $newGitTagBranch
           git push origin $newGitTagBranch
        }
   } else {
        echo "Version already  defined [$newVersion]"
   }
  
} catch {
    echo $_.Exception.Message
    exit 1
}