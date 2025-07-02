from PIL import Image

# 图片隐写（信息隐藏）工具
# 支持将文本信息嵌入到图片像素中，以及从图片中提取隐藏信息


def embed_message(img_path, message, out_path):
    """
    将文本信息嵌入到图片像素的最低有效位（LSB），生成新图片
    :param img_path: 原始图片路径（建议PNG/BMP等无损格式）
    :param message: 要嵌入的文本信息
    :param out_path: 输出图片路径
    :raises: ValueError 如果消息太长无法嵌入
    """
    img = Image.open(img_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 检查消息长度是否超出图片容量
    max_chars = (img.width * img.height) // 8
    if len(message) > max_chars:
        raise ValueError(f"消息太长，图片最多只能容纳{max_chars}个字符，当前消息长度为{len(message)}")
    
    binary = ''.join(format(ord(c), '08b') for c in message)
    pixels = img.load()
    idx = 0
    for y in range(img.height):
        for x in range(img.width):
            if idx < len(binary):
                r, g, b = pixels[x, y]
                # 修改红色通道的最低位
                r = (r & ~1) | int(binary[idx])
                pixels[x, y] = (r, g, b)
                idx += 1
            else:
                break
        if idx >= len(binary):
            break
    img.save(out_path)


def extract_message(img_path, length):
    """
    从图片像素的最低有效位提取指定长度的文本信息
    :param img_path: 含有隐藏信息的图片路径
    :param length: 要提取的字符数
    :return: 提取出的文本信息
    """
    img = Image.open(img_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = img.load()
    bits = []
    idx = 0
    for y in range(img.height):
        for x in range(img.width):
            if idx < length * 8:
                r, g, b = pixels[x, y]
                bits.append(str(r & 1))
                idx += 1
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars) 