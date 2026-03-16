"""加密工具测试。

REQ-0001-005: OpenClaw 凭证管理
"""
import base64
import os

import pytest


class TestCryptoUtils:
    """测试加密工具"""

    def test_encrypt_decrypt_roundtrip(self):
        """REQ-0001-005: 加密后可解密还原"""
        from app.utils.crypto import encrypt, decrypt

        key = os.urandom(32)  # AES-256 key
        plaintext = "my-secret-token-12345"

        ciphertext = encrypt(plaintext, key)
        decrypted = decrypt(ciphertext, key)

        assert decrypted == plaintext
        assert ciphertext != plaintext

    def test_encrypt_produces_different_ciphertext(self):
        """REQ-0001-005: 相同明文每次加密产生不同密文（IV 随机）"""
        from app.utils.crypto import encrypt

        key = os.urandom(32)
        plaintext = "same-plaintext"

        ciphertext1 = encrypt(plaintext, key)
        ciphertext2 = encrypt(plaintext, key)

        assert ciphertext1 != ciphertext2  # IV 不同

    def test_decrypt_with_wrong_key_fails(self):
        """REQ-0001-005: 错误密钥解密失败"""
        from app.utils.crypto import decrypt, encrypt

        key1 = os.urandom(32)
        key2 = os.urandom(32)  # 不同的密钥
        plaintext = "secret-data"

        ciphertext = encrypt(plaintext, key1)

        with pytest.raises(Exception):  # DecryptionError or similar
            decrypt(ciphertext, key2)

    def test_key_from_base64(self):
        """REQ-0001-005: 从 base64 字符串生成密钥"""
        from app.utils.crypto import key_from_base64, key_to_base64

        original_key = os.urandom(32)
        b64 = key_to_base64(original_key)
        restored_key = key_from_base64(b64)

        assert restored_key == original_key

    def test_mask_credential(self):
        """REQ-0001-005: 凭证脱敏"""
        from app.utils.crypto import mask_credential

        assert mask_credential("sk-proj-1234567890abcdef") == "sk-proj-***"
        assert mask_credential("short") == "***"
        assert mask_credential("") == "***"

    def test_encrypt_empty_string(self):
        """REQ-0001-005: 空字符串加密"""
        from app.utils.crypto import decrypt, encrypt

        key = os.urandom(32)
        ciphertext = encrypt("", key)
        decrypted = decrypt(ciphertext, key)

        assert decrypted == ""

    def test_encrypt_unicode(self):
        """REQ-0001-005: Unicode 加密"""
        from app.utils.crypto import decrypt, encrypt

        key = os.urandom(32)
        plaintext = "中文密钥 🔑"

        ciphertext = encrypt(plaintext, key)
        decrypted = decrypt(ciphertext, key)

        assert decrypted == plaintext

    def test_encrypt_long_text(self):
        """REQ-0001-005: 长文本加密"""
        from app.utils.crypto import decrypt, encrypt

        key = os.urandom(32)
        plaintext = "x" * 10000  # 10KB

        ciphertext = encrypt(plaintext, key)
        decrypted = decrypt(ciphertext, key)

        assert decrypted == plaintext
