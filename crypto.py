# encoding: utf-8
import base64
from Crypto.Cipher import AES

# Thanks to fanjindong @ https://www.jianshu.com/p/d18c13681bbc

class aesEncrypt:

    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def pad(self, data):
        # https://stackoverflow.com/questions/14179784/python-encrypting-with-pycrypto-aes
        data = bytes(data, encoding="utf-8")
        length = 16 - (len(data) % 16)
        data += bytes([length]) * length
        return data
    
    def encrypt(self, rawData):
        data = self.pad(rawData)
        chip = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(chip.encrypt(data))
