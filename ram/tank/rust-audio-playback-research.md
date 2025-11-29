# Rust Terminal Audio Playback Research

Research conducted: 2025-11-29

## Research Question
Is there a way to play audio from the terminal natively in Rust? Looking for Rust crates or fallback to external programs.

---

## Native Rust Audio Crates

### 1. **rodio** (Most Popular & Recommended)
- **Status**: Most widely-used audio playback crate (5.3M total downloads, 844.3K recent)
- **Cross-platform**: Yes (via cpal library)
- **Formats**: MP3 (minimp3), WAV (hound), Vorbis (lewton), FLAC (claxon), or all via Symphonia
- **Complexity**: High-level, simple API - can play audio in just a few lines of code
- **Backend**: Uses cpal for cross-platform audio I/O
- **Threading**: Spawns background thread for playback, handles mixing automatically
- **CLI-friendly**: Yes - simple and straightforward for terminal use

**Cross-compilation note**: Depends on alsa library on Linux (libasound & libasound-dev), which can complicate cross-compiling

**crates.io**: https://crates.io/crates/rodio
**GitHub**: https://github.com/RustAudio/rodio
**Docs**: https://docs.rs/rodio

### 2. **soloud** (Alternative - C++ bindings)
- **Status**: Cross-platform Rust bindings for SoLoud C++ audio engine
- **Cross-platform**: Yes (miniaudio backend by default)
- **Formats**: WAV, MP3, OGG, FLAC + speech synthesis
- **Complexity**: Mid-level, requires C++ compiler and CMake to build
- **Backend**: Configurable (miniaudio default, ALSA, etc.)
- **CLI-friendly**: Yes, but heavier build dependencies

**Build requirements**: Rust compiler, C++ compiler, Cargo, CMake, git (Ninja recommended)

**crates.io**: https://crates.io/crates/soloud
**GitHub**: https://github.com/MoAlyousef/soloud-rs
**Docs**: https://docs.rs/soloud

### 3. **rusty_audio** (Wrapper)
- **Status**: "Fun and easy" 4-track audio system built on rodio
- **Cross-platform**: macOS, Windows, iOS out of box; Linux requires extra deps
- **Formats**: MP3, WAV, Vorbis, FLAC
- **Complexity**: Very simple, aimed at small projects
- **CLI-friendly**: Yes - simplified rodio interface

**Note**: Uses rodio under the hood, so consider using rodio directly for more control

**crates.io**: https://crates.io/crates/rusty_audio

### 4. Low-level Options

**cpal**
- Low-level cross-platform audio I/O library in pure Rust
- Used by rodio under the hood
- More control but more complexity
- Good if you need fine-grained audio device/stream management

**rust-portaudio**
- Bindings for the PortAudio library
- Cross-platform support
- Similar complexity to cpal

**hound**
- WAV, FLAC, Ogg Vorbis file reading/writing
- Doesn't handle playback itself (needs to be paired with cpal/rodio)

---

## Complete CLI Music Players (Built with Rust)

### **CLI-Rhythm**
- Simple, lightweight CLI music player
- Formats: MP3, WAV, FLAC, AAC
- Minimalistic interface with keyboard shortcuts

### **termusic**
- Full-featured terminal music and podcast player
- Formats: MP3, M4A, FLAC, AIFF, WAV, Opus, OGG Vorbis
- Can download music from youtube/netease/migu/kugou
- Embeds lyrics and album photos into files

### **simple-audio-player**
- Minimal audio player to play arbitrary sound files instantly from terminal

---

## External Program Fallback Options

If shelling out to external programs is acceptable:

### Linux-Specific
**aplay** (Part of ALSA)
- Default tool for WAV playback on Linux
- Pre-installed on most Linux systems
- ALSA-only (Linux only)
- Command: `aplay [flags] [filename]`

### macOS-Specific
**afplay** (Built-in)
- Native macOS audio playback tool
- Formats: AIFF, WAV, MP4, MP3
- Options: volume (-v), time (-t), rate (-r), quality (-q)
- Command: `afplay <sound file>`
- Limitation: Poor stdin piping support (tries to sniff format, requires seeking)

### Cross-Platform Tools

**ffplay** (Part of FFmpeg)
- Best cross-platform option
- Extensive format support
- Can suppress output: `ffplay -nodisp -autoexit -loglevel quiet filename.{wav,mp3,ogg,...}`
- Tempo and pitch adjustment support
- More reliable than afplay in some cases

**sox / play** (Sound eXchange)
- "Swiss Army knife of sound processing"
- Cross-platform (installable via homebrew, apt, etc.)
- Formats: WAV, MP3, FLAC, Ogg Vorbis
- Real-time audio effects
- Good stdin piping support: `cat file.raw | play -t raw -e floating-point -b 32 -c 2 -r 44100 -`
- Can access CoreAudio directly on macOS
- `play` is sox under a different name

**Other Options**
- **mplayer**: `mplayer foo.mp3`
- **mpg123**: MP3-specific player
- **mpv**: Good for piping audio

---

## Recommendation Summary

### For Pure Rust Solution
**Use rodio** - It's the de facto standard for audio playback in Rust:
- Simple API
- Cross-platform
- Well-maintained and widely used
- Good format support
- Perfect for CLI use cases

### For Shelling Out
**Platform detection strategy**:
1. **Linux**: aplay (pre-installed) or ffplay
2. **macOS**: afplay (pre-installed) or ffplay
3. **Windows**: ffplay or PowerShell
4. **Cross-platform fallback**: ffplay (if ffmpeg installed) or sox

**Best cross-platform external tool**: ffplay (part of ffmpeg suite)

---

## Sources

- [Audio — list of Rust libraries/crates // Lib.rs](https://lib.rs/multimedia/audio)
- [GitHub - RustAudio/rodio: Rust audio playback library](https://github.com/RustAudio/rodio)
- [rodio - crates.io: Rust Package Registry](https://crates.io/crates/rodio)
- [rodio: Complete Rust Crate Guide & Documentation [2025]](https://generalistprogrammer.com/tutorials/rodio-rust-crate-guide)
- [Top 5 Rust Crates for Audio Processing](https://crates.dev/article/Top_5_Rust_Crates_for_Audio_Processing.html)
- [CLI-Rhythm - crates.io: Rust Package Registry](https://crates.io/crates/CLI-Rhythm)
- [termusic - crates.io: Rust Package Registry](https://crates.io/crates/termusic)
- [soloud - crates.io: Rust Package Registry](https://crates.io/crates/soloud)
- [GitHub - MoAlyousef/soloud-rs: Rust bindings for the soloud audio engine library](https://github.com/MoAlyousef/soloud-rs)
- [How to play mp3 files from the command line? - Ask Ubuntu](https://askubuntu.com/questions/115369/how-to-play-mp3-files-from-the-command-line)
- [OSX equivalent of piping sound to linux's aplay - Stack Overflow](https://stackoverflow.com/questions/34809320/osx-equivalent-of-piping-sound-to-linuxs-aplay)
- [Alternative to APLAY for Mac OS X bash - Ask Different](https://apple.stackexchange.com/questions/74619/alternative-to-aplay-for-mac-os-x-bash)
- [Play MP3 or WAV file via the Linux command line - Super User](https://superuser.com/questions/276596/play-mp3-or-wav-file-via-the-linux-command-line)
