# Unreal Engine 4 - Installed Engine Build under Arch Linux

### 05/21/2019

In this guide we will be setting up an Installed Engine Build (like the one you get on Windows through the Epic Launcher) of Unreal Engine 4.22.2 with an Ubuntu VM whilst being on Arch Linux.

For a very long time I wanted to make an [Installed Engine Build](https://docs.unrealengine.com/en-us/Programming/Deployment/UsinganInstalledBuild) of Unreal Engine 4 for Arch Linux, but had no time to spare.

Since setting UE4 up for Arch Linux is not an easy task, because of mismatching compiler versions etc., I wanted to take the fastest route I could find. There are several problems in building UE4 for Arch Linux as you can see in [this thread](https://aur.archlinux.org/packages/unreal-engine).

This procedure will take up approximately 200 Gigabytes, but the final Engine Installation will only occupy around 15 Gigabytes.

## [](#vm-setup)Virtual Machine Setup

### [](#download-ubuntu)Download Ubuntu 18.04 Server LTS

We create a dir which will contain our VM applicance:

```bash
mkdir -p ~/vm/ue4-build-server && cd ~/vm/ue4-build-server
```

After that we grab the LTS copy of Ubuntu Server:

```bash
wget http://releases.ubuntu.com/18.04/ubuntu-18.04.2-live-server-amd64.iso
```

### [](#create-qemu-image)Create QEMU Image

Make sure you have QEMU and KVM installed. [Here](https://wiki.archlinux.org/index.php/QEMU) is a guide which explains how to do this on Arch. We need to create an image with the size of ~150 Gigabytes.

```bash
qemu-img create -f qcow2 ue4-build-disk.img 150G
```

### [](#install-ubuntu)Install Ubuntu

Bring up a VM with 4 cores and 6GB RAM and boot from the image:

```bash
qemu-system-x86_64 -enable-kvm -cpu host -smp 4 -enable-kvm -drive file=./ue4-build-disk.img,if=virtio -net nic -net user -m 6G -cdrom ./ubuntu-18.04.2-live-server-amd64.iso -boot d
```

Just follow the guided Ubuntu installation and make sure to select that it occupies the whole disk. For easiness in SSHing you should name your user the same as on the host machine.
After the installation shutdown the VM.

### [](#start-vm)Start Build Server

Start it again with VM port 22 being forwarded to hosts 2222 port.
You can assign more cores and memory if you want to speed up the build.

```bash
qemu-system-x86_64 -enable-kvm -cpu host -smp 4 -enable-kvm -drive file=./ue4-build-disk.img,if=virtio -m 6G -net nic -net user,hostfwd=tcp::2222-:22
```

Now SSH into the VM:

```bash
ssh localhost -p 2222
```

### [](#install-packages)Update & Install Packages in VM

First make sure that the system is up to date and fulfills the dependencies:

```bash
sudo apt update && sudo apt dist-upgrade -y && sudo apt install -y wget curl build-essential python xdg-utils
```

Reboot after this is done:

```bash
systemctl reboot
```

## [](#build-ue4)Build UE4

### [](#clone-repo-setup)Clone Repository & Setup

After rebooting, SSH into the VM again:

```bash
ssh localhost -p 2222
```

Clone the 4.22.2-release branch from Epics Github page and run Setup script:

```bash
git clone https://USER:TOKEN@github.com/EpicGames/UnrealEngine.git --branch 4.22.2-release --single-branch ue-4.22.2 && cd ./ue-4.22.2 && ./Setup.sh
```

### [](#minor-qoli)Make Minor Quality of Life Improvements for UE4 (Optional)

I've made some changes to a few config files. This is more a note to myself, but maybe someone does find it useful.
Download the repository from GitLab:

```bash
cd .. && git clone https://gitlab.com/JACKSONMEISTER/ue4-qoli.git --branch 4.22.2 --single-branch && cd ./ue-4.22.2
```

Patch UE source with updated configs:

```bash
git apply ../ue4-qoli/ue-4.22.2-qoli.patch
```

### [](#create-installed-build)Create Installed Build

Now run the build script to create an Installed Engine Build:

```bash
./Engine/Build/BatchFiles/RunUAT.sh BuildGraph -target="Make Installed Build Linux" -script=./Engine/Build/InstalledEngineBuild.xml -set:HostPlatformOnly=true -set:WithDDC=false -clean
```

Note that we are building without [Derived Data Cache](https://docs.unrealengine.com/en-us/Engine/Basics/DerivedDataCache) for space and time reasons. For more information about build parameters check [this site](https://docs.unrealengine.com/en-us/Programming/Deployment/UsinganInstalledBuild).

### [](#pack-archive)Pack Archive

For transferring the Installed Engine Build to the host we tar it and exit the session:

```bash
cd ~ && tar cf ue-4.22.2.tar -C ./ue-4.22.2/LocalBuilds/Engine/Linux . && exit
```

## [](#install-ue4)Install UE4 on Host

### [](#copy-from-vm)Copy from VM

We use SCP to copy the tarball from the Build Server:

```bash
scp -P 2222 localhost:~/ue-4.22.2.tar ~/downloads
```

### [](#install-opt)Install to /opt

Install the Engine to /opt. You can install it wherever you want - an even better practice would be to create an Arch Linux Packagebuild.

```bash
cd /opt && sudo mkdir ue-4.22.2 && sudo chown -R $USER:$USER ./ue-4.22.2 && cd ./ue-4.22.2 && tar xf ~/downloads/ue-4.22.2.tar
```

### [](#set-permissions)Set the right Permissions

According to [this PKGBUILD](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=unreal-engine) from the [unreal-engine AUR](https://aur.archlinux.org/packages/unreal-engine/) we need to set some permissions for the Engine to work correctly:

```bash
cd .. && chmod -R a+rwX ./ue-4.22.2
```

### [](#start-menu-shortcuts)Start Menu Shortcuts

To create start menu entries etc. we create the files ue-4.22.2.desktop and ue-4.22.2-debug.desktop:

```bash
# ue-4.22.2.desktop
#!/usr/bin/env xdg-open

[Desktop Entry]
Type=Application
Version=1.0
Name=Unreal Engine 4.22.2
Path=/opt/ue-4.22.2/Engine/Binaries/Linux
Exec=/opt/ue-4.22.2/Engine/Binaries/Linux/UE4Editor -opengl4
Icon=ue4editor
Terminal=false
Categories=Development;
Comment=Epic's Game Engine
```

```bash
# ue-4.22.2-debug.desktop
#!/usr/bin/env xdg-open

[Desktop Entry]
Type=Application
Version=1.0
Name=Unreal Engine 4.22.2 Debug
Path=/opt/ue-4.22.2/Engine/Binaries/Linux
Exec=/opt/ue-4.22.2/Engine/Binaries/Linux/UE4Editor-Linux-DebugGame -opengl4 -debug
Icon=ue4editor
Terminal=false
Categories=Development;
Comment=Epic's Game Engine
```

These files have to be placed in **$HOME/.local/share/applications**. The ue4editor icon is contained in the Papirus Icon Suite. Alternatively you can grab an icon from UE's source tree and place it in **$HOME/.local/share/icons**.

## [](#conclusion) Conclusion

Now we can have fun with UE4 on Arch Linux and distribute our UE4 Installed Engine Build to our team.
We managed to craft an Installed Engine Build using a VM and installed it to our Arch Linux host.
The build is redistributable for teams and easy to install. This type of build is also known as Rocket Build - the same type that is distributed within the Epic Launcher.

![](..assets/ue4-desktop.png)
