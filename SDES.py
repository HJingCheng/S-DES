import base64
import concurrent.futures
from itertools import product
import time

# 实现SDES类
class SDES:
    def __init__(self, key):
        self.key = key
        self.k1, self.k2 = self.generate_subkeys(key)

    # 根据给定的置换表对输入的比特串进行置换
    @staticmethod
    def permute(input_bits, permutation_table):
        output_bits = [input_bits[i - 1] for i in permutation_table]
        return output_bits

    # 对给定的比特串进行循环左移
    @staticmethod
    def left_shift(bits, shift_amount):
        return bits[shift_amount:] + bits[:shift_amount]

    # 对给定的比特串进行异或操作
    @staticmethod
    def xor(bits1, bits2):
        return [bit1 ^ bit2 for bit1, bit2 in zip(bits1, bits2)]

    # 将4bit转换成8bit
    @staticmethod
    def EP_expansion(bits):
        EPBox = [4, 1, 2, 3, 2, 3, 4, 1]
        return SDES.permute(bits, EPBox)

    # 根据S-Box表进行查找
    @staticmethod
    def SBox_lookup(bits, SBox):
        row = int(f"{bits[0]}{bits[3]}", 2)
        col = int(f"{bits[1]}{bits[2]}", 2)
        return format(SBox[row][col], '02b')

    # F轮换函数
    def f_function(self, bits, subkey):
        SBox1 = [(1, 0, 3, 2), (3, 2, 1, 0), (0, 2, 1, 3), (3, 1, 0, 2)]
        SBox2 = [(0, 1, 2, 3), (2, 3, 1, 0), (3, 0, 1, 2), (2, 1, 0, 3)]
        P4 = [2, 4, 3, 1]
        expanded_bits = SDES.EP_expansion(bits)     # 4bit -> 8bit
        xor_bits = SDES.xor(expanded_bits, subkey)  # 和子密钥进行异或
        left_bits, right_bits = xor_bits[:4], xor_bits[4:]  # 分成两部分
        sbox1_output = SDES.SBox_lookup(left_bits, SBox1)   # 查找S-Box1
        sbox2_output = SDES.SBox_lookup(right_bits, SBox2)  # 查找S-Box2
        output = SDES.permute(list(map(int, sbox1_output + sbox2_output)), P4)      # 4bit -> 4bit
        return output

    # 生成子密钥
    def generate_subkeys(self, key):
        P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
        P8 = [6, 3, 7, 4, 8, 5, 10, 9]
        permuted_key = SDES.permute(key, P10)   # 进行 P10 置换
        left_half = permuted_key[:5]    # 分成两部分
        right_half = permuted_key[5:]   # 分成两部分
        LS1_left = SDES.left_shift(left_half, 1)    # 左移
        LS1_right = SDES.left_shift(right_half, 1)  # 左移
        k1 = SDES.permute(LS1_left + LS1_right, P8)     # 进行置换
        LS2_left = SDES.left_shift(LS1_left, 1)    # 左移
        LS2_right = SDES.left_shift(LS1_right, 1)   # 左移
        k2 = SDES.permute(LS2_left + LS2_right, P8)    # 进行 P8 置换
        return k1, k2

    # 加密
    def encrypt(self, plaintext):
        IP = [2, 6, 3, 1, 4, 8, 5, 7]
        IP_inv = [4, 1, 3, 5, 7, 2, 8, 6]
        permuted_bits = SDES.permute(plaintext, IP)     # 进行 IP 置换
        L, R = permuted_bits[:4], permuted_bits[4:]     # 分成两部分
        new_R = SDES.xor(self.f_function(R, self.k1), L)    # F轮换
        L, R = R, new_R     # 交换
        new_R = SDES.xor(self.f_function(R, self.k2), L)    # F轮换
        ciphertext = SDES.permute(new_R + R, IP_inv)    # 进行 IP-1 置换
        return ciphertext   # 返回密文

    # 解密
    def decrypt(self, ciphertext):
        IP = [2, 6, 3, 1, 4, 8, 5, 7]
        IP_inv = [4, 1, 3, 5, 7, 2, 8, 6]
        permuted_bits = SDES.permute(ciphertext, IP)    # 进行 IP 置换
        L, R = permuted_bits[:4], permuted_bits[4:]     # 分成两部分
        new_R = SDES.xor(self.f_function(R, self.k2), L)    # F轮换
        L, R = R, new_R     # 交换
        new_R = SDES.xor(self.f_function(R, self.k1), L)    # F轮换
        plaintext = SDES.permute(new_R + R, IP_inv)     # 进行 IP-1 置换
        return plaintext    # 返回明文

    def encrypt_string(self, plaintext_str):
        ciphertext_bytes = []
        for char in plaintext_str:
            ascii_value = ord(char)
            binary_repr = [int(bit) for bit in format(ascii_value, '08b')]
            encrypted_block = self.encrypt(binary_repr)
            encrypted_byte = int("".join(map(str, encrypted_block)), 2)
            ciphertext_bytes.append(encrypted_byte)
        return "".join(chr(byte) for byte in ciphertext_bytes)

    def decrypt_string(self, ciphertext_str):
        decrypted_bytes = []
        for char in ciphertext_str:
            ascii_value = ord(char)
            binary_repr = [int(bit) for bit in format(ascii_value, '08b')]
            decrypted_block = self.decrypt(binary_repr)
            decrypted_byte = int("".join(map(str, decrypted_block)), 2)
            decrypted_bytes.append(decrypted_byte)
        return "".join(chr(byte) for byte in decrypted_bytes)

    # # 加密字符串
    # def encrypt_string(self, plaintext_str):
    #     ciphertext_bytes = bytearray()
    #     for char in plaintext_str:
    #         ascii_value = ord(char)
    #         binary_repr = [int(bit) for bit in format(ascii_value, '08b')]
    #         encrypted_block = self.encrypt(binary_repr)
    #         encrypted_byte = int("".join(map(str, encrypted_block)), 2)
    #         ciphertext_bytes.append(encrypted_byte)
    #     return base64.b64encode(ciphertext_bytes).decode('utf-8')   # 使用base64编码
    #
    # # 解密字符串
    # def decrypt_string(self, ciphertext_str):
    #     decrypted_bytes = bytearray()
    #     ciphertext_bytes = base64.b64decode(ciphertext_str)     # 使用base64解码
    #     for byte in ciphertext_bytes:
    #         binary_repr = [int(bit) for bit in format(byte, '08b')]
    #         decrypted_block = self.decrypt(binary_repr)
    #         decrypted_byte = int("".join(map(str, decrypted_block)), 2)
    #         decrypted_bytes.append(decrypted_byte)
    #     return decrypted_bytes.decode('utf-8')

