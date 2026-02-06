# PowerShell completion for pythondocker
# Add to profile: . C:\path\to\pythondocker.ps1
# Or: pythondocker completions powershell | Out-String | Invoke-Expression

Register-ArgumentCompleter -CommandName pythondocker -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $words = $commandAst.CommandElements | ForEach-Object { $_.ToString() }
    $idx = $words.IndexOf($wordToComplete)
    if ($idx -lt 0) { $idx = $words.Count }

    $commands = @('list', 'info', 'clean', 'remove', 'freeze', 'completions')
    $versions = @('2.7', '3.11', '3.12', '3.13', 'pypy3.11', 'pypy3.10', 'pypy2.7', 'jython')
    $opts = @('--help', '--shell', '--python', '-p', '--requirements', '-r', '--args', '--env',
        '--verbose', '-v', '--force-recreate', '--encoding', '-e', '--no-deps', '--log-file',
        '-l', '--debug', '-d', '--offline')

    if ($wordToComplete -match '^-') {
        return $opts | Where-Object { $_ -like "$wordToComplete*" }
    }
    if ($idx -eq 1) {
        return $commands | Where-Object { $_ -like "$wordToComplete*" }
    }
    if ($idx -eq 2 -and $words[1] -eq 'remove') {
        return $versions | Where-Object { $_ -like "$wordToComplete*" }
    }
    return $null
}
