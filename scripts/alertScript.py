import os

def replace_specific_links():
    """
    读取指定 Markdown 文件，根据预定义的映射表替换 ![[Pasted image ...]] 为 ![[Pn]]
    增强了匹配逻辑，可以匹配带 .png/.jpg 后缀或不带后缀的链接。
    """
    # 定义目标文件路径
    target_file = os.path.join('content', 'posts', 'EvilBox One Writeup', 'index.md')
    
    # 定义替换映射表 (Key: 原文件名(不含后缀), Value: 新文件名(不含后缀))
    replacements = {
        "Pasted image 20250511195359": "P1",
        "Pasted image 20250511195453": "P2",
        "Pasted image 20250511195530": "P3",
        "Pasted image 20250511195622": "P4",
        "Pasted image 20250511195743": "P5",
        "Pasted image 20250511200428": "P6",
        "Pasted image 20250511200758": "P7",
        "Pasted image 20250511200858": "P8",
        "Pasted image 20250511200928": "P9",
        "Pasted image 20250511201602": "P10",
        "Pasted image 20250511205626": "P11",
        "Pasted image 20250511211114": "P12",
        "Pasted image 20250511211410": "P13",
        "Pasted image 20250511211857": "P14",
        "Pasted image 20250511211927": "P15"
    }

    # 检查文件是否存在
    if not os.path.exists(target_file):
        print(f"错误: 找不到文件 -> {target_file}")
        # 调试用：打印当前工作目录，方便排查路径问题
        print(f"当前工作目录: {os.getcwd()}")
        return

    try:
        # 读取文件内容
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        count = 0
        replaced_items = []

        # 遍历映射表进行替换
        for old_key, new_val in replacements.items():
            # 定义多种可能的源格式，防止因后缀缺失或不同导致匹配失败
            # 注意：替换目标统一为 .png (即 ![[Pn.png]])
            patterns = [
                f"![[{old_key}.png]]",  # 匹配 .png
                f"![[{old_key}.jpg]]",  # 匹配 .jpg
                f"![[{old_key}]]"       # 匹配无后缀
            ]
            
            target_str = f"![[{new_val}.png]]"

            for search_str in patterns:
                if search_str in content:
                    # 统计出现的次数
                    matches = content.count(search_str)
                    content = content.replace(search_str, target_str)
                    count += matches
                    replaced_items.append(f"{search_str} -> {target_str}")

        # 如果内容发生了变化，则写回文件
        if content != original_content:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"成功处理文件: {target_file}")
            print("执行的替换操作如下：")
            for item in replaced_items:
                print(item)
            print(f"总计替换了 {count} 处链接。")
        else:
            print(f"在文件 {target_file} 中未找到任何匹配列表的链接。")
            print("请检查 Markdown 文件中的图片链接格式是否为 ![[Pasted image ...]] 或包含 .png/.jpg 后缀。")

    except Exception as e:
        print(f"处理文件时发生错误: {e}")

if __name__ == "__main__":
    replace_specific_links()