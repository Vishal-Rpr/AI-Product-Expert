# Compile both living CVs with Tectonic (source files stay pdflatex-compatible).
$root = Split-Path -Parent $PSScriptRoot
if (-not $root) { $root = "C:\Users\user\Desktop\AI Product Expert\Knowledge\CV" }
$tectonic = Join-Path $root ".tools\tectonic.exe"
$env:FONTCONFIG_FILE = Join-Path $root ".tools\fonts.conf"

function Compile-Cv($src) {
  $outdir = Split-Path -Parent $src
  $tmp = Join-Path $outdir "_compile.tex"
  (Get-Content $src -Raw) -replace '\\input\{glyphtounicode\}', '% \input{glyphtounicode}' -replace '\\pdfgentounicode=1', '% \pdfgentounicode=1' | Set-Content -Encoding UTF8 $tmp
  & $tectonic --keep-logs --outdir $outdir $tmp
  $base = [IO.Path]::GetFileNameWithoutExtension($src)
  $pdfTmp = Join-Path $outdir "_compile.pdf"
  $pdfOut = Join-Path $outdir "$base.pdf"
  if (Test-Path $pdfTmp) { Move-Item -Force $pdfTmp $pdfOut }
  Remove-Item -Force $tmp, (Join-Path $outdir "_compile.log") -ErrorAction SilentlyContinue
}

Compile-Cv (Join-Path $root "SPM\Vishal_Prabhakar_SPM.tex")
Compile-Cv (Join-Path $root "AI_PM\Vishal_Prabhakar_AI_PM.tex")
