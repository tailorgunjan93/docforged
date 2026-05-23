# run_eval.ps1 -- Full DocNest RAG evaluation: Gemini + Groq + judge comparison
# Run from repo root:  .\run_eval.ps1
# Requires: python in PATH, GOOGLE_API_KEY and GROQ_API_KEY in .env

Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"

$python = $null

# -- Check python --------------------------------------------------------------
foreach ($candidate in @("python", "python3", "python3.11",
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe",
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe",
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $python = $candidate; break
    }
}
if (-not $python) {
    Write-Host "ERROR: python not found. Activate your venv/conda or install Python." -ForegroundColor Red
    exit 1
}

$pyVer = & $python --version 2>&1
Write-Host ""
Write-Host "=== DocNest Full Eval Run ===" -ForegroundColor Cyan
Write-Host "Python : $pyVer"
Write-Host "Time   : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# -- RUN 1: Gemini 2.0 Flash ---------------------------------------------------
Write-Host "------------------------------------------------------" -ForegroundColor Yellow
Write-Host "RUN 1/3 -- Gemini 2.0 Flash  (run-id: v7_gemini)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------" -ForegroundColor Yellow
Write-Host ""

$t1 = Get-Date
& $python eval/rag_accuracy_eval.py --model gemini-2.0-flash --run-id v7_gemini $dur1 = [math]::Round(((Get-Date) - $t1).TotalMinutes, 1)
Write-Host ""
Write-Host "RUN 1 done in ${dur1} min" -ForegroundColor Green
Write-Host ""

# -- RUN 2: Groq llama-3.3-70b -------------------------------------------------
Write-Host "------------------------------------------------------" -ForegroundColor Yellow
Write-Host "RUN 2/3 -- Groq llama-3.3-70b  (run-id: v7_groq)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------" -ForegroundColor Yellow
Write-Host ""

$t2 = Get-Date
& $python eval/rag_accuracy_eval.py --model groq/llama-3.3-70b-versatile --run-id v7_groq $dur2 = [math]::Round(((Get-Date) - $t2).TotalMinutes, 1)
Write-Host ""
Write-Host "RUN 2 done in ${dur2} min" -ForegroundColor Green
Write-Host ""

# -- RUN 3: Judge both result sets and compare ---------------------------------
Write-Host "------------------------------------------------------" -ForegroundColor Yellow
Write-Host "RUN 3/3 -- Judging both result sets + comparison" -ForegroundColor Yellow
Write-Host "------------------------------------------------------" -ForegroundColor Yellow
Write-Host ""

$geminiAnswers = "eval/results/v7_gemini/answers_for_claude.json"
$groqAnswers   = "eval/results/v7_groq/answers_for_claude.json"

$stopWords = @("what","which","how","the","a","an","is","are","was","were","does","did","do",
               "in","on","at","to","for","of","and","or","by","with","from","this","that",
               "these","those","it","its","be","been","being","have","has","had","will",
               "would","could","should","may","might","must","shall","can","cannot","dont",
               "doesnt","report","describe","say","says","said","describes","according",
               "year","annual","global")

function Get-Nums($text) {
    $t = $text -replace ',',''
    [regex]::Matches($t, '\b\d[\d\.]*') | ForEach-Object { $_.Value }
}
function Is-Close($a, $b) {
    try {
        $va=[double]$a; $vb=[double]$b
        return ([Math]::Abs($va-$vb)/[Math]::Max([Math]::Abs($va),0.001)) -lt 0.06
    } catch { return $a -eq $b }
}
function Local-Judge($q, $cand, $ref) {
    $c = $cand.ToLower().Trim()
    $r = $ref.ToLower().Trim()
    if ($c.StartsWith("not found in context") -or $c.StartsWith("not found in the context")) {
        return 0
    }
    $rn  = @(Get-Nums $r); $cn = @(Get-Nums $c)
    $nh  = ($rn | Where-Object { $rv=$_; ($cn | Where-Object { Is-Close $rv $_ }) }).Count
    $nr  = if ($rn.Count -gt 0) { $nh/$rn.Count } else { 1.0 }
    $rw  = ($r -replace '[^a-z0-9]',' ').Split(' ') | Where-Object { $_ -notin $stopWords -and $_.Length -gt 2 }
    $cw  = ($c -replace '[^a-z0-9]',' ').Split(' ') | Where-Object { $_.Length -gt 0 }
    $kr  = if ($rw.Count -gt 0) { (($rw|Where-Object{$_ -in $cw}).Count)/$rw.Count } else { 0.0 }
    if ($nr -ge 0.75 -and $kr -ge 0.45) { return 10 }
    if ($rn.Count -eq 0 -and $kr -ge 0.60) { return 10 }
    if ($rn.Count -eq 0 -and $kr -ge 0.40) { return 9 }
    $cmb = 0.50*$nr + 0.30*$kr
    if ($cmb -ge 0.70){10} elseif($cmb -ge 0.55){9} elseif($cmb -ge 0.40){8} `
    elseif($cmb -ge 0.28){7} elseif($cmb -ge 0.18){6} elseif($cmb -ge 0.10){5} `
    elseif($cmb -ge 0.04){3} else{0}
}

