import os
import subprocess
import json
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# 设置 exiftool 的路径
EXIFTOOL_PATH = r'C:\Program Files\LRTimelapse 7\exiftool.exe' #替换为自己的exiftool安装路径
SAVE_DIR = r'.\output'  # 保存图片的目录


def get_exif_data(filepath):
    try:
        result = subprocess.run(
            [EXIFTOOL_PATH, '-j', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'  # 指定使用 utf-8 编码
        )
        exif_data = json.loads(result.stdout)
        return exif_data[0] if exif_data else None
    except json.JSONDecodeError as e:
        print(f"JSON decode error for file {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        return None


def get_equivalent_focal_length(exif_data):
    focal_length = exif_data.get('FocalLengthIn35mmFormat', 'Unknown')
    try:
        equivalent_focal_length = int(focal_length)
        return equivalent_focal_length
    except:
        return 'Unknown'


def get_camera_model(exif_data):
    return str(exif_data.get('Model', 'Unknown'))


def get_lens_model(exif_data):
    return str(exif_data.get('LensID', exif_data.get('LensModel', exif_data.get('Lens', 'Unknown'))))


def get_aperture(exif_data):
    return str(exif_data.get('FNumber', 'Unknown'))


def get_iso(exif_data):
    return str(exif_data.get('ISO', 'Unknown'))


def process_file(file_path):
    exif_data = get_exif_data(file_path)
    if not exif_data:
        return None, None, None, None, None, file_path

    equivalent_focal_length = get_equivalent_focal_length(exif_data)
    camera_model = get_camera_model(exif_data)
    lens_model = get_lens_model(exif_data)
    aperture = get_aperture(exif_data)
    iso = get_iso(exif_data)

    # 输出处理完成的文件名
    print(f"Processed: {os.path.basename(file_path)}")

    return equivalent_focal_length, camera_model, lens_model, aperture, iso, None


def traverse_folders(base_folder):
    focal_length_distribution = defaultdict(int)
    camera_model_distribution = defaultdict(int)
    lens_model_distribution = defaultdict(int)
    aperture_distribution = defaultdict(int)
    iso_distribution = defaultdict(int)
    error_files = []
    files_to_process = []

    # 收集所有待处理的文件，排除以 '.' 开头的文件
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if not file.startswith('.') and file.lower().endswith(('.jpg', '.raf', '.nef', '.arw', '.cr3')):
                files_to_process.append(os.path.join(root, file))

    # 使用多线程处理文件
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(process_file, file_path): file_path for file_path in files_to_process}

        for future in as_completed(futures):
            focal_length, camera_model, lens_model, aperture, iso, error_file = future.result()
            if error_file:
                error_files.append(error_file)
            else:
                focal_length_distribution[focal_length] += 1
                camera_model_distribution[camera_model] += 1
                lens_model_distribution[lens_model] += 1
                aperture_distribution[aperture] += 1
                iso_distribution[iso] += 1

    return (focal_length_distribution, camera_model_distribution, lens_model_distribution,
            aperture_distribution, iso_distribution, error_files)


def plot_distribution(distribution, title, xlabel, numeric_sort=False, bin_size=None):
    if not distribution:
        print(f"No data available for {title}. Unable to generate plot.")
        return

    if numeric_sort:
        items = sorted(distribution.items(), key=lambda x: float(x[0].replace('Unknown', 'inf').replace('undef', 'inf')))
    elif bin_size:
        # 将数值根据 bin_size 进行分段
        bins = defaultdict(int)
        for key, value in distribution.items():
            if key.isdigit():
                key_bin = (int(key) // bin_size) * bin_size
                bins[f"[{key_bin}~{key_bin + bin_size})"] += value
            else:
                bins[key] += value
        items = sorted(bins.items())
    else:
        items = sorted(distribution.items())

    labels, values = zip(*items)

    plt.figure(figsize=(12, 6))
    plt.bar(labels, values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # 保存图表
    save_path = os.path.join(SAVE_DIR, f"{title}.png")
    plt.savefig(save_path)
    print(f"Saved plot to {save_path}")


def main():
    base_folder = r"E:\相机" ##修改为你想统计硬盘的目录

    # 确保保存目录存在
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    (focal_length_dist, camera_model_dist, lens_model_dist,
     aperture_dist, iso_dist, error_files) = traverse_folders(base_folder)

    print("全画幅等效焦段分布:")
    for focal_length, count in focal_length_dist.items():
        print(f"{focal_length}: {count}")

    print("\n机型分布:")
    for model, count in camera_model_dist.items():
        print(f"{model}: {count}")

    print("\n镜头分布:")
    for lens, count in lens_model_dist.items():
        print(f"{lens}: {count}")

    print("\n光圈分布:")
    for aperture, count in aperture_dist.items():
        print(f"{aperture}: {count}")

    print("\nISO分布:")
    for iso, count in iso_dist.items():
        print(f"{iso}: {count}")
    #输出不支持的文件用作exiftool字段调试
    # if error_files:
    #     print("\n无法读取EXIF信息的文件(不支持的格式):")
    #     for file in error_files:
    #         print(file)

    plot_distribution(focal_length_dist, 'Full-frame Equivalent Focal Length Distribution',
                      'Focal Length (35mm equivalent)', bin_size=10)
    plot_distribution(camera_model_dist, 'Camera Model Distribution', 'Camera Model')
    plot_distribution(lens_model_dist, 'Lens Model Distribution', 'Lens Model')
    plot_distribution(aperture_dist, 'Aperture Distribution', 'Aperture (F-number)', numeric_sort=True)
    plot_distribution(iso_dist, 'ISO Distribution', 'ISO Value', numeric_sort=True)


if __name__ == "__main__":
    main()