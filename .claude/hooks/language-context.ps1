$ErrorActionPreference = 'Stop'

$inputJson = [Console]::In.ReadToEnd()
try { $data = $inputJson | ConvertFrom-Json } catch { exit 0 }

$prompt = [string]$data.prompt

$isThai = $false
foreach ($ch in $prompt.ToCharArray()) {
    $code = [int][char]$ch
    if ($code -ge 0x0E00 -and $code -le 0x0E7F) {
        $isThai = $true
        break
    }
}

if ($isThai) {
    $lang = 'Thai'
} else {
    $lang = 'English'
}

$out = @{
    hookSpecificOutput = @{
        hookEventName = 'UserPromptSubmit'
        additionalContext = "Language check: the user's latest message appears to be written in $lang. Respond in $lang."
    }
}
$out | ConvertTo-Json -Depth 5 -Compress
