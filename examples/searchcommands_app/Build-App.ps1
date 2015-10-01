[CmdletBinding()]
param(
    [parameter(Mandatory=$false)]
    [switch]
    $Clean,
    [parameter(Mandatory=$false)]
    [switch]
    $DebugBuild
)

$buildNumber = git log -1 --pretty=format:%ct

$debugClient = if ($DebugBuild) {
    "--debug-client=`"C:\Program Files (x86)\JetBrains\PyCharm\debug-eggs\pycharm-debug.egg`""
}
else {
    ""
}

if ($Clean) {
    Get-Item -ErrorAction SilentlyContinue "$PSScriptRoot\build", "${env:SPLUNK_HOME}\etc\apps\chunked_searchcommands" | Remove-Item -ErrorAction Stop -Force -Recurse
}

$ErrorActionPreference = "Continue" ;# Because PowerShell assumes a command has failed if there's any output to stderr even if the command's exit code is zero

python "${PSScriptRoot}\setup.py" build --build-number="${buildNumber}" $debugClient

if ($LASTEXITCODE -ne 0) {
    "Exit code = $LASTEXITCODE"
    return
}
