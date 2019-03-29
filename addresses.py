import hashlib
import os
import ecdsa
import ecdsa.der
import ecdsa.util
from bitcoin import *
import json
import requests

b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

secure_key_length=60


def base58encode(n):
    result = ''
    while n > 0:
        result = b58[n%58] + result
        n /= 58
    return result


def base256decode(s):
    result = 0
    for c in s:
        result = result * 256 + ord(c)
    return result


def countLeadingChars(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count


def base58CheckEncode(version, payload):
    s = chr(version) + payload
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    result = s + checksum
    leadingZeros = countLeadingChars(result, '\0')
    return '1' * leadingZeros + base58encode(base256decode(result))


def privateKeyToWif(key_hex):
    return base58CheckEncode(0x80, key_hex.decode('hex'))


def privateKeyToPublicKey(s):
    sk = ecdsa.SigningKey.from_string(s.decode('hex'), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    return ('\04' + sk.verifying_key.to_string()).encode('hex')


def pubKeyToAddr(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(s.decode('hex')).digest())
    return base58CheckEncode(0, ripemd160.digest())


def keyToAddr(s):
    return pubKeyToAddr(privateKeyToPublicKey(s))


def generate_privatekey(phrase):
    keysum=phrase
    secret_exponent=hashlib.sha256(keysum).hexdigest()
    privkey=privateKeyToWif(secret_exponent)
    return privkey


def generate_publickey(phrase):
    keysum=phrase
    secret_exponent=hashlib.sha256(keysum).hexdigest()
    public_key = privateKeyToPublicKey(secret_exponent)
    return public_key


def generate_publicaddress(phrase):
    public_key = generate_publickey(phrase)
    public_address = pubKeyToAddr(public_key)
    return public_address


def random_address_pair():
    a = str(os.urandom(secure_key_length))
    b = str(hashlib.sha256(a).hexdigest())
    priv = generate_privatekey(b)
    pub = generate_publickey(b)
    pubaddr = generate_publicaddress(b)
    return priv, pub, pubaddr
