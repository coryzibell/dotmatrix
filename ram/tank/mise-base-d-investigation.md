# mise base-d Version Investigation

## Summary

**Issue:** mise warning about old base-d version (0.1.85) when working in `/home/w3surf/work/personal/code/base-d/`

**Root Cause:** Version mismatch between global mise config and local project config

## Details

### Global Configuration
- **Location:** `/home/w3surf/.config/mise/config.toml`
- **base-d version:** `0.2.2` (latest)
- **Installed at:** `/home/w3surf/.local/share/mise/installs/cargo-base-d/0.2.2/bin/base-d`

### Local Project Configuration
- **Location:** `/home/w3surf/work/personal/code/base-d/mise.toml`
- **base-d version:** `0.1.85` (pinned old version)
- **Status:** Not installed initially, automatically installed when accessed

### What Happened

1. Global mise config specifies `cargo:base-d = "latest"` (0.2.2)
2. Local project has `mise.toml` specifying `cargo:base-d = "0.1.85"`
3. When working in the project directory, mise detects the local config takes precedence
4. Version 0.1.85 was not installed, triggering the warning
5. mise automatically installed 0.1.85 from source (compiled via cargo)

### Mise Behavior

mise uses directory-specific configurations:
- Outside project: uses global config → base-d 0.2.2
- Inside `/home/w3surf/work/personal/code/base-d/`: uses local config → base-d 0.1.85

## Why This Exists

The base-d project is likely pinning to version 0.1.85 for development purposes:
- Testing compatibility
- Regression testing
- Maintaining specific version for development/testing

## Resolution Options

1. **Keep as-is** - Warning appears but both versions work correctly (different contexts)
2. **Update local mise.toml** - Change version to "latest" or "0.2.2"
3. **Remove local mise.toml** - Let project use global config
4. **Accept the old version** - If testing against 0.1.85 is intentional

## Files

- Global config: `/home/w3surf/.config/mise/config.toml`
- Local config: `/home/w3surf/work/personal/code/base-d/mise.toml`
- Version 0.2.2 binary: `/home/w3surf/.local/share/mise/installs/cargo-base-d/0.2.2/bin/base-d`
- Version 0.1.85 binary: `/home/w3surf/.local/share/mise/installs/cargo-base-d/0.1.85/bin/base-d`
