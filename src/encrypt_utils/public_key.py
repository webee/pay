# coding=utf-8
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_OAEP
import base64

class Key(object):
    def __init__(self, rsa_key):
        self._key = rsa_key
        self._signer = PKCS1_v1_5.new(self._key)
        self._cipher = PKCS1_OAEP.new(self._key)

    def gen_public_key(self):
        """如果此含私钥，则生成相应的公钥
        """
        if self.has_private():
            return Key(self._key.publickey())

    def has_private(self):
        """是否含私钥
        :return:
        """
        return self._key.has_private()

    @property
    def key_data(self):
        """如果此含私钥，则返回私钥内容;
        否则返回公钥内容
        :return:
        """
        return self._key.exportKey()

    def export(self, fout):
        """导出key_data到fout
        :param fout:
        :return:
        """
        fout.write(self.key_data)

    def sign(self, data):
        h = SHA.new()
        h.update(data)

        return self._signer.sign(h)

    def sign_to_base64(self, data):
        return base64.urlsafe_b64encode(self.sign(data))

    def verify(self, data, signature):
        h = SHA.new()
        h.update(data)

        return self._signer.verify(h, signature)

    def verify_from_base64(self, data, signature):
        return self.verify(data, base64.urlsafe_b64decode(signature))

    def encrypt(self, data):
        return self._cipher.encrypt(data)

    def encrypt_to_base64(self, data):
        return base64.urlsafe_b64encode(self.encrypt(data))

    def decrypt(self, ciphertext):
        return self._cipher.decrypt(ciphertext)

    def decrypt_from_base64(self, ciphertext):
        return self._cipher.decrypt(base64.urlsafe_b64decode(ciphertext))


def generate_key(bits=2048):
    rng = Random.new().read

    return Key(RSA.generate(bits, rng))


def load_key(private_key_path):
    return Key(RSA.importKey(open(private_key_path).read()))


def loads_key(key_data):
    return Key(RSA.importKey(key_data))
