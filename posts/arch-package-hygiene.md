# Arch Linux Package Hygiene #

### 12/01/2020 ###

As Manjaro/Arch installations starting to age, maintaining proper package 
management discipline is an essential part to keep systems consistent throughout 
updates. This especially holds true when using a rolling release distribution.
This short guide servers as a compilation of all the cleanup and analyze commands
I have been using for several years. All of this information is more or less
copied from the Arch Wiki, especially from the
[pacman tips and tricks page](https://wiki.archlinux.org/index.php/Pacman/Tips_and_tricks)
and the [pacman main page](https://wiki.archlinux.org/index.php/pacman).

## [](#identify-remove)Identifying and Removing Orphans ##

### [](#orphans) Listing Orphaned Packages ###

```bash
$ pacman -Qdtq
```

Lists all as dependency installed packages which are not required anymore.
`-Q` switch indicates a package query. `-d` option lists only packages which
were installed as dependencies and `-t` arg filters packages which are not 
required by any installed package. To strip the version number for further 
processing `-q` is also appended.

### [](#removing) Removing Orphaned Packages ###

```bash
$ pacman -Rs $(pacman -Qdtq)
```

Args in the first command are there to indicate a package removal by passing
`-R`. The `-s` switch takes care that unnecessary dependencies are removed.
Here command expansion is used to pass a list of orphaned packages (see above)
to the removal call.

## [](#deps) Package Dependencies ##

### [](#list) Listing Package Dependencies ###

```bash
$ pactree curl -cd1
curl
├─ca-certificates
├─krb5
├─libssh2
├─libssh2 provides libssh2.so=1-64
├─openssl
├─zlib
├─libpsl
├─libpsl provides libpsl.so=5-64
├─libnghttp2
├─libidn2
├─libidn2 provides libidn2.so=0-64
└─zstd
```

Output lists all dependencies of curl package. `-c` switch simply colorizes 
output while `-d` switch defines depth of dependency listing. Example above 
with a depth of 2 would also list first child dependencies of curls dependencies:

```bash
$ pactree curl -cd2
curl
├─ca-certificates
│ └─ca-certificates-mozilla
├─krb5
│ ├─e2fsprogs
│ ├─libldap
│ └─keyutils
├─libssh2
│ ├─openssl
│ └─zlib
├─libssh2 provides libssh2.so=1-64
├─openssl
│ └─perl
├─zlib
│ └─glibc
├─libpsl
│ ├─libidn2
│ ├─libidn2 provides libidn2.so=0-64
│ └─libunistring
├─libpsl provides libpsl.so=5-64
├─libnghttp2
│ └─glibc
├─libidn2
│ └─libunistring
├─libidn2 provides libidn2.so=0-64
└─zstd
  ├─zlib
  ├─xz
  └─lz4
```

### [](#reverse) Reverse Dependencies ###

Often it is useful to find out to which packages the package in question
is a dependency. This is simply realized by adding `-r` switch to `pactree`.

```bash
$ pactree -crd1
curl
├─ceph-libs
├─cfitsio
├─cmake
├─dolphin-emu
├─dotnet-runtime
├─elfutils
├─exiv2
├─git
├─gst-plugins-bad
├─jp2a
├─lib32-curl
├─libcmis
├─libcurl-gnutls
├─libelf
├─libgphoto2
├─libofa
├─libofx
├─libqalculate
├─libreoffice-fresh
├─networkmanager
├─obs-studio
├─pacman
├─pakku
├─pkgfile
├─poppler
├─python-pycurl
├─qemu
├─raptor
└─sane
```

Depth value for `-d` switch does the same as above just in reverse order.

## [](#cache) Clearing the Package Cache ##

Installed packages are stored in `/var/cache/pacman/pkg/`. Packages will never 
get removed automatically - even after upgrades. For a long living system this
creates a high demand of persistent memory which one might not like.
To counter this behavior `paccache` can be used to clear old package installations.

```$ paccache -rk0``` removes all cached packages from hard drive.
However keep in mind that this makes it impossible to downgrade or reinstall
packages in offline mode. `-r` switch means remove and `-k` switch defines how
many of the latest versions should be kept.

```$ paccache -ruk0``` removes all cached packages which are uninstalled from
hard drive. `-u` switch indicates to remove uninstalled packages.

One could also tend to provide a combination of both methods. For example to 
remove all uninstalled packages and keep the latest version of installed packages
simply run: ```$ paccache -rk1 -ruk0```.

## [](#conclusion) Conclusion ##
In this post we have shown how to execute basic package hygiene on Arch Linux
based systems. We took a look at how to identify and remove orphaned packages,
how to query package dependencies and how to deal with a ever growing package
cache.
