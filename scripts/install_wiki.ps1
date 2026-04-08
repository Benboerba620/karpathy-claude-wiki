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

    $marker = '## Protocol 1 — Ingest'
    $start = $TemplateText.IndexOf($marker)
    if ($start -lt 0) {
        throw "模板 CLAUDE.md 中未找到 '$marker'"
    }

    return $TemplateText.Substring($start).Trim()
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
    Write-Step "已写入 wiki 协议文件: $protocolPath"
}

function Merge-ClaudeMd {
    param(
        [string]$TemplatePath,
        [string]$TargetPath,
        [string]$WikiDirName
    )

    if (-not (Test-Path $TargetPath)) {
        Copy-Item $TemplatePath $TargetPath -Force
        Write-Step '已复制完整 CLAUDE.md 到目标项目根目录'
        return
    }

    $existing = Get-Content -Raw -Encoding UTF8 $TargetPath
    $sectionHeader = '## Wiki Protocols (karpathy-claude-wiki)'
    if ($existing.Contains($sectionHeader)) {
        Write-Step '目标项目已包含 wiki 轻量接入段，跳过 CLAUDE.md 追加'
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
    Write-Step '已向现有 CLAUDE.md 追加轻量 wiki 接入段'
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
        throw '未找到 entity 模板 profile.md'
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
    Write-Step "已创建首个 entity: $entityProfile"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$resolvedTargetDir = [System.IO.Path]::GetFullPath($TargetDir)
$resolvedRepoRoot = [System.IO.Path]::GetFullPath($repoRoot)

if ($resolvedTargetDir -eq $resolvedRepoRoot) {
    throw 'TargetDir 不能直接等于模板仓库本身，请传入你的项目目录。'
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

if (-not (Test-Path $sourceWiki)) { throw '未找到模板 wiki/ 目录' }
if (-not (Test-Path $sourceClaude)) { throw '未找到模板 CLAUDE.md' }
if (-not (Test-Path $sourceIndexScript)) { throw '未找到模板 scripts/wiki_index.py' }

if (Test-Path $targetWiki) {
    if (-not $Force) {
        throw "目标目录已存在 $targetWiki。若确认覆盖，请加 -Force。"
    }
    Remove-Item $targetWiki -Recurse -Force
}

Write-Step "复制 wiki 模板到 $targetWiki"
Copy-Item $sourceWiki $targetWiki -Recurse -Force

if (-not (Test-Path $targetScriptsDir)) {
    New-Item -ItemType Directory -Path $targetScriptsDir -Force | Out-Null
}
Copy-Item $sourceIndexScript $targetIndexScript -Force
Write-Step '已复制 scripts/wiki_index.py'

Write-ProtocolFile -TemplatePath $sourceClaude -WikiRoot $targetWiki -WikiDirName $WikiDirName
Merge-ClaudeMd -TemplatePath $sourceClaude -TargetPath $targetClaude -WikiDirName $WikiDirName
New-FirstEntity -WikiRoot $targetWiki -Name $EntityName

if (-not $SkipIndex) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        Write-Step '正在生成 wiki 索引'
        Push-Location $resolvedTargetDir
        try {
            & python .\scripts\wiki_index.py
            if ($LASTEXITCODE -ne 0) {
                throw 'wiki_index.py 执行失败'
            }
            & python .\scripts\wiki_index.py --lint
            if ($LASTEXITCODE -ne 0) {
                throw 'wiki lint 检查失败'
            }
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Warning '未检测到 python，已跳过 _index.json / overview.md 生成。安装 Python 后请手动运行: python scripts/wiki_index.py'
    }
}

$schemaPath = "$WikiDirName/_schema.md"
$protocolsPath = "$WikiDirName/_protocols.md"
Write-Host ''
Write-Host '安装完成。下一步：' -ForegroundColor Green
Write-Host "1. 把原始文件放进 $WikiDirName\raw\articles 或 papers 等目录" -ForegroundColor Green
Write-Host '2. 打开 Claude Code' -ForegroundColor Green
Write-Host "3. 对它说：读一下 '$schemaPath'、'$protocolsPath' 和 'CLAUDE.md'，然后按 ingest 协议把我刚放进去的文件摄入到 wiki 里。" -ForegroundColor Green
