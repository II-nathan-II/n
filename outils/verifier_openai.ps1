# Vérification OpenAI (lecture seule) — à lancer sur TON PC Windows.
# Ne génère aucune image, ne dépense aucun crédit, n'affiche jamais la clé.
# Usage (PowerShell) :  powershell -ExecutionPolicy Bypass -File .\verifier_openai.ps1

$ErrorActionPreference = 'Stop'
$sortie = Join-Path $PSScriptRoot 'resultat_openai.txt'
$log = New-Object System.Collections.Generic.List[string]
function Say($t) { Write-Host $t; $log.Add($t) }

Say "=== Vérification OpenAI (lecture seule) — $(Get-Date -Format 'yyyy-MM-dd HH:mm') ==="

# 1. Variable d'environnement (jamais affichée)
$key = $env:OPENAI_API_KEY
if (-not $key) { $key = [Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User') }
if (-not $key) { $key = [Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'Machine') }
if (-not $key) {
    Say "1) OPENAI_API_KEY : ABSENTE. Ouvre un NOUVEAU terminal (une variable créée après l'ouverture d'un terminal n'y est pas visible)."
    $log | Set-Content -Encoding UTF8 $sortie; exit 1
}
Say ("1) OPENAI_API_KEY : présente ({0} caractères, valeur non affichée)" -f $key.Length)

$headers = @{ Authorization = "Bearer $key" }

function Get-Api($url) {
    try {
        $r = Invoke-WebRequest -Uri $url -Headers $headers -Method GET -UseBasicParsing -TimeoutSec 30
        return @{ ok = $true; code = [int]$r.StatusCode; body = ($r.Content | ConvertFrom-Json) }
    } catch {
        $code = 0
        if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
        return @{ ok = $false; code = $code; err = $_.Exception.Message }
    }
}

# 2. GET /v1/models
$m = Get-Api 'https://api.openai.com/v1/models'
if (-not $m.ok) {
    $why = switch ($m.code) {
        401 { "clé refusée (invalide, révoquée ou mal copiée)" }
        403 { "accès refusé (projet/organisation non autorisé, ou région non prise en charge)" }
        429 { "trop de requêtes, ou quota/facturation à vérifier sur platform.openai.com" }
        0   { "aucune réponse : pare-feu, proxy ou antivirus qui bloque api.openai.com ?" }
        default { "erreur HTTP $($m.code)" }
    }
    Say "2) GET /v1/models : ECHEC — $why"
    $log | Set-Content -Encoding UTF8 $sortie; exit 2
}
$ids = @($m.body.data | ForEach-Object { $_.id } | Sort-Object)
Say "2) GET /v1/models : OK (HTTP $($m.code)) — $($ids.Count) modèles visibles avec cette clé"

# Texte
$texte = $ids | Where-Object { $_ -match '^(gpt|o\d)' -and $_ -notmatch 'image|audio|realtime|transcribe|tts|search|embedding' }
Say ("   Modèles de texte (extrait) : " + (($texte | Select-Object -First 15) -join ', '))

# 3. GPT Image 2
$images = $ids | Where-Object { $_ -match 'image|dall-e' }
Say ("3) Modèles d'image visibles : " + ($(if ($images) { $images -join ', ' } else { 'aucun' })))
if ($ids -contains 'gpt-image-2') {
    Say "   gpt-image-2 : DISPONIBLE pour ton compte"
} else {
    Say "   gpt-image-2 : NON visible pour ton compte (vérification d'organisation requise, ou modèle pas encore ouvert à ton niveau d'accès)"
}

# 4. Détails du modèle (toujours gratuit : simple lecture)
foreach ($id in @('gpt-image-2', 'gpt-image-1') | Where-Object { $ids -contains $_ }) {
    $d = Get-Api "https://api.openai.com/v1/models/$id"
    if ($d.ok) { Say ("4) Fiche {0} : propriétaire={1}, créé={2}" -f $id, $d.body.owned_by, [DateTimeOffset]::FromUnixTimeSeconds($d.body.created).ToString('yyyy-MM-dd')) }
}
Say "   Note : l'API ne publie NI les tailles/qualités d'image disponibles NI les prix. Ils sont dans la documentation OpenAI (page du modèle et page Pricing)."

Say "5) Aucune image générée, aucun crédit dépensé (seulement des requêtes GET en lecture)."
$log | Set-Content -Encoding UTF8 $sortie
Say "Résultat enregistré (sans la clé) dans : $sortie"
