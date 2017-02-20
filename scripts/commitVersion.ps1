try {
    $branch = $args[0]
    $releaseRegex = [regex] 'FDMBS_Release_*'
    if (!($branch -match 'master' -Or $branch -cmatch $releaseRegex)) {
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
   } else {
        echo "Version already  defined [$newVersion]"
   }
  
} catch {
    echo $_.Exception.Message
    exit 1
}