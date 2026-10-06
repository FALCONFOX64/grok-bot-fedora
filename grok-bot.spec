# Repack a Grok Bot Debian package as a Fedora RPM.
# build.sh extracts the .deb and passes _version and _payload.

%{!?_payload:%{error:Run ./build.sh so the _payload macro is defined}}
%{!?_version:%{error:Run ./build.sh so the _version macro is defined}}

Name:           grok-bot
Version:        %{_version}
Release:        1%{?dist}
Summary:        Grok Bot desktop agent
License:        LicenseRef-Proprietary
URL:            https://cursor.com
ExclusiveArch:  x86_64
Vendor:         SpaceXAI
Packager:       SpaceXAI <hi@cursor.com>

# Same runtime libraries as the Debian Depends line.
# Sonames that rpmbuild can see are also added automatically.
Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       libuuid
Requires:       libsecret
Requires:       alsa-lib
Requires:       mesa-libgbm
Requires:       libxkbcommon
Requires:       libdrm
Requires(post): alternatives
Requires(postun): alternatives

# Debian Recommends: libappindicator3-1. Tray icon support.
Recommends:     libappindicator-gtk3

# The Debian package replaced an earlier product name.
Provides:       sand = %{version}-%{release}
Obsoletes:      sand < %{version}-%{release}

# Bundled Electron libraries must not become system-wide Provides.
# libffmpeg.so is NEEDED by the main binary and resolved via $ORIGIN.
AutoProv:       no
%global __requires_exclude ^libffmpeg\\.so(\\(.*\\))?$
%global __os_install_post %{nil}
%global debug_package %{nil}

%description
Grok Bot desktop agent.

Repackaged from the Debian package grok-bot_%{version}_amd64.deb.
Files are installed under /opt/Grok Bot, with a /usr/bin/grok-bot command,
a desktop entry, and hicolor icons.

%prep
# Payload is already unpacked.

%build
# Prebuilt Electron application. Nothing to compile.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a %{_payload}/. %{buildroot}/
chmod 0755 "%{buildroot}/opt/Grok Bot/chrome-sandbox"
chmod 0755 "%{buildroot}/opt/Grok Bot/grok-bot"

%post -p /bin/bash
if type update-alternatives >/dev/null 2>&1; then
    if [ -L '/usr/bin/grok-bot' -a -e '/usr/bin/grok-bot' -a "`readlink '/usr/bin/grok-bot'`" != '/etc/alternatives/grok-bot' ]; then
        rm -f '/usr/bin/grok-bot'
    fi
    update-alternatives --install '/usr/bin/grok-bot' 'grok-bot' '/opt/Grok Bot/grok-bot' 100 || ln -sf '/opt/Grok Bot/grok-bot' '/usr/bin/grok-bot'
else
    ln -sf '/opt/Grok Bot/grok-bot' '/usr/bin/grok-bot'
fi

# Match the Debian postinst: setuid sandbox only when user namespaces are unavailable.
if ! { [[ -L /proc/self/ns/user ]] && unshare --user true; }; then
    chmod 4755 '/opt/Grok Bot/chrome-sandbox' || true
else
    chmod 0755 '/opt/Grok Bot/chrome-sandbox' || true
fi

if hash update-mime-database 2>/dev/null; then
    update-mime-database /usr/share/mime || true
fi

if hash update-desktop-database 2>/dev/null; then
    update-desktop-database /usr/share/applications || true
fi

if hash gtk-update-icon-cache 2>/dev/null; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi

if apparmor_status --enabled >/dev/null 2>&1; then
    APPARMOR_PROFILE_SOURCE='/opt/Grok Bot/resources/apparmor-profile'
    APPARMOR_PROFILE_TARGET='/etc/apparmor.d/grok-bot'
    if apparmor_parser --skip-kernel-load --debug "$APPARMOR_PROFILE_SOURCE" >/dev/null 2>&1; then
        cp -f "$APPARMOR_PROFILE_SOURCE" "$APPARMOR_PROFILE_TARGET"
        if hash apparmor_parser 2>/dev/null; then
            apparmor_parser --replace --write-cache --skip-read-cache "$APPARMOR_PROFILE_TARGET" || true
        fi
    else
        echo "Skipping the installation of the AppArmor profile as this version of AppArmor does not seem to support the bundled profile" >&2
    fi
fi

%postun -p /bin/bash
if [ "$1" -eq 0 ]; then
    if type update-alternatives >/dev/null 2>&1; then
        update-alternatives --remove 'grok-bot' '/opt/Grok Bot/grok-bot' || true
    else
        rm -f '/usr/bin/grok-bot'
    fi

    if [ -f /etc/apparmor.d/grok-bot ]; then
        if apparmor_status --enabled >/dev/null 2>&1 && hash apparmor_parser 2>/dev/null; then
            apparmor_parser --remove /etc/apparmor.d/grok-bot || true
        fi
        rm -f /etc/apparmor.d/grok-bot
    fi
fi

if hash update-desktop-database 2>/dev/null; then
    update-desktop-database /usr/share/applications || true
fi

if hash gtk-update-icon-cache 2>/dev/null; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi

%files
"/opt/Grok Bot"
/usr/share/applications/grok-bot.desktop
/usr/share/doc/grok-bot
/usr/share/icons/hicolor/16x16/apps/grok-bot.png
/usr/share/icons/hicolor/24x24/apps/grok-bot.png
/usr/share/icons/hicolor/32x32/apps/grok-bot.png
/usr/share/icons/hicolor/48x48/apps/grok-bot.png
/usr/share/icons/hicolor/64x64/apps/grok-bot.png
/usr/share/icons/hicolor/128x128/apps/grok-bot.png
/usr/share/icons/hicolor/256x256/apps/grok-bot.png
/usr/share/icons/hicolor/512x512/apps/grok-bot.png
