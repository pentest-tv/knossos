# Run ONCE on a Windows Docker host that can reach Docker Hub. Pulls each image,
# reads its repo digest, and writes pinned refs into .env. Commit the resulting .env.
#   powershell -ExecutionPolicy Bypass -File scripts\pin-digests.ps1
$ErrorActionPreference = "Stop"

$tags = [ordered]@{
  TARGET_IMAGE = "tleemcjr/metasploitable2:latest"
  DVWA_IMAGE   = "vulnerables/web-dvwa:latest"
  JUICE_IMAGE  = "bkimminich/juice-shop:latest"
  GOPHISH_IMAGE = "gophish/gophish:latest"
  MAILHOG_IMAGE = "mailhog/mailhog:latest"
  BIND_IMAGE   = "internetsystemsconsortium/bind9:9.20"
  PYTHON_IMAGE = "python:3.12-slim"
  BASE_DEBIAN  = "debian:stable-slim"
  BASE_KALI    = "kalilinux/kali-rolling:latest"
}

$envFile = ".env"
if (-not (Test-Path $envFile)) { Copy-Item ".env.example" $envFile }
$lines = Get-Content $envFile

foreach ($var in $tags.Keys) {
  $tag = $tags[$var]
  Write-Host "pulling $tag ..."
  docker pull $tag | Out-Null
  $pinned = docker inspect --format '{{index .RepoDigests 0}}' $tag
  if ([string]::IsNullOrWhiteSpace($pinned)) { throw "no repo digest for $tag" }
  Write-Host "  $var=$pinned"
  if ($lines -match "^$var=") {
    $lines = $lines -replace "^$var=.*", "$var=$pinned"
  } else {
    $lines += "$var=$pinned"
  }
}

Set-Content -Path $envFile -Value $lines
Write-Host "Done. Pinned digests written to $envFile. Commit it."
