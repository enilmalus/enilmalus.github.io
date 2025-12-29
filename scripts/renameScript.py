import os

def rename_pasted_images():
    """
    遍历指定目录，将名为 "Pasted image xxx" 的图片重命名为 P1, P2, P3...
    """
    # 定义目标目录 (使用 os.path.join 适配不同操作系统)
    target_dir = os.path.join('content', 'posts', 'DeathStart Writeup')

    # 检查目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误: 找不到目录 -> {target_dir}")
        return

    # 获取目录下所有文件
    all_files = os.listdir(target_dir)

    # 筛选符合条件的文件
    # 条件1: 以 "Pasted image" 开头
    # 条件2: 后缀为 .png 或 .jpg (忽略大小写)
    images_to_rename = []
    for filename in all_files:
        if filename.startswith("Pasted image") and \
           (filename.lower().endswith(".png") or filename.lower().endswith(".jpg")):
            images_to_rename.append(filename)

    # 排序文件
    # 这一点很重要，通常 "Pasted image" 后面跟的是时间戳，
    # 默认的字符串排序即可保证按时间顺序重命名 (P1对应最早的截图)
    images_to_rename.sort()

    if not images_to_rename:
        print("未发现符合 'Pasted image xxx' 格式的 png/jpg 图片。")
        return

    print(f"发现 {len(images_to_rename)} 张图片，开始重命名...")

    # 遍历并重命名
    for index, old_name in enumerate(images_to_rename, start=1):
        # 获取原始文件名和后缀名
        old_root, ext = os.path.splitext(old_name)
        
        # 构建新文件名主体 P1, P2...
        new_root = f"P{index}"
        # 构建完整新名称: P1.png, P2.jpg ...
        new_name = f"{new_root}{ext}"
        
        old_path = os.path.join(target_dir, old_name)
        new_path = os.path.join(target_dir, new_name)

        # 防止覆盖已存在的 Pn 文件 (如果文件夹里原本就有 P1.png)
        if os.path.exists(new_path):
             print(f"跳过: '{new_name}' 已存在，无法将 '{old_name}' 重命名为此名称。")
             continue

        try:
            # 执行重命名
            os.rename(old_path, new_path)
            # 按照要求的格式输出：原名(无后缀)     新名(无后缀)
            print(f"{old_root}     {new_root}")
        except OSError as e:
            print(f"重命名 '{old_name}' 失败: {e}")

    print("所有操作完成。")

if __name__ == "__main__":
    rename_pasted_images()