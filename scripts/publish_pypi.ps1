$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (Test-Path dist) {
    Remove-Item dist -Recurse -Force
}

python -m build
python -m twine check dist/*
python -m twine upload dist/*

Write-Host 'Uploaded to PyPI successfully.'
