[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetDir,

    [string]$WikiDirName = 'wiki',

    [string]$Language = 'zh-CN',

    [string]$EntityName = '',

    [switch]$Force,

    [switch]$SkipIndex,

    [Alias('IncludeIngestHelper')]
    [switch]$WithIngestHelper
)

$ErrorActionPreference = 'Stop'

function Normalize-Language {
    param([string]$Value)

    switch -Regex ($Value.Trim().ToLowerInvariant()) {
        '^(zh|zh-cn|zh-hans|cn)$' { return 'zh-CN' }
        '^(en|en-us|en-gb)$' { return 'en' }
        default { throw "Unsupported language '$Value'. Use zh-CN or en." }
    }
}

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

function Get-UsablePythonCommand {
    $candidates = @(
        @{ Name = 'py'; VersionArgs = @('--version'); PrefixArgs = @('-3'); DisplayName = 'py -3' },
        @{ Name = 'python'; VersionArgs = @('--version'); PrefixArgs = @(); DisplayName = 'python' },
        @{ Name = 'python3'; VersionArgs = @('--version'); PrefixArgs = @(); DisplayName = 'python3' }
    )

    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Name -ErrorAction SilentlyContinue
        if (-not $command -or -not $command.Source) {
            continue
        }

        try {
            $versionOutput = & $command.Source @($candidate.VersionArgs) 2>&1 | Out-String
            if ($LASTEXITCODE -ne 0) {
                continue
            }
            if ($versionOutput -notmatch 'Python\s+3(\.\d+)+') {
                continue
            }

            return [pscustomobject]@{
                Path = $command.Source
                PrefixArgs = $candidate.PrefixArgs
                DisplayName = $candidate.DisplayName
            }
        }
        catch {
            continue
        }
    }

    return $null
}

function Get-ProtocolBody {
    param([string]$TemplateText)

    $match = [regex]::Match($TemplateText, '(?ms)^## Protocol 1 .*')
    if (-not $match.Success) {
        throw 'Could not find Protocol 1 block in template CLAUDE.md'
    }

    return $match.Value.Trim()
}

function Get-LocaleOverridePath {
    param(
        [string]$RepoRoot,
        [string]$Language,
        [string]$RelativePath
    )

    if ($Language -eq 'zh-CN') {
        return (Join-Path $RepoRoot $RelativePath)
    }

    $overridePath = Join-Path $RepoRoot (Join-Path (Join-Path 'locales' $Language) $RelativePath)
    if (Test-Path $overridePath) {
        return $overridePath
    }

    return (Join-Path $RepoRoot $RelativePath)
}

function Apply-WikiLocaleOverrides {
    param(
        [string]$RepoRoot,
        [string]$Language,
        [string]$TargetWiki
    )

    if ($Language -eq 'zh-CN') {
        return
    }

    $localeWikiRoot = Join-Path $RepoRoot (Join-Path (Join-Path 'locales' $Language) 'wiki')
    if (-not (Test-Path $localeWikiRoot)) {
        throw "Locale wiki overrides were not found for language '$Language'."
    }

    Get-ChildItem $localeWikiRoot -Force | ForEach-Object {
        Copy-Item $_.FullName $TargetWiki -Recurse -Force
    }

    Write-Step "Applied wiki locale overrides: $Language"
}

function Get-LocaleSettings {
    param(
        [string]$Language,
        [string]$WikiDirName
    )

    $schemaPath = "$WikiDirName/_schema.md"
    $protocolsPath = "$WikiDirName/_protocols.md"

    return [pscustomobject]@{
        ProtocolTitle = 'Wiki Protocols'
        ProtocolHeading = '# Wiki Protocols'
        ProtocolIntro = "> Installed from karpathy-claude-wiki. Read this together with $schemaPath whenever working with the wiki."
        LightweightHeader = '## Wiki Protocols (karpathy-claude-wiki)'
        LightweightLines = @(
            "When working with $WikiDirName/, first read:",
            "- $schemaPath",
            "- $protocolsPath",
            '',
            'Use those files for ingest, cross-reference, contradiction scan, crystallization, and periodic wiki maintenance.',
            'If the wiki protocol conflicts with project-specific instructions above, surface the conflict and ask the user which rule should win.'
        )
        CompletionTitle = 'Installation complete. Next steps:'
        CompletionSteps = @(
            "1. Drop a source file into $WikiDirName\raw\",
            '2. Open Claude Code',
            "3. Tell it: read '$schemaPath', '$protocolsPath', and 'CLAUDE.md', then ingest the file I just dropped following the protocol.",
            "4. Optional: if you use Obsidian Clippings, ask the agent to scan it with 'python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings' first."
        )
    }
}

