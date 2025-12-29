import os

def replace_specific_links():
    """
    读取指定 Markdown 文件，根据预定义的映射表替换 ![[Pasted image ...]] 为 ![[Pn]]
    """
    # 定义目标文件路径
    target_file = os.path.join('content', 'posts', 'DeathStart Writeup', 'index.md')
    
    # 定义替换映射表 (Key: 原文件名, Value: 新文件名)
    replacements = {
        "Pasted image 20250624162048": "P1",
        "Pasted image 20250624162222": "P2",
        "Pasted image 20250624162225": "P3",
        "Pasted image 20250624162347": "P4",
        "Pasted image 20250624162455": "P5",
        "Pasted image 20250624162613": "P6",
        "Pasted image 20250624162810": "P7",
        "Pasted image 20250624163016": "P8",
        "Pasted image 20250624163223": "P9",
        "Pasted image 20250624163547": "P10",
        "Pasted image 20250624163649": "P11",
        "Pasted image 20250624164027": "P12",
        "Pasted image 20250624164201": "P13",
        "Pasted image 20250624164208": "P14",
        "Pasted image 20250624164218": "P15",
        "Pasted image 20250624164338": "P16",
        "Pasted image 20250624164707": "P17",
        "Pasted image 20250624164737": "P18",
        "Pasted image 20250624164912": "P19",
        "Pasted image 20250624164959": "P20",
        "Pasted image 20250624165103": "P21",
        "Pasted image 20250624165218": "P22",
        "Pasted image 20250624165405": "P23",
        "Pasted image 20250624170238": "P24"
    }

    # 检查文件是否存在
    if not os.path.exists(target_file):
        print(f"错误: 找不到文件 -> {target_file}")
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
            # 构造完整的搜索和替换字符串，现在包含 .png 后缀
            search_str = f"![[{old_key}.png]]"
            replace_str = f"![[{new_val}.png]]"
            
            # 如果文件中存在该字符串，则进行替换
            if search_str in content:
                # 统计出现的次数
                matches = content.count(search_str)
                content = content.replace(search_str, replace_str)
                count += matches
                replaced_items.append(f"{search_str} -> {replace_str}")

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
            print("未在文件中找到任何匹配列表的链接，文件未修改。")

    except Exception as e:
        print(f"处理文件时发生错误: {e}")

if __name__ == "__main__":
    replace_specific_links()