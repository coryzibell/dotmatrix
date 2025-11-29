# Rodio ALSA Runtime Dependency Research

**Date:** 2025-11-29
**Question:** Does rodio need ALSA libraries at runtime on Linux, or just at compile time?

## Key Findings

### Architecture
1. **rodio** → **cpal** → **alsa-sys** → **libasound** (ALSA library)
2. rodio uses cpal for all platform audio I/O
3. On Linux, cpal uses ALSA backend via alsa-sys crate

### Runtime Dependency: YES

**libasound2 (ALSA library) is a RUNTIME dependency**, not just compile-time:

- **Build-time:** Requires `libasound2-dev` (Debian/Ubuntu) or `alsa-lib-devel` (Fedora)
- **Runtime:** Binary dynamically links against `libasound.so` and requires it present on system
- Can verify with: `ldd <binary>` or `readelf -d <binary> | grep NEEDED`

### Dynamic Linking Behavior

ALSA is **always dynamically linked** in standard builds because:
- ALSA library internally uses `dlopen()` to load plugins at runtime
- Even static linking attempts fail - ALSA tries to load `libasound_module_*.so` plugins dynamically
- This defeats static linking and requires plugin `.so` files at runtime

### Minimal System Impact

On a minimal Linux system **without libasound**:
- Binary will fail to start with "shared library not found" error
- No graceful fallback to null audio or other backends
- ALSA must be present on target system

### Workaround: Headless Build

Rodio CAN be built **without audio output** using:
```toml
[dependencies]
rodio = { version = "0.21.0", default-features = false, features = ["symphonia-all"] }
```

This excludes cpal/ALSA entirely - useful for:
- Decode/process audio without playback
- Environments where ALSA unavailable
- But: no audio playback capability

## Answer Summary

**Runtime dependency:** YES
**Type:** Dynamic library (`libasound.so`)
**Required on target:** libasound2 package (not -dev)
**Static linking:** Not practical due to ALSA plugin architecture

## Sources
- [rodio crates.io](https://crates.io/crates/rodio)
- [GitHub - RustAudio/rodio](https://github.com/RustAudio/rodio)
- [GitHub - RustAudio/cpal](https://github.com/RustAudio/cpal)
- [Stack Overflow - alsa-sys dependency](https://stackoverflow.com/questions/57727066/how-can-i-install-and-connect-the-alsa-pc-when-building-the-alsa-sys-crate-as)
- [ALSA static linking issues](https://alsa-user.narkive.com/Be4310jg/alsa-static-linking)
