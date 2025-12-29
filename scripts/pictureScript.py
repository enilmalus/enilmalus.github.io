import re
import os

def convert_wiki_links_to_markdown(file_path):
    """
    读取指定 Markdown 文件，将 ![[xxx]] 或 ![[xxx.png]] 格式替换为 ![xxx](xxx.png)
    """
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 错误: 找不到文件 -> {file_path}")
        return

    try:
        # 读取文件内容 (使用 utf-8 编码)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 定义更灵活的正则表达式
        # 解释:
        # !\[\[        匹配 literal 的 ![[
        # \s* 允许开头有空格
        # (.+?)        捕获组 1: 文件名主体
        # (?:          非捕获组 (用于匹配后缀)
        #   \.(?:png|jpg|jpeg|gif|bmp)  匹配常见图片后缀
        # )?           ? 表示后缀是可选的 (Obsidian 链接可能没有后缀)
        # \s* 允许结尾有空格
        # \]\]         匹配 literal 的 ]]
        pattern = re.compile(r'!\[\[\s*(.+?)(?:\.(?:png|jpg|jpeg|gif|bmp))?\s*\]\]', re.IGNORECASE)

        # 定义替换回调函数
        def replace_func(match):
            filename = match.group(1) # 获取捕获的文件名 (不含后缀，如果正则调整过)
            # 无论原链接是否有后缀，输出都加上 .png (或者根据需要调整)
            # 如果原文是 ![[P1.png]] -> filename可能是 P1.png (取决于正则贪婪性)，这里简单处理
            
            # 为了保险，先去掉可能被捕获进来的后缀，重新加标准后缀
            root_name = os.path.splitext(filename)[0]
            return f"![{root_name}]({root_name}.png)"

        # 执行替换
        new_content, count = pattern.subn(replace_func, content)

        if count > 0:
            # 将修改后的内容写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 成功处理文件: {file_path}")
            print(f"共替换了 {count} 处图片链接。")
        else:
            print(f"⚠️ 在文件 {file_path} 中未发现符合转换规则的内容。")
            print("-" * 30)
            print("【调试信息】文件中的前 5 个 Wiki 链接如下 (如果存在)：")
            # 查找所有 ![[...]] 格式的内容用于调试
            debug_links = re.findall(r'!\[\[.*?\]\]', content)
            if debug_links:
                for link in debug_links[:5]:
                    print(f"  {link}")
                print(f"共发现 {len(debug_links)} 个 Wiki 链接，但正则未匹配上或无需替换。")
                print("请检查：链接是否已经是标准格式 ![xxx](xxx.png) ？")
            else:
                print("文件中完全没有发现 ![[...]] 格式的文本。")
            print("-" * 30)

    except Exception as e:
        print(f"处理文件时发生错误: {e}")

if __name__ == "__main__":
    # 使用 os.path.join 构建路径
    target_file = os.path.join('content', 'posts', 'Venom Writeup', 'index.md')
    
    # 执行转换
    convert_wiki_links_to_markdown(target_file)