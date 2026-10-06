# Grok Bot on Fedora

I wanted to install Grok Bot on Fedora. The installer I had was a Debian package, `grok-bot_0.66.0_amd64.deb`. Fedora installs software from RPM packages with `dnf`, so that `.deb` could not be installed. That is what started this project.

`build.sh` reads a Grok Bot `.deb` and builds an RPM from the same files.

## Build

Install the RPM build tools once:

```bash
sudo dnf install rpm-build
```

Build from the downloaded package:

```bash
./build.sh ~/Downloads/grok-bot_0.66.0_amd64.deb
```

The RPM is written to `dist/`.

## Install

```bash
sudo dnf install ./dist/grok-bot-*.x86_64.rpm
```

Grok Bot is installed under `/opt/Grok Bot`. Start it from the application menu, or run `grok-bot`.

On this Fedora 44 machine the transaction also installs `libXScrnSaver`. `libappindicator-gtk3` is a weak dependency, used for the tray icon.

## What the package keeps from the .deb

The program files are copied unchanged. The RPM creates the `/usr/bin/grok-bot` command, the desktop entry, and the icons. Debian dependency names are mapped to Fedora packages (`gtk3`, `alsa-lib`, `nss`, and the rest of the libraries the app loads). `libffmpeg.so` stays inside `/opt/Grok Bot` and is not published as a system library.

## Updates

The Debian package registers an apt repository so later upgrades come from Cursor. This RPM does not add a DNF repository. `dnf upgrade` will not fetch a newer Grok Bot. To move forward, download the newer `.deb`, run `build.sh` again, and install the new RPM.

The `.deb` and the built `.rpm` are not stored in this repository. Grok Bot is proprietary. Download the package yourself and build it on the machine where you will install it.
