# Jalankan pengambilan harga dari PC pemilik (Rencana Jaringan B, rencana 10.1).
#
# Contoh uji tanpa push:   powershell -NoProfile -ExecutionPolicy Bypass -File skrip\jadwal_harga.ps1
# Contoh dengan push:      ... -File skrip\jadwal_harga.ps1 -Dorong
# Daftarkan tugas (tiap 3 jam, saat PC menyala; ganti path sesuai folder repo):
#   schtasks /Create /TN DasborHarga /SC HOURLY /MO 3 /TR "powershell -NoProfile -ExecutionPolicy Bypass -File C:\...\dasbor_sukoharjo\skrip\jadwal_harga.ps1 -Dorong"
# Di Task Scheduler (GUI), centang "Run task as soon as possible after a scheduled start is missed".
param(
    [string]$Cabang = "main",
    [switch]$Dorong
)

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
New-Item -ItemType Directory -Force -Path "_tmp" | Out-Null
$log = Join-Path $repo "_tmp\jadwal_harga.log"

function Catat([string]$pesan) {
    $baris = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $pesan
    Add-Content -Path $log -Value $baris -Encoding UTF8
    Write-Output $baris
}

if ($Dorong) {
    git pull --rebase --autostash origin $Cabang | Out-Null
    if ($LASTEXITCODE -ne 0) { Catat "GAGAL git pull"; exit 1 }
}

python skrip/ambil_harga.py | ForEach-Object { Catat $_ }
if ($LASTEXITCODE -ne 0) { Catat "ambil_harga.py gagal, data lama dipertahankan"; exit 1 }

if ($Dorong) {
    # status.json di-ignore git (dibangun ulang saat deploy), jadi tidak ikut di-add.
    git add hasil/situs/data/harga.json hasil/situs/data/harga_riwayat.json
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -m ("data: harga " + (Get-Date -Format "yyyy-MM-dd")) | Out-Null
        git push origin $Cabang | Out-Null
        if ($LASTEXITCODE -ne 0) { Catat "GAGAL git push"; exit 1 }
        Catat "data terdorong ke $Cabang"
    } else {
        Catat "tidak ada perubahan"
    }
}
