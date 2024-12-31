# 照片数据分析器

## 概览

这个Python脚本旨在读取并分析指定目录下照片的EXIF数据。它从每张照片的元数据中提取并统计焦段、光圈、ISO、相机型号和镜头型号。脚本使用`exiftool`工具来提取EXIF数据，并提供对照片集合的全面分析。

## 功能特点

- **EXIF数据提取**：从图像文件中提取EXIF数据。
- **数据聚合**：收集并统计特定的EXIF数据，如焦段、光圈、ISO、相机型号和镜头型号。
- **多线程**：采用多线程技术高效处理大量文件。
- **数据可视化**：使用`matplotlib`为每个EXIF数据类别生成条形图。

## 要求

- **Python**：需要Python 3.x来运行此脚本。
- **exiftool**：脚本依赖于`exiftool`工具来提取EXIF数据。必须安装并在系统的PATH中可用，或者在脚本中指定`EXIFTOOL_PATH`变量的正确路径。

## 安装

1. 确保系统已安装Python。
2. 使用pip安装所需的库：
   ```bash
   pip install matplotlib
   ```
3. 从官方网站下载并安装exiftool，并确保它在系统的PATH中可用，或者更新脚本中的EXIFTOOL_PATH变量，指向exiftool.exe的正确路径。
   
## 使用方法

1. 如果exiftool.exe不在系统的PATH中，请更新脚本中的EXIFTOOL_PATH变量为其路径。
2. 修改main函数中的base_folder变量为你想要分析的照片所在的目录。
3. 运行脚本。输出将默认保存在./output目录中。
   
##命令行执行

在命令行或终端中运行脚本：
```bash
python photo_exif_analyzer.py
```
