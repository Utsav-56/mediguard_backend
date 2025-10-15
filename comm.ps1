# if params of -p is also given, then push to remote repo
param(
    [switch]$p
)

git add .

# Ask for commit message 
$script:commitMessage = Read-Host "Enter commit message"
git commit -m $script:commitMessage

if ($p) {
    git push origin main
}