"""加密工具模块。

REQ-0001-005: OpenClaw 凭证管理

提供 AES-256-GCM 加密/解密和凭证脱敏功能。
"""
import base64
import os
import secrets
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class DecryptionError(Exception):
    """解密失败异常"""

    pass


def encrypt(plaintext: str, key: bytes) -> str:
    """使用 AES-256-GCM 加密

    Args:
        plaintext: 明文字符串
        key: 32 字节加密密钥

    Returns:
        Base64 编码的密文（包含 nonce）
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256")

    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)  # GCM recommended nonce size

    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    # 组合 nonce + ciphertext 并 base64 编码
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode("ascii")


def decrypt(ciphertext: str, key: bytes) -> str:
    """使用 AES-256-GCM 解密

    Args:
        ciphertext: Base64 编码的密文（包含 nonce）
        key: 32 字节加密密钥

    Returns:
        解密后的明文

    Raises:
        DecryptionError: 解密失败（密钥错误或数据损坏）
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256")

    try:
        combined = base64.b64decode(ciphertext.encode("ascii"))
        nonce = combined[:12]
        actual_ciphertext = combined[12:]

        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, actual_ciphertext, None)

        return plaintext.decode("utf-8")
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {e}") from e


def key_to_base64(key: bytes) -> str:
    """将密钥转换为 Base64 字符串

    Args:
        key: 32 字节密钥

    Returns:
        Base64 编码的密钥字符串
    """
    return base64.b64encode(key).decode("ascii")


def key_from_base64(b64: str) -> bytes:
    """从 Base64 字符串还原密钥

    Args:
        b64: Base64 编码的密钥字符串

    Returns:
        32 字节密钥
    """
    key = base64.b64decode(b64.encode("ascii"))
    if len(key) != 32:
        raise ValueError("Invalid key length, expected 32 bytes")
    return key


def generate_key() -> bytes:
    """生成新的 32 字节密钥

    Returns:
        32 字节随机密钥
    """
    return secrets.token_bytes(32)


def mask_credential(credential: str, visible_prefix: int = 8) -> str:
    """脱敏凭证

    Args:
        credential: 原始凭证
        visible_prefix: 可见的前缀字符数

    Returns:
        脱敏后的凭证（前缀 + ***）
    """
    if not credential:
        return "***"

    if len(credential) <= visible_prefix:
        return "***"

    return credential[:visible_prefix] + "***"
