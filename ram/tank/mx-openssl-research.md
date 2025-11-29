# mx OpenSSL Research

**Date:** 2025-11-29
**Target:** /home/w3surf/work/personal/code/mx

## Current State

### Dependency Chain
```
mx v0.1.13
└── reqwest v0.12.24 (features: ["json", "blocking"])
    └── (default-tls feature enabled by default)
        └── hyper-tls v0.6.0
            └── native-tls v0.2.14
                └── openssl v0.10.75
                    └── openssl-sys v0.9.111
```

**Root cause:** `reqwest` with default features enables `default-tls`, which uses `native-tls`, which requires system OpenSSL on Linux.

### Current Cargo.toml (line 46)
```toml
reqwest = { version = "0.12", features = ["json", "blocking"] }
```

## Solution: Two Options

### Option 1: Vendored OpenSSL (Bundle OpenSSL)
**Change to:**
```toml
reqwest = { version = "0.12", features = ["json", "blocking", "native-tls-vendored"] }
```

**Pros:**
- Minimal change - just add one feature flag
- Keeps using OpenSSL (battle-tested)
- Works across all platforms

**Cons:**
- Longer compile times (compiles OpenSSL from source)
- Larger binary size
- Still depends on C code (cross-compilation can be tricky)

### Option 2: Switch to rustls (Pure Rust TLS)
**Change to:**
```toml
reqwest = { version = "0.12", default-features = false, features = ["json", "blocking", "rustls-tls"] }
```

**Pros:**
- Pure Rust - no C dependencies
- Faster compile times (no OpenSSL build)
- Smaller binaries
- Better cross-compilation story
- Future-proof (reqwest considering making this default)

**Cons:**
- Different TLS implementation (though well-tested)
- May have edge cases with some TLS configurations

## Recommendation

**Use Option 2 (rustls)** unless there's a specific need for OpenSSL.

Rationale:
- mx is a CLI tool, not a library - we control the TLS implementation
- rustls is mature and widely used
- Eliminates system dependency issues entirely
- Aligns with Rust ecosystem direction

## Implementation

Change line 46 in `/home/w3surf/work/personal/code/mx/Cargo.toml` from:
```toml
reqwest = { version = "0.12", features = ["json", "blocking"] }
```

To either:
```toml
# Option 1: Vendored OpenSSL
reqwest = { version = "0.12", features = ["json", "blocking", "native-tls-vendored"] }

# Option 2: rustls (recommended)
reqwest = { version = "0.12", default-features = false, features = ["json", "blocking", "rustls-tls"] }
```

Then run:
```bash
cd /home/w3surf/work/personal/code/mx
cargo clean
cargo build --release
```

## Sources
- [reqwest GitHub](https://github.com/seanmonstar/reqwest)
- [reqwest Issue #377 - Support vendored feature](https://github.com/seanmonstar/reqwest/issues/377)
- [reqwest Issue #2025 - Consider switching to rustls](https://github.com/seanmonstar/reqwest/issues/2025)
- [reqwest docs.rs](https://docs.rs/reqwest/latest/reqwest/)
