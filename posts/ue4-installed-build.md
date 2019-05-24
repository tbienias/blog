# Unreal Engine 4 - Installed Engine Build under Linux

### 05/21/2019

This is a little abstract.

## [](#vm-setup)Virtual Machine Setup

### [](#download-ubuntu)Download Ubuntu 18.04 Server LTS

```bash
mkdir -p ~/vm/ue4-build-server && cd ~/vm/ue4-build-server
```

```bash
wget http://releases.ubuntu.com/18.04/ubuntu-18.04.2-live-server-amd64.iso
```

### [](#create-qemu-image)Create QEMU Image

```bash
qemu-img create -f qcow2 ue4-build-disk.img 150G
```

### [](#install-ubuntu)Install Ubuntu

```bash
qemu-system-x86_64 -enable-kvm -cpu host -smp 4 -enable-kvm -drive file=./ue4-build-disk.img,if=virtio -net nic -net user -m 6G -cdrom ./ubuntu-18.04.2-live-server-amd64.iso -boot d
```

### [](#start-vm)Start Build Server

```bash
qemu-system-x86_64 -enable-kvm -cpu host -smp 4 -enable-kvm -drive file=./ue4-build-disk.img,if=virtio -m 6G -net nic -net user,hostfwd=tcp::2222-:22
```

```bash
ssh localhost -p 2222
```

### [](#install-packages)Update & Install Packages in VM

```bash
sudo apt update && sudo apt dist-upgrade -y && sudo apt install -y wget curl build-essential python xdg-utils
```

```bash
systemctl reboot
```

## [](#build-ue4)Build UE4

### [](#clone-repo-setup)Clone Repository & Setup

```bash
ssh localhost -p 2222
```

```bash
git clone https://USER:TOKEN@github.com/EpicGames/UnrealEngine.git --branch 4.22.2-release --single-branch ue-4.22.2 && cd ./ue-4.22.2 && ./Setup.sh
```

### [](#minor-qoli)Make Minor Quality of Life Improvements for UE4 (Optional)

```bash
cd .. && git clone https://gitlab.com/JACKSONMEISTER/ue4-qoli.git --branch 4.22.2 --single-branch && cd ./ue-4.22.2
```

```bash
git apply ../ue4-qoli/ue-4.22.2-qoli.patch
```

### [](#create-installed-build)Create Installed Build

```bash
./Engine/Build/BatchFiles/RunUAT.sh BuildGraph -target="Make Installed Build Linux" -script=./Engine/Build/InstalledEngineBuild.xml -set:HostPlatformOnly=true -set:WithDDC=false -clean
```

### [](#pack-archive)Pack Archive

```bash
cd .. && tar cf ue-4.22.2.tar -C ./ue-4.22.2/LocalBuilds/Engine/Linux . && exit
```

## [](#install-ue4)Install UE4 on Host

### [](#copy-from-vm)Copy from VM

```bash
scp -P 2222 localhost:~/ue-4.22.2.tar ~
```

### [](#install-opt)Install to /opt

```bash
cd /opt && sudo mkdir ue-4.22.2 && sudo chown -R jacksonmeister:jacksonmeister ./* && cd ./ue-4.22.2 && tar xf ~/ue-4.22.2.tar
```

### [](#set-permissions)Set the right Permissions

```bash
chmod -R a+rwX ./*
```