function Write-ProtocolFile {
    param(
        [string]$TemplatePath,
        [string]$WikiRoot,
        [string]$WikiDirName,
        [string]$Language
    )

    $template = Get-Content -Raw -Encoding UTF8 $TemplatePath
    $body = Get-ProtocolBody -TemplateText $template
    $protocolPath = Join-Path $WikiRoot '_protocols.md'
    $today = Get-Date -Format 'yyyy-MM-dd'
    $settings = Get-LocaleSettings -Language $Language -WikiDirName $WikiDirName

    $content = @(
        '---',
        "title: $($settings.ProtocolTitle)",
        'type: meta',
        "created: $today",
        "updated: $today",
        '---',
        '',
        $settings.ProtocolHeading,
        '',
        $settings.ProtocolIntro,
        '',
        $body
    ) -join "`r`n"

    Write-Utf8File -Path $protocolPath -Content ($content.Trim() + "`r`n")
    Write-Step "Wrote wiki protocol file: $protocolPath"
}

function Merge-ClaudeMd {
    param(
        [string]$TemplatePath,
        [string]$TargetPath,
        [string]$WikiDirName,
        [string]$Language
    )

    $settings = Get-LocaleSettings -Language $Language -WikiDirName $WikiDirName

    if (-not (Test-Path $TargetPath)) {
        Copy-Item $TemplatePath $TargetPath -Force
        Write-Step 'Copied full CLAUDE.md to target project root'
        return
    }

    $existing = Get-Content -Raw -Encoding UTF8 $TargetPath
    if ($existing.Contains($settings.LightweightHeader)) {
        Write-Step 'Target project already contains the lightweight wiki section; skipping append'
        return
    }

    $lightweightSection = @(
        $settings.LightweightHeader,
        '',
        ($settings.LightweightLines -join "`r`n")
    ) -join "`r`n"

    $merged = $existing.TrimEnd() + "`r`n`r`n" + $lightweightSection + "`r`n"
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

function Normalize-CopiedWiki {
    param([string]$WikiRoot)

    foreach ($generatedName in @('_index.json', 'overview.md', '_attention.md')) {
        $generatedPath = Join-Path $WikiRoot $generatedName
        if (Test-Path $generatedPath) {
            Remove-Item $generatedPath -Force
        }
    }

    $rawRoot = Join-Path $WikiRoot 'raw'
    if (-not (Test-Path $rawRoot)) {
        return
    }

    Get-ChildItem $rawRoot -Force | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
    }

    $gitkeepPath = Join-Path $rawRoot '.gitkeep'
    if (-not (Test-Path $gitkeepPath)) {
        New-Item -ItemType File -Path $gitkeepPath -Force | Out-Null
    }

    Write-Step 'Removed generated files and non-template raw materials from copied wiki/'
}

