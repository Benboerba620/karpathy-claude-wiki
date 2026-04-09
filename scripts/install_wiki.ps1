[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetDir,

    [string]$WikiDirName = 'wiki',

    [string]$EntityName = '',

    [switch]$Force,

    [switch]$SkipIndex
)

$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[karpathy-claude-wiki] $Message" -ForegroundColor Cyan
}

function Write-Utf8File {
    param(
        [string]$Path,
        [string]$Content,
        [bool]$WithBom = $false
    )

    $encoding = New-Object System.Text.UTF8Encoding($WithBom)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Get-ProtocolBody {
    param([string]$TemplateText)

    $match = [regex]::Match($TemplateText, '(?ms)^## Protocol 1 .*')
    if (-not $match.Success) {
        throw 'Could not find Protocol 1 block in template CLAUDE.md'
    }

    return $match.Value.Trim()
}

function Write-ProtocolFile {
    param(
        [string]$TemplatePath,
        [string]$WikiRoot,
        [string]$WikiDirName
    )

    $template = Get-Content -Raw -Encoding UTF8 $TemplatePath
    $body = Get-ProtocolBody -TemplateText $template
    $protocolPath = Join-Path $WikiRoot '_protocols.md'
    $today = Get-Date -Format 'yyyy-MM-dd'
    $schemaPath = "$WikiDirName/_schema.md"

    $content = @"
---
title: Wiki Protocols
type: meta
created: $today
updated: $today
---

# Wiki Protocols

> Installed from karpathy-claude-wiki. Read this together with $schemaPath whenever working with the wiki.

$body
"@

    Write-Utf8File -Path $protocolPath -Content ($content.Trim() + "`r`n")
    Write-Step "Wrote wiki protocol file: $protocolPath"
}

function Merge-ClaudeMd {
    param(
        [string]$TemplatePath,
        [string]$TargetPath,
        [string]$WikiDirName
    )

    if (-not (Test-Path $TargetPath)) {
        Copy-Item $TemplatePath $TargetPath -Force
        Write-Step 'Copied full CLAUDE.md to target project root'
        return
    }

    $existing = Get-Content -Raw -Encoding UTF8 $TargetPath
    $sectionHeader = '## Wiki Protocols (karpathy-claude-wiki)'
    if ($existing.Contains($sectionHeader)) {
        Write-Step 'Target project already contains the lightweight wiki section; skipping append'
        return
    }

    $schemaPath = "$WikiDirName/_schema.md"
    $protocolsPath = "$WikiDirName/_protocols.md"
    $lightweightSection = @"
## Wiki Protocols (karpathy-claude-wiki)

When working with $WikiDirName/, first read:
- $schemaPath
- $protocolsPath

Use those files for ingest, cross-reference, contradiction scan, crystallization, and periodic wiki maintenance.
If the wiki protocol conflicts with project-specific instructions above, surface the conflict and ask the user which rule should win.
"@

    $merged = $existing.TrimEnd() + "`r`n`r`n" + $lightweightSection.Trim() + "`r`n"
    Write-Utf8File -Path $TargetPath -Content $merged
    Write-Step 'Appended lightweight wiki integration to existing CLAUDE.md'
}

function New-FirstEntity {
    param(
        [string]$WikiRoot,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Name)) {
        return
    }

    $templatePath = Join-Path $WikiRoot 'entities\_template\profile.md'
    if (-not (Test-Path $templatePath)) {
        throw 'Entity template profile.md was not found'
    }

    $entityDir = Join-Path $WikiRoot (Join-Path 'entities' $Name)
    $entityProfile = Join-Path $entityDir 'profile.md'
    $today = Get-Date -Format 'yyyy-MM-dd'

    if (-not (Test-Path $entityDir)) {
        New-Item -ItemType Directory -Path $entityDir -Force | Out-Null
    }

    $content = Get-Content -Raw -Encoding UTF8 $templatePath
    $content = $content.Replace('<Entity name>', $Name)
    $content = $content.Replace('YYYY-MM-DD', $today)
    $content = $content.Replace('| Started tracking | YYYY-MM-DD |', "| Started tracking | $today |")
    $content = $content.Replace('- Related entities: [[entity1]], [[entity2]]', '- Related entities:')
    $content = $content.Replace('- Related concepts: [[concept1]], [[concept2]]', '- Related concepts:')
    $content = $content.Replace('- Related sources: [[sources/source1]], [[sources/source2]]', '- Related sources:')
    $content = $content.Replace('- Variable 1 — why it matters, how to measure', '- ')
    $content = $content.Replace('- Variable 2 — why it matters, how to measure', '- ')
    $content = $content.Replace('- Variable 3 — why it matters, how to measure', '- ')
    $content = $content.Replace('- (questions you haven''t answered yet)', '- ')

    Write-Utf8File -Path $entityProfile -Content $content
    Write-Step "Created first entity: $entityProfile"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$resolvedTargetDir = [System.IO.Path]::GetFullPath($TargetDir)
$resolvedRepoRoot = [System.IO.Path]::GetFullPath($repoRoot)

if ($resolvedTargetDir -eq $resolvedRepoRoot) {
    throw 'TargetDir cannot be the template repository itself. Pass your own project directory.'
}

if (-not (Test-Path $resolvedTargetDir)) {
    New-Item -ItemType Directory -Path $resolvedTargetDir -Force | Out-Null
}

$sourceWiki = Join-Path $repoRoot 'wiki'
$sourceClaude = Join-Path $repoRoot 'CLAUDE.md'
$sourceIndexScript = Join-Path $repoRoot 'scripts\wiki_index.py'
$targetWiki = Join-Path $resolvedTargetDir $WikiDirName
$targetScriptsDir = Join-Path $resolvedTargetDir 'scripts'
$targetIndexScript = Join-Path $targetScriptsDir 'wiki_index.py'
$targetClaude = Join-Path $resolvedTargetDir 'CLAUDE.md'

if (-not (Test-Path $sourceWiki)) { throw 'Template wiki/ directory was not found' }
if (-not (Test-Path $sourceClaude)) { throw 'Template CLAUDE.md was not found' }
if (-not (Test-Path $sourceIndexScript)) { throw 'Template scripts/wiki_index.py was not found' }

if (Test-Path $targetWiki) {
    if (-not $Force) {
        throw "Target wiki directory already exists at $targetWiki. Pass -Force to overwrite it."
    }
    Remove-Item $targetWiki -Recurse -Force
}

Write-Step "Copying wiki template to $targetWiki"
Copy-Item $sourceWiki $targetWiki -Recurse -Force

if (-not (Test-Path $targetScriptsDir)) {
    New-Item -ItemType Directory -Path $targetScriptsDir -Force | Out-Null
}
Copy-Item $sourceIndexScript $targetIndexScript -Force
Write-Step 'Copied scripts/wiki_index.py'

Write-ProtocolFile -TemplatePath $sourceClaude -WikiRoot $targetWiki -WikiDirName $WikiDirName
Merge-ClaudeMd -TemplatePath $sourceClaude -TargetPath $targetClaude -WikiDirName $WikiDirName
New-FirstEntity -WikiRoot $targetWiki -Name $EntityName

if (-not $SkipIndex) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        Write-Step 'Generating wiki index'
        Push-Location $resolvedTargetDir
        try {
            try {
                & $python.Source .\scripts\wiki_index.py
                if ($LASTEXITCODE -ne 0) {
                    throw 'wiki_index.py failed'
                }

                & $python.Source .\scripts\wiki_index.py --lint
                if ($LASTEXITCODE -ne 0) {
                    throw 'wiki lint failed'
                }
            }
            catch {
                Write-Warning "python was detected, but index generation or lint failed. Installation still completed. Run 'python scripts/wiki_index.py' and 'python scripts/wiki_index.py --lint' later. Details: $($_.Exception.Message)"
            }
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Warning "python was not detected; skipped _index.json / overview.md generation. Installation still completed. Run 'python scripts/wiki_index.py' later after Python is available."
    }
}

$schemaPath = "$WikiDirName/_schema.md"
$protocolsPath = "$WikiDirName/_protocols.md"
Write-Host ''
Write-Host 'Installation complete. Next steps:' -ForegroundColor Green
Write-Host "1. Drop source files into $WikiDirName\raw\articles or papers and other raw folders" -ForegroundColor Green
Write-Host '2. Open Claude Code' -ForegroundColor Green
Write-Host "3. Tell it: read '$schemaPath', '$protocolsPath', and 'CLAUDE.md', then ingest the file I just dropped following the protocol." -ForegroundColor Green
