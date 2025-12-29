import os
import re

def replace_specific_links():
    """
    读取指定 Markdown 文件，将 ![[Pasted image ...]] 替换为 ![[Pn.png]]
    包含强力调试功能，检测文件是否已保存或包含特殊字符。
    """
    target_file = os.path.join('content', 'posts', 'Venom Writeup', 'index.md')
    
    # 替换映射表
    replacements = {
        "Pasted image 20250524173935": "P1",
        "Pasted image 20250524174155": "P2",
        "Pasted image 20250524174246": "P3",
        "Pasted image 20250524174321": "P4",
        "Pasted image 20250524174409": "P5",
        "Pasted image 20250524174415": "P6",
        "Pasted image 20250524174423": "P7",
        "Pasted image 20250524174443": "P8",
        "Pasted image 20250524174820": "P9",
        "Pasted image 20250524174921": "P10",
        "Pasted image 20250524175222": "P11",
        "Pasted image 20250524175401": "P12",
        "Pasted image 20250524175455": "P13",
        "Pasted image 20250524175511": "P14",
        "Pasted image 20250524181324": "P15",
        "Pasted image 20250524181345": "P16",
        "Pasted image 20250524181506": "P17",
        "Pasted image 20250524181547": "P18",
        "Pasted image 20250524181711": "P19",
        "Pasted image 20250524181752": "P20",
        "Pasted image 20250524181839": "P21",
        "Pasted image 20250524181912": "P22",
        "Pasted image 20250524182056": "P23"
    }

    if not os.path.exists(target_file):
        print(f"❌ 错误: 找不到文件 -> {target_file}")
        return

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("-" * 40)
        print("【步骤1：检查文件原始内容】")
        
        # 预检：文件中是否包含 'Pasted image' 字符串？
        if "Pasted image" not in content and "Pasted image" not in content: # 注意第二个包含特殊空格
            print("⚠️ 警告：在读取的文件内容中，完全没有找到 'Pasted image' 这个字符串！")
            print("可能的原因为：")
            print("1. 你在编辑器中还原了内容，但**没有保存** (Ctrl+S)。")
            print("2. 文件已经被上一次运行成功修改过了（变成了 P1, P2...）。")
            
            # 打印当前文件中的前5个链接看看是什么样子的
            print("\n当前文件中的前 3 个图片链接长这样：")
            preview_links = re.findall(r'!\[\[.*?\]\]', content)
            for l in preview_links[:3]:
                print(f"  {l}")
            return

        print("✅ 检测到 'Pasted image' 字符串，文件已读取，准备替换...")

        # 定义更宽松的正则
        # \s+ : 匹配任意空白字符（包括空格、Tab、换行符）
        # .*? : 允许 .png 后缀之前有任意字符
        pattern = re.compile(r'!\[\[\s*(Pasted\s+image\s+\d+).*?\]\]', re.IGNORECASE)

        replaced_items = []
        
        def replacement_func(match):
            full_match = match.group(0)
            # 将匹配到的文件名中的所有空白字符替换为标准单空格，以便查表
            # 例如 "Pasted   image 123" -> "Pasted image 123"
            raw_name = match.group(1)
            standard_name = re.sub(r'\s+', ' ', raw_name)
            
            if standard_name in replacements:
                new_name = replacements[standard_name]
                new_link = f"![[{new_name}.png]]"
                replaced_items.append(f"{full_match} \n   --> {new_link}")
                return new_link
            else:
                print(f"⚠️ 发现未在列表中定义的图片: {standard_name}")
                return full_match

        new_content, count = pattern.subn(replacement_func, content)

        if count > 0:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("-" * 40)
            print(f"🎉 成功！共替换了 {count} 处链接。")
            print("\n部分替换详情：")
            for item in replaced_items[:5]: # 只显示前5个
                print(item)
            if len(replaced_items) > 5:
                print("...")
        else:
            print("-" * 40)
            print("❌ 脚本运行结束，但替换数量为 0。")
            print("这说明正则没有匹配上，请检查原文本格式是否非常特殊（如包含不可见字符）。")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    replace_specific_links()