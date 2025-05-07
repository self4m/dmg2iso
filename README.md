# 一、操作说明

使用苹果官方的 DMG 镜像文件将系统安装器安装到 macOS 的 `应用程序` 目录中  

再通过安装器内置的 `createinstallmedia` 工具将包含引导程序的安装器写入目标镜像文件  

将镜像文件转换为可以启动的 iso 格式的镜像文件  

  

！！！**只支持 macOS 10.13 ~ 至今的镜像系统**！！！  

！！！**只支持 macOS 10.13 ~ 至今的镜像系统**！！！  

！！！**只支持 macOS 10.13 ~ 至今的镜像系统**！！！  

  

可以通过 https://github.com/corpnewt/gibMacOS 工具下载镜像文件，但是转换为 DMG 文件需要使用 macOS    

---

# 二、运行环境

- macOS 系统（这点很难绷，要是有  谁还搞 iso ）
- python 环境 推荐使用 python 3.8 及以上版本

---

# 三、使用方法

1. 将苹果官方的 DMG 镜像文件安装到 macOS 系统中

2. 执行脚本生成镜像文件

   - 双击执行

   ```
   双击 dmg2iso.command 即可开始处理
   ```

   - 命令行执行

   ```bash
   # 在 Tetminal 中执行 python3 dmg2iso.py 命令即可开始处理
   python3 dmg2iso.py
   ```

3. 转换后的镜像文件存储于脚本目录的 `iso` 文件夹中

4. 压缩 `iso` 文件（可选）

   生成临时镜像时已尽可能的缩小大小了，但是仍需预留空间以供安装器使用  

   由于 `iso` 文件的性质，所以转换生成的文件大小将与临时镜像的大小相同  

   使用压缩脚本重构 `iso` 文件，预计将会节省 1G 左右的空间

   - 双击执行

   ```
   双击 optimize_iso.command 即可开始处理
   ```

   - 命令行执行

   ```bash
   # 在 Tetminal 中执行 python3 optimize_iso.py 命令即可开始处理
   python3 optimize_iso.py
   ```