import base64, sys
from Crypto.Cipher import DES3

secret = base64.decodestring(sys.argv[1])
password = base64.decodestring(sys.argv[2])

print DES3.new(secret[:24], DES3.MODE_CBC, secret[24:]).decrypt(password)
