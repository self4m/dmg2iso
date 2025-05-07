#!/usr/bin/env python3
import os
import sys
import subprocess
import glob
import signal
import math

def run(cmd, sudo=False):
    if sudo:
        cmd = ['sudo'] + cmd
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 命令执行失败: {' '.join(e.cmd)}")
        sys.exit(1)

def input_int(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
            print(f"请输入 {min_val} 到 {max_val} 之间的数字。")
        except ValueError:
            print("无效输入，请输入一个数字。")

def list_installers():
    apps_dir = "/Applications"
    pattern = os.path.join(apps_dir, "Install macOS *.app")
    return glob.glob(pattern)

def choose_installer(apps):
    print("[INFO] 检测到以下 macOS 安装器：")
    for i, app in enumerate(apps, 1):
        print(f"[{i}] {os.path.basename(app)}")
    idx = input_int("请选择编号: ", 1, len(apps))
    return apps[idx - 1]

def get_installer_size(installer_path):
    result = subprocess.run(['du', '-sk', installer_path], stdout=subprocess.PIPE, text=True)
    size_str = result.stdout.split()[0]
    size_in_kb = int(size_str)
    size_in_gb = size_in_kb / 1024 / 1024
    return size_in_gb

def create_temp_dmg(installer_path, dmg_path, volume_name):
    installer_size_gb = get_installer_size(installer_path)
    dmg_size_gb = math.ceil(installer_size_gb * 1.2)
    dmg_size = f"{dmg_size_gb}g"
    print(f"[INFO] 安装器大小：{installer_size_gb:.2f} GB，创建临时卷 .dmg 文件大小：{dmg_size}")

    if os.path.exists(dmg_path):
        os.remove(dmg_path)

    print(f"[INFO] 正在创建中...")
    run([
        "hdiutil", "create",
        "-size", dmg_size,
        "-layout", "SPUD",
        "-fs", "HFS+J",
        "-volname", volume_name,
        "-o", dmg_path
    ])
    print(f"[INFO] 临时 .dmg 文件创建完成")

def attach_dmg(dmg_path, mount_point):
    print(f"[INFO] 挂载镜像...")
    run(["hdiutil", "attach", dmg_path, "-mountpoint", f"/Volumes/{mount_point}", "-nobrowse"])

def detach_volume(mount_point):
    vol_path = f"/Volumes/{mount_point}"
    if os.path.exists(vol_path):
        print(f"[INFO] 卸载镜像...")
        try:
            run(["hdiutil", "detach", vol_path])
        except:
            pass

def create_install_media(installer_app, temp_volume):
    tool = os.path.join(installer_app, "Contents/Resources/createinstallmedia")
    if not os.path.exists(tool):
        print(f"[ERROR] 找不到 createinstallmedia 工具: {tool}")
        sys.exit(1)
    print("[INFO] 写入安装器到临时卷...")

    try:
        subprocess.run(
            ['sudo', tool, '--volume', f'/Volumes/{temp_volume}', '--nointeraction'],
            check=True
        )
        print("[INFO] 安装器写入完成")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] createinstallmedia 执行失败: {' '.join(e.cmd)}")
        sys.exit(1)

def compress_dmg(input_dmg, output_dmg):
    print("[INFO] 正在压缩生成 Installer.dmg ...")
    try:
        subprocess.run([
            "hdiutil", "convert", input_dmg,
            "-format", "UDZO",
            "-o", output_dmg
        ], check=True)
        print(f"[SUCCESS] 生成压缩镜像: {output_dmg}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] hdiutil convert 压缩失败: {' '.join(e.cmd)}")
        sys.exit(1)

def convert_dmg_to_iso(input_dmg, iso_path):
    cdr_path = iso_path + ".cdr"
    if os.path.exists(cdr_path):
        os.remove(cdr_path)
    if os.path.exists(iso_path):
        os.remove(iso_path)
    print("[INFO] 正在将镜像文件转换为 ISO 格式...")

    try:
        subprocess.run([
            "hdiutil", "convert", input_dmg,
            "-format", "UDTO",
            "-o", cdr_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] hdiutil convert 执行失败: {' '.join(e.cmd)}")
        sys.exit(1)

    try:
        os.rename(cdr_path, iso_path)
        print(f"[SUCCESS] ISO 镜像已生成: {iso_path}")
    except Exception as e:
        print(f"[ERROR] 重命名失败: {e}")
        print(f"请手动执行：mv {cdr_path} {iso_path}")

def cleanup(paths):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)

def handle_interrupt(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_interrupt)

if __name__ == "__main__":
    installers = list_installers()
    if not installers:
        print("[ERROR] /Applications 下未找到 macOS 安装器")
        sys.exit(1)

    installer_app = choose_installer(installers)
    installer_name = os.path.splitext(os.path.basename(installer_app))[0]

    output_dir = os.path.join(os.getcwd(), "iso")
    os.makedirs(output_dir, exist_ok=True)

    temp_dmg = os.path.join(output_dir, f"Temp_{installer_name}.dmg")
    final_dmg = os.path.join(output_dir, f"{installer_name}.dmg")
    iso_path = os.path.join(output_dir, f"{installer_name}.iso")
    temp_volume = "InstallVolume"

    try:
        cleanup([temp_dmg, final_dmg, iso_path])
        create_temp_dmg(installer_app, temp_dmg, temp_volume)
        attach_dmg(temp_dmg, temp_volume)
        create_install_media(installer_app, temp_volume)
        detach_volume(temp_volume)
        detach_volume(installer_name)
        compress_dmg(temp_dmg, final_dmg)
        convert_dmg_to_iso(final_dmg, iso_path)
        cleanup([temp_dmg])
    except KeyboardInterrupt:
        print("\n[INFO] 检测到用户中断 (Ctrl+C)，准备清理资源...")
        detach_volume(temp_volume)
        detach_volume(installer_name)
        cleanup([temp_dmg])
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 发生异常: {e}")
        print("[INFO] 正在清理挂载卷和临时文件...")
        detach_volume(temp_volume)
        detach_volume(installer_name)
        cleanup([temp_dmg])
        sys.exit(1)
