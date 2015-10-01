[CmdletBinding()]
param(
    [parameter(Mandatory=$false)]
    [switch]
    $Clean,
    [ValidateScript(ScriptBlock={Test-Path $_})]
    [parameter(Mandatory=$false)]
    [string]
    $DebugClient
)

# TODO: Answer this: We like "splunk restart -f" because it's fast, but what's the right thing to do for customers?
# TODO: Do the right thing when SPLUNK_HOME is undefined
# TODO: Parameterize version number

$appName = Split-Path -Leaf $PSScriptRoot
$buildNumber = git log -1 --pretty=format:%ct

$debugClient = if ($DebugClient -ne $null) {
    "--debug-client=`"$DebugClient`""
}
else {
    ""
}

if ($Clean) {
    Get-Item -ErrorAction SilentlyContinue "$PSScriptRoot\build", "${env:SPLUNK_HOME}\etc\apps\${appName}" | Remove-Item -ErrorAction Stop -Force -Recurse
}

$ErrorActionPreference = "Continue" ;# Because PowerShell assumes a command has failed if there's any output to stderr even if the command's exit code is zero

python "${PSScriptRoot}\setup.py" build --build-number="${buildNumber}" $debugClient

if ($LASTEXITCODE -ne 0) {
    "Exit code = $LASTEXITCODE"
    return
}

splunk start ;# Because the splunk daemon might not be running

if ($LASTEXITCODE -ne 0) {
    "Exit code = $LASTEXITCODE"
    return
}

splunk install app "${PSScriptRoot}\build\${appName}-1.0.0-${buildNumber}.tar.gz" -auth admin:changeme -update 1

if ($LASTEXITCODE -ne 0) {
    "Exit code = $LASTEXITCODE"
    return
}

splunk restart -f ;# Because a restart is usually required after installing an application

if ($LASTEXITCODE -ne 0) {
    "Exit code = $LASTEXITCODE"
    return
}
