from PIL import Image
import math


def embed_message(img_path, message, out_path):
    """更健壮的嵌入函数，支持所有utf-8字符（包括汉字、标点）"""
    try:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 编码消息并添加长度头(4字节)
        message_bytes = message.encode('utf-8')
        data = len(message_bytes).to_bytes(4, 'big') + message_bytes

        # 更安全的校验和计算（对原始utf-8字节）
        checksum = sum(message_bytes) % 256
        data += checksum.to_bytes(1, 'big')

        # 转换为比特流（确保字节顺序正确）
        bit_stream = []
        for byte in data:
            for i in range(7, -1, -1):
                bit_stream.append((byte >> i) & 1)

        # 检查容量
        if len(bit_stream) > img.width * img.height * 3:
            raise ValueError("消息太大，图片容量不足")

        # 嵌入数据（使用更可靠的位操作）
        pixels = img.load()
        bit_ptr = 0
        for y in range(img.height):
            for x in range(img.width):
                if bit_ptr >= len(bit_stream):
                    break

                r, g, b = pixels[x, y]
                if bit_ptr < len(bit_stream):
                    r = (r & 0xFE) | bit_stream[bit_ptr]
                    bit_ptr += 1
                if bit_ptr < len(bit_stream):
                    g = (g & 0xFE) | bit_stream[bit_ptr]
                    bit_ptr += 1
                if bit_ptr < len(bit_stream):
                    b = (b & 0xFE) | bit_stream[bit_ptr]
                    bit_ptr += 1

                pixels[x, y] = (r, g, b)

        # 强制保存为PNG格式（无损）
        if not out_path.lower().endswith('.png'):
            out_path += '.png'
        img.save(out_path, format='PNG')

    except Exception as e:
        raise ValueError(f"嵌入失败: {str(e)}")


def extract_message(img_path):
    """更健壮的提取函数，支持所有utf-8字符（包括汉字、标点）"""
    try:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        pixels = img.load()
        bit_stream = []

        # 读取所有LSB位
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                bit_stream.extend([r & 1, g & 1, b & 1])

        # 提取消息长度（前32位）
        if len(bit_stream) < 32:
            return "错误：数据不完整"

        msg_len = int(''.join(map(str, bit_stream[:32])), 2)

        # 计算需要读取的总比特数
        total_bits = 32 + msg_len * 8 + 8  # 头+数据+校验

        # 提取数据部分
        if len(bit_stream) < total_bits:
            return "错误：数据被截断"

        data_bits = bit_stream[32:32 + msg_len * 8]
        checksum_bits = bit_stream[32 + msg_len * 8:32 + msg_len * 8 + 8]

        # 转换为字节
        data = bytearray()
        for i in range(0, len(data_bits), 8):
            byte = 0
            for bit in data_bits[i:i + 8]:
                byte = (byte << 1) | bit
            data.append(byte)

        # 校验和验证
        received_checksum = 0
        for bit in checksum_bits:
            received_checksum = (received_checksum << 1) | bit
        if sum(data) % 256 != received_checksum:
            try:
                decoded = data.decode('utf-8', errors='replace')
            except Exception:
                decoded = str(data)
            return "警告：校验失败（但尝试解码）\n解码结果：" + decoded

        return data.decode('utf-8')
    except Exception as e:
        return f"提取错误：{str(e)}"
