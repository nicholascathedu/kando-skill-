# Starts menus_guard.py with the first working Python 3.9+ when Claude Code runs hooks in
# PowerShell (Windows without Git Bash). hooks.json reads the hook's input into $kandoEvent and
# sets $mode, then runs this file with Invoke-Expression, so the execution policy doesn't
# block it. Without a working Python the guard stays out of the way, quietly.
if (-not $kandoEvent -or -not $kandoEvent.Contains('menus.json')) { exit 0 }
$guard = Join-Path $env:CLAUDE_PLUGIN_ROOT 'hooks/menus_guard.py'
$OutputEncoding = New-Object System.Text.UTF8Encoding $false
# python.exe is often the Microsoft Store stub, which fails the version check and is skipped.
foreach ($try in @('py -3', 'python3', 'python', 'uv run --no-project python')) {
    $parts = $try.Split(' ')
    if (-not (Get-Command $parts[0] -CommandType Application -ErrorAction SilentlyContinue)) { continue }
    $rest = @($parts | Select-Object -Skip 1)
    try {
        & $parts[0] @rest -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>$null | Out-Null
    } catch { continue }
    if ($LASTEXITCODE -ne 0) { continue }
    $kandoEvent | & $parts[0] @rest $guard $mode
    exit $LASTEXITCODE
}
exit 0