$Language = Normalize-Language -Value $Language
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
$sourceClaude = Get-LocaleOverridePath -RepoRoot $repoRoot -Language $Language -RelativePath 'CLAUDE.md'
$sourceIndexScript = Join-Path $repoRoot 'scripts\wiki_index.py'
$sourceIngestHelper = Join-Path $repoRoot 'scripts\ingest_helper.py'
$sourceIngestSkillDir = Join-Path $repoRoot 'skills\wiki-ingest'
$sourceEnvExample = Join-Path $repoRoot '.env.example'
$targetWiki = Join-Path $resolvedTargetDir $WikiDirName
$targetScriptsDir = Join-Path $resolvedTargetDir 'scripts'
$targetSkillsDir = Join-Path $resolvedTargetDir 'skills'
$targetIndexScript = Join-Path $targetScriptsDir 'wiki_index.py'
$targetIngestHelper = Join-Path $targetScriptsDir 'ingest_helper.py'
$targetIngestSkillDir = Join-Path $targetSkillsDir 'wiki-ingest'
$targetClaude = Join-Path $resolvedTargetDir 'CLAUDE.md'
$targetEnvExample = Join-Path $resolvedTargetDir '.env.example'

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
Apply-WikiLocaleOverrides -RepoRoot $repoRoot -Language $Language -TargetWiki $targetWiki
Normalize-CopiedWiki -WikiRoot $targetWiki

if (-not (Test-Path $targetScriptsDir)) {
    New-Item -ItemType Directory -Path $targetScriptsDir -Force | Out-Null
}

Copy-Item $sourceIndexScript $targetIndexScript -Force
Write-Step 'Copied scripts/wiki_index.py'

if (Test-Path $sourceIngestSkillDir) {
    if (-not (Test-Path $targetSkillsDir)) {
        New-Item -ItemType Directory -Path $targetSkillsDir -Force | Out-Null
    }
    if (Test-Path $targetIngestSkillDir) {
        Remove-Item $targetIngestSkillDir -Recurse -Force
    }
    Copy-Item $sourceIngestSkillDir $targetIngestSkillDir -Recurse -Force
    Write-Step 'Copied skills/wiki-ingest'
}

if ($WithIngestHelper) {
    if (-not (Test-Path $sourceIngestHelper)) { throw 'Template scripts/ingest_helper.py was not found' }
    if (-not (Test-Path $sourceEnvExample)) { throw 'Template .env.example was not found' }

    Copy-Item $sourceIngestHelper $targetIngestHelper -Force
    Copy-Item $sourceEnvExample $targetEnvExample -Force
    Write-Step 'Copied scripts/ingest_helper.py and .env.example'
}

Write-ProtocolFile -TemplatePath $sourceClaude -WikiRoot $targetWiki -WikiDirName $WikiDirName -Language $Language
Merge-ClaudeMd -TemplatePath $sourceClaude -TargetPath $targetClaude -WikiDirName $WikiDirName -Language $Language
New-FirstEntity -WikiRoot $targetWiki -Name $EntityName

if (-not $SkipIndex) {
    $python = Get-UsablePythonCommand
    if ($python) {
        Write-Step 'Generating wiki index'
        Push-Location $resolvedTargetDir
        try {
            try {
                $indexArgs = @($python.PrefixArgs + @('.\scripts\wiki_index.py'))
                $lintArgs = @($python.PrefixArgs + @('.\scripts\wiki_index.py', '--lint'))

                & $python.Path @indexArgs
                if ($LASTEXITCODE -ne 0) {
                    throw 'wiki_index.py failed'
                }

                & $python.Path @lintArgs
                if ($LASTEXITCODE -ne 0) {
                    throw 'wiki lint failed'
                }
            }
            catch {
                Write-Warning "$($python.DisplayName) was detected, but index generation or lint failed. Installation still completed. Run '$($python.DisplayName) scripts/wiki_index.py' and '$($python.DisplayName) scripts/wiki_index.py --lint' later. Details: $($_.Exception.Message)"
            }
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Warning "No usable Python 3 interpreter was detected; skipped _index.json / overview.md generation. Installation still completed. On Windows, the Microsoft Store 'python.exe' alias does not count. Run 'py -3 scripts/wiki_index.py' or 'python scripts/wiki_index.py' later after Python is installed."
    }
}

$completion = Get-LocaleSettings -Language $Language -WikiDirName $WikiDirName
Write-Host ''
Write-Host $completion.CompletionTitle -ForegroundColor Green
$completion.CompletionSteps | ForEach-Object { Write-Host $_ -ForegroundColor Green }
