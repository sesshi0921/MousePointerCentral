#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$InstallDir = Join-Path $env:USERPROFILE ".claude\mcp-servers\mouse-mcp"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$Settings   = Join-Path $env:USERPROFILE ".claude\settings.json"
$OutputDir  = Join-Path $env:USERPROFILE "Documents\mouse-mcp"

Write-Host "[1/4] ソースをコピー中: $InstallDir"
New-Item -ItemType Directory -Force -Path "$InstallDir\src" | Out-Null
Copy-Item -Recurse -Force "$ScriptDir\src\mouse_mcp" "$InstallDir\src\"
Copy-Item -Force "$ScriptDir\pyproject.toml" "$InstallDir\"

Write-Host "[2/5] Python 3.10+ を検索中"
$Python3 = $null
$candidates = @("python3.13","python3.12","python3.11","python3.10","python3","python")
foreach ($cmd in $candidates) {
    $exe = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($exe) {
        $ver = & $exe.Path -c "import sys; print(sys.version_info >= (3,10))" 2>$null
        if ($ver -eq "True") { $Python3 = $exe.Path; break }
    }
}
if (-not $Python3) {
    Write-Error "エラー: Python 3.10 以上が見つかりません"; exit 1
}
$pyVer = & $Python3 --version
Write-Host "  使用 Python: $Python3 ($pyVer)"

Write-Host "[3/5] venv作成・パッケージインストール中"
& $Python3 -m venv --clear "$InstallDir\.venv"
& "$InstallDir\.venv\Scripts\pip.exe" install --quiet --upgrade pip
& "$InstallDir\.venv\Scripts\pip.exe" install --quiet "$InstallDir"

$Python = "$InstallDir\.venv\Scripts\python.exe"

Write-Host "[4/5] settings.json を更新中"
New-Item -ItemType Directory -Force -Path (Split-Path $Settings) | Out-Null

$UpdateScript = @'
import json, sys, os

settings_path, python_path, output_dir = sys.argv[1], sys.argv[2], sys.argv[3]

if os.path.exists(settings_path):
    with open(settings_path, encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = {}

settings.setdefault("mcpServers", {})
settings["mcpServers"]["mouse"] = {
    "command": python_path,
    "args": ["-m", "mouse_mcp.server"],
    "env": {
        "MOUSE_MCP_OUTPUT_DIR": output_dir
    }
}

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")
'@

$TmpScript = [System.IO.Path]::GetTempFileName() + ".py"
Set-Content -Path $TmpScript -Value $UpdateScript -Encoding UTF8
& $Python $TmpScript $Settings $Python $OutputDir
Remove-Item $TmpScript

Write-Host "[5/5] 完了"
Write-Host "  インストール先: $InstallDir"
Write-Host "  録画出力先:     $OutputDir"
Write-Host "  Claude Code を再起動すると mouse MCP サーバーが有効になります"
