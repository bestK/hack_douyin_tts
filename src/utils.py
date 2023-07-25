def random_ip():
    return '.'.join(str(random.randint(1, 255)) for _ in range(4))


import random
from base64 import b64decode, b64encode
from datetime import datetime
from string import Template
from urllib.parse import quote

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import config


def encrypt_aes_ecb(data, key):
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    data_bytes = data.encode()
    ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
    return b64encode(ct_bytes).decode()


def decrypt_aes_ecb(encrypted_data, key):
    encrypted_data = b64decode(encrypted_data)
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode()


def encrypted_params(text: str, zbid: str, conf: config.TTS_CONFIG):
    now = int(datetime.now().timestamp()) * 1000

    template = Template(conf.api_params)
    plaintText = template.substitute(now=now, text=text, zbid=zbid)
    encrypted_data = encrypt_aes_ecb(plaintText, conf.api_req_key)
    encrypted_data = quote(encrypted_data)

    reqForm = {"req": encrypted_data, "sec": conf.api_sec}
    body = "&".join(f"{key}={value}" for key, value in reqForm.items())

    return plaintText, body
