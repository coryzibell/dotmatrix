# Release Infrastructure Reconnaissance - 2025-12-01

## Mission: Determine current release setup for base-d and mx

### Findings

#### 1. cargo-dist Status
**No dist.toml found in either repository.**
- Checked: `/home/w3surf/work/personal/code/base-d/`
- Checked: `/home/w3surf/work/personal/code/mx/`
- **Conclusion:** No cargo-dist integration at all currently.

#### 2. Release Workflow Analysis
Source: `/home/w3surf/work/personal/code/nebuchadnezzar/.github/workflows/follow-the-white-rabbit.yml`

**Current Release Generator:**
- GitHub CLI (`gh release create`) with `--generate-notes` flag
- This uses GitHub's automatic release notes based on PR titles and commits
- No custom templating or formatting

**Process:**
1. Builds 9 platform targets (Linux gnu/musl, FreeBSD, Windows, macOS - x86_64 and aarch64)
2. Packages as `.tar.gz` (Unix) or `.zip` (Windows)
3. Uploads artifacts
4. Creates release with: `gh release create "$VERSION" --title "Release $VERSION" --generate-notes`
5. Attaches all build artifacts

**Asset naming convention:**
- `{binary-name}-{os}-{arch}[.tar.gz|.zip]`
- Examples: `base-d-linux-x86_64.tar.gz`, `mx-windows-x86_64.zip`

#### 3. Current Release Notes Format
**Example from base-d v3.0.0:**
```markdown
## What's Changed
* Refactor CLI to subcommand pattern by @coryzibell in https://github.com/coryzibell/base-d/pull/123

**Full Changelog**: https://github.com/coryzibell/base-d/compare/v2.0.13...v3.0.0
```

**Example from mx v0.1.24:**
```markdown
## What's Changed
* Dependency cleanup and Edition 2024 migration by @coryzibell in https://github.com/coryzibell/mx/pull/48

**Full Changelog**: https://github.com/coryzibell/mx/compare/v0.1.23...v0.1.24
```

**Characteristics:**
- Simple PR list
- No installation instructions
- No download links table
- No checksums
- No installer scripts

#### 4. Release Assets
Both repos release 9 platform binaries:
- FreeBSD x86_64
- Linux aarch64 (gnu and musl)
- Linux x86_64 (gnu and musl)
- macOS aarch64 and x86_64
- Windows aarch64 and x86_64

No checksums, signatures, or installer scripts included.

### Answers to Neo's Questions

**Q: What's generating the release notes right now?**
A: GitHub's built-in `--generate-notes` feature. Zero custom formatting.

**Q: Is there any cargo-dist involvement at all?**
A: None. No dist.toml, no cargo-dist workflow integration.

**Q: Where would we add a download table?**
A: Options:
1. **Custom release notes template** - Create `.github/release.yml` to customize the generated notes
2. **Post-processing script** - Script that runs after `gh release create` to append download table
3. **cargo-dist integration** - Full replacement with cargo-dist (generates nice tables by default)
4. **Manual edit** - One-time manual addition (not sustainable)

### Recommendation Path

For adding download tables without full cargo-dist migration:

**Option A - Minimal (Template):**
Add `.github/release.yml` to customize GitHub's auto-generated notes.

**Option B - Script Enhancement:**
Modify `follow-the-white-rabbit.yml` to:
1. Generate release with notes
2. Calculate checksums for artifacts
3. Append formatted download table to release body
4. Update release via `gh release edit`

**Option C - Full cargo-dist:**
Initialize cargo-dist, which automatically generates:
- Professional release notes
- Download tables with checksums
- Installer scripts
- Platform-specific instructions

### Next Steps

Awaiting direction on which path to follow.

---
Tank out.