function Score-Answers($jsonPath) {
    if (-not (Test-Path $jsonPath)) { return $null }
    $pairs = Get-Content $jsonPath -Raw | ConvertFrom-Json

    $byDoc = @{}; $all = @()
    foreach ($p in $pairs) {
        $s = Local-Judge $p.question $p.docnest_answer $p.expected_answer
        $all += $s
        if (-not $byDoc.ContainsKey($p.doc)) { $byDoc[$p.doc] = @() }
        $byDoc[$p.doc] += $s
    }
    return @{
        all    = $all
        byDoc  = $byDoc
        avg    = [math]::Round(($all | Measure-Object -Average).Average, 2)
        pass   = ($all | Where-Object { $_ -ge 7 }).Count
        total  = $all.Count
    }
}

$gR  = Score-Answers $geminiAnswers
$grR = Score-Answers $groqAnswers

# -- Print side-by-side comparison ---------------------------------------------
Write-Host ""
Write-Host "+============================================================+" -ForegroundColor Cyan
Write-Host "|          DOCNEST RAG EVAL -- FINAL RESULTS                 |" -ForegroundColor Cyan
Write-Host "+============================================================+" -ForegroundColor Cyan
Write-Host ("|  {0,-20} | {1,-18} | {2,-12} |" -f "Metric", "Gemini 2.0 Flash", "Groq 70B") -ForegroundColor Cyan
Write-Host "+============================================================+" -ForegroundColor Cyan

if ($gR -and $grR) {
    $gAvg  = $gR.avg;   $grAvg = $grR.avg
    $gP    = $gR.pass;  $grP   = $grR.pass
    $gT    = $gR.total; $grT   = $grR.total
    $gPct  = [math]::Round($gP/$gT*100)
    $grPct = [math]::Round($grP/$grT*100)
    Write-Host ("|  {0,-20} | {1,-18} | {2,-12} |" -f "Avg score", "$gAvg / 10", "$grAvg / 10") -ForegroundColor White
    Write-Host ("|  {0,-20} | {1,-18} | {2,-12} |" -f "Pass rate (>=7)", "$gP/$gT ($gPct%)", "$grP/$grT ($grPct%)") -ForegroundColor White
    Write-Host "+------------------------------------------------------------+" -ForegroundColor Cyan

    foreach ($doc in $gR.byDoc.Keys) {
        $gs   = $gR.byDoc[$doc]
        $gda  = [math]::Round(($gs|Measure-Object -Average).Average,1)
        $gdp  = ($gs|Where-Object{$_-ge 7}).Count
        $shortDoc = $doc.Substring(0,[Math]::Min(20,$doc.Length)).PadRight(20)

        if ($grR.byDoc.ContainsKey($doc)) {
            $grs  = $grR.byDoc[$doc]
            $grda = [math]::Round(($grs|Measure-Object -Average).Average,1)
            $grdp = ($grs|Where-Object{$_-ge 7}).Count
            Write-Host ("|  {0} | avg={1} pass={2}/{3}    | avg={4} pass={5}/{6} |" -f `
                $shortDoc, "$gda".PadRight(3), $gdp, $gs.Count, `
                "$grda".PadRight(3), $grdp, $grs.Count) -ForegroundColor White
        } else {
            Write-Host ("|  {0} | avg={1} pass={2}/{3}    | (no data)    |" -f `
                $shortDoc, "$gda".PadRight(3), $gdp, $gs.Count) -ForegroundColor White
        }
    }
    Write-Host "+============================================================+" -ForegroundColor Cyan
} elseif ($gR) {
    Write-Host "  Gemini only: avg=$($gR.avg)  pass=$($gR.pass)/$($gR.total)" -ForegroundColor White
    Write-Host "  Groq results not found." -ForegroundColor Yellow
    Write-Host "+============================================================+" -ForegroundColor Cyan
} elseif ($grR) {
    Write-Host "  Groq only: avg=$($grR.avg)  pass=$($grR.pass)/$($grR.total)" -ForegroundColor White
    Write-Host "  Gemini results not found." -ForegroundColor Yellow
    Write-Host "+============================================================+" -ForegroundColor Cyan
} else {
    Write-Host "  (Could not load one or both result sets)" -ForegroundColor Red
    Write-Host "+============================================================+" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Results written to:" -ForegroundColor Green
Write-Host "  eval/results/v7_gemini/live_results.md"
Write-Host "  eval/results/v7_groq/live_results.md"
Write-Host ""

$totalDur = [math]::Round($dur1 + $dur2, 1)
Write-Host "Total wall time: ${totalDur} min" -ForegroundColor Green
Write-Host "Run complete: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
