import os
import subprocess
import sys
import shutil

def run(cmd, sudo=False):
    if sudo:
        cmd = ['sudo'] + cmd
    try:
        subprocess.run(
            cmd, 
            check=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.STDOUT
        )
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

def list_iso_files():
    iso_dir = os.path.join(os.getcwd(), "iso")
    if not os.path.exists(iso_dir):
        print(f"[ERROR] 目录不存在: iso/")
        sys.exit(1)
    return [f for f in os.listdir(iso_dir) if f.endswith(".iso")]

def choose_iso_file(filenames):
    print("[INFO] 可用镜像文件：")
    for i, name in enumerate(filenames, 1):
        print(f"[{i}] {name}")
    idx = input_int("请选择编号: ", 1, len(filenames))
    return filenames[idx - 1]

def mount_iso(full_path):
    result = subprocess.run(
        ["hdiutil", "attach", full_path],
        capture_output=True, 
        text=True
    )
    if result.returncode != 0:
        print("[ERROR] 挂载失败")
        sys.exit(1)
    
    for line in result.stdout.splitlines():
        if "/Volumes/" in line:
            return line.split("\t")[-1].split("/")[-1]
    print("[ERROR] 挂载异常")
    sys.exit(1)

def unmount_iso(volume_name):
    print(f"[INFO] 正在卸载 {volume_name}...")
    run(["hdiutil", "detach", f"/Volumes/{volume_name}"])

def compress_process(selected_file):
    base_name = os.path.splitext(selected_file)[0]
    output_name = f"{base_name}_compressed.iso"
    final_name = f"{base_name}_compressed_optimized.iso"
    
    iso_dir = os.path.join(os.getcwd(), "iso")
    src_path = os.path.join(iso_dir, selected_file)
    temp_dir = os.path.join(iso_dir, "temp")

    print("=" * 40)
    print(f"[INFO] 开始处理: {selected_file}")
    
    volume_name = mount_iso(src_path)
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        print(f"[INFO] 正在复制文件...")
        run(["cp", "-R", f"/Volumes/{volume_name}/.", temp_dir])

        print(f"[INFO] 正在生成 {output_name}...")
        dest_path = os.path.join(iso_dir, output_name)
        run([
            "hdiutil", "makehybrid",
            "-iso", "-joliet",
            "-o", dest_path,
            temp_dir
        ])

        print(f"[INFO] 正在优化 {final_name}...")
        final_path = os.path.join(iso_dir, final_name)
        run([
            "hdiutil", "convert",
            dest_path,
            "-format", "UDTO",
            "-o", final_path
        ])

        os.remove(dest_path)
        if os.path.exists(final_path + ".cdr"):
            shutil.move(final_path + ".cdr", final_path)

        print(f"[SUCCESS] 生成镜像: {final_name}")
        size_mb = os.path.getsize(final_path) // 1024 // 1024
        print(f"[INFO] 最终大小: {size_mb}MB")

    finally:
        unmount_iso(volume_name)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=== macOS ISO 压缩工具 ===")
    
    iso_files = list_iso_files()
    if not iso_files:
        print("[ERROR] iso/ 目录中没有找到ISO文件")
        sys.exit(1)
    
    selected = choose_iso_file(iso_files)
    compress_process(selected)
    print("[INFO] 操作完成！")
