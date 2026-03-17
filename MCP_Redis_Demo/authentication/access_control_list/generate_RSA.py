"""
生成一对RSA密钥，将私钥以PEM格式存储
"""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import hashlib

# 生成2048位的RSA私钥
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# 序列化私钥为PEM格式
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# 获取公钥并序列化为PEM格式
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# 生成公钥的MD5哈希值
der_data = public_key.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
md5_hash = hashlib.md5(der_data).hexdigest()
print(md5_hash)

# 保存私钥到文件 文件名为公钥MD5
with open(f"./private_key/{md5_hash}.pem", "wb") as f:
    f.write(private_pem)

print("RSA密钥对已生成：")
print(f"私钥 -> ./private_key/{md5_hash}.pem")

# 从pem文件读取私钥
# with open(f"./private_key/{md5_hash}.pem", "rb") as key_file:
#     private_key_2 = serialization.load_pem_private_key(
#         key_file.read(),
#         password=None
#     )