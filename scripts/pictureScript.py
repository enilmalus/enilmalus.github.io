import re
import os

def convert_wiki_links_to_markdown(file_path):
    """
    读取指定 Markdown 文件，将 ![[xxx.png]] 格式替换为 ![xxx](xxx.png)
    """
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 -> {file_path}")
        return

    try:
        # 读取文件内容 (使用 utf-8 编码)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 定义正则表达式
        # 解释:
        # !\[\[      匹配 literal 的 ![[
        # (.+?)      捕获组 1: 匹配文件名部分 (非贪婪模式)，对应 prompt 中的 xxx
        # \.png      匹配 literal 的 .png (根据你的要求，只针对 png)
        # \]\]       匹配 literal 的 ]]
        pattern = r'!\[\[(.+?)\.png\]\]'
        
        # 定义替换格式
        # \1 代表正则中第一个捕获组的内容 (即文件名 xxx)
        # 结果变成 ![xxx](xxx.png)
        replacement = r'![\1](\1.png)'

        # 执行替换
        new_content, count = re.subn(pattern, replacement, content)

        if count > 0:
            # 将修改后的内容写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"成功处理文件: {file_path}")
            print(f"共替换了 {count} 处图片链接。")
        else:
            print("未发现需要替换的内容。")

    except Exception as e:
        print(f"处理文件时发生错误: {e}")

if __name__ == "__main__":
    # 使用 os.path.join 构建路径，以适应不同操作系统 (Windows/Mac/Linux)
    target_file = os.path.join('content', 'posts', 'Credit Card Scammers Writeup', 'index.md')
    
    # 执行转换
    convert_wiki_links_to_markdown(target_file)