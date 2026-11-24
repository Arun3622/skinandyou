$ErrorActionPreference = 'Stop'
$runtime = Join-Path $env:LOCALAPPDATA 'SkinAndYouLocal'
$python = Join-Path $PSScriptRoot '.local/venv/Scripts/python.exe'
$backend = Join-Path $PSScriptRoot 'www/skin_and_you'
$url = 'http://127.0.0.1:8000/'

if (-not (Test-Path -LiteralPath $python)) {
    throw 'The project Python environment is missing. Create .local/venv and install requirements-local.txt.'
}

function Test-LocalSite {
    $response = curl.exe --noproxy '*' --silent --include --fail --max-time 2 $url
    return ($LASTEXITCODE -eq 0 -and
        ($response -match '<title>Skin & You</title>') -and
        ($response -match "Content-Security-Policy: .*connect-src 'self'"))
}

if (Test-LocalSite) {
    Write-Output "Skin & You is already running at $url"
    return
}

$env:SKIN_LOCAL_DB_PASSWORD = (Get-Content -LiteralPath (Join-Path $runtime 'db-password') -Raw).Trim()
$env:SKIN_LOCAL_SECRET_KEY = (Get-Content -LiteralPath (Join-Path $runtime 'django-secret') -Raw).Trim()

function Test-LocalDatabase {
    # A WSL forwarding socket can accept TCP before PostgreSQL accepts connections.
    $probe = 'import os, psycopg2; psycopg2.connect(dbname="skin_n_you_local", user="skin_user", password=os.environ["SKIN_LOCAL_DB_PASSWORD"], host="127.0.0.1", port=55432, connect_timeout=2).close()'
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $python
    $startInfo.Arguments = '-c "' + $probe.Replace('"', '\"') + '"'
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true

    $probeProcess = New-Object System.Diagnostics.Process
    $probeProcess.StartInfo = $startInfo
    $null = $probeProcess.Start()
    $null = $probeProcess.StandardOutput.ReadToEnd()
    $null = $probeProcess.StandardError.ReadToEnd()
    $probeProcess.WaitForExit()
    return ($probeProcess.ExitCode -eq 0)
}

if (-not (Test-LocalDatabase)) {
    # WSL may stop a background Linux service when its last Windows client exits.
    $postgresErrors = Join-Path $runtime 'postgres-errors.log'
    $postgres = Start-Process -FilePath wsl.exe -WindowStyle Hidden -PassThru `
        -ArgumentList '-d Ubuntu -u root -- sh -c "pg_ctlcluster 18 skinandyou start; pg_isready -q -p 55432 && exec sleep infinity"' `
        -RedirectStandardOutput (Join-Path $runtime 'postgres-output.log') -RedirectStandardError $postgresErrors
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ($postgres.HasExited) {
            throw "PostgreSQL exited. See $postgresErrors"
        }
        if (Test-LocalDatabase) {
            break
        }
        if ($attempt -eq 29) { throw "PostgreSQL did not respond. See $postgresErrors" }
        Start-Sleep -Milliseconds 500
    }
}

$stderr = Join-Path $runtime 'django-errors.log'
$server = Start-Process -FilePath $python -WorkingDirectory $backend -WindowStyle Hidden -PassThru `
    -ArgumentList 'manage.py', 'runserver', '127.0.0.1:8000', '--settings=skin_and_you.local_settings', '--noreload', '--nostatic' `
    -RedirectStandardOutput (Join-Path $runtime 'django-output.log') -RedirectStandardError $stderr

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    if ($server.HasExited) {
        throw "Django exited. See $stderr"
    }
    if (Test-LocalSite) {
        Write-Output "Skin & You is running at $url"
        return
    }
}

throw "Django did not respond at $url. See $stderr"