# 暴力破解
def brute_force(pairs):
    start_time = time.time()  # 记录开始时间

    def try_key(key_bits):
        key = list(key_bits)
        sdes = SDES(key)
        if all(sdes.decrypt(ciphertext) == plaintext for plaintext, ciphertext in pairs):
            return key

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(try_key, key_bits) for key_bits in product([0, 1], repeat=10)]

        for future in concurrent.futures.as_completed(futures):
            key = future.result()
            if key is not None:
                end_time = time.time()  # 记录结束时间
                time_taken = end_time - start_time  # 计算所花费的时间
                return key, time_taken  # 返回找到的密钥和所花费的时间

    return None, None  # 如果没有找到密钥，返回 None


def brute_force_all(pairs):
    start_time = time.time()  # 记录开始时间
    keys_found = []  # 用于存储找到的所有密钥

    def try_key(key_bits):
        key = list(key_bits)
        sdes = SDES(key)
        if all(sdes.decrypt(ciphertext) == plaintext for plaintext, ciphertext in pairs):
            return key

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(try_key, key_bits) for key_bits in product([0, 1], repeat=10)]

        for future in concurrent.futures.as_completed(futures):
            key = future.result()
            if key is not None:
                keys_found.append(key)

    end_time = time.time()  # 记录结束时间
    time_taken = end_time - start_time  # 计算所花费的时间
    return keys_found, time_taken  # 返回找到的所有密钥和所花费的时间

# 进行测试
if __name__ == '__main__':
    # sdes = SDES(key=[1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
    # plaintext = [1, 1, 1, 1, 1, 1, 1, 1]
    # ciphertext = sdes.encrypt(plaintext)
    # decrypted_text = sdes.decrypt(ciphertext)
    # print(f"Plaintext: {plaintext}")
    # print(f"Ciphertext: {ciphertext}")
    # print(f"Decrypted text: {decrypted_text}")
    #
    # plaintext_str = "AAA"
    # ciphertext_str = sdes.encrypt_string(plaintext_str)
    # decrypted_str = sdes.decrypt_string(ciphertext_str)
    # print(f"Plaintext: {plaintext_str}")
    # print(f"Ciphertext: {ciphertext_str}")
    # print(f"Decrypted text: {decrypted_str}")
    #
    # pairs = [
    #     {
    #         'plaintext': [1, 1, 1, 1, 1, 1, 1, 1],
    #         'ciphertext': [1, 1, 1, 0, 1, 0, 0, 0],
    #     }
    # ]
    # # 将明文和密文字符串转换为整数列表
    # pairs = [(pair['plaintext'], pair['ciphertext']) for pair in pairs]
    # print(f"Pairs: {pairs}")
    # print(f"Brute force: {brute_force(pairs)}")
    #
    # print(f"Brute force all: {brute_force_all(pairs)}")
    sdes = SDES(key=[1, 0, 1, 0, 0, 0, 0, 0, 1, 0])
    text = [0, 0, 0, 0, 0, 0, 0, 0]
    ciphertext = sdes.encrypt(text)
    print(f"Ciphertext: {ciphertext}")
    decrypted_text = sdes.decrypt(ciphertext)
    print(f"Decrypted text: {decrypted_text}")
    print(f"Plaintext: {text}")
    print(f"Key: {sdes.key}")
