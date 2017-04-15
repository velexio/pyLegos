import math
import hashlib
from os import urandom
from base64 import b64encode


def get_salt():
    rb = urandom(32)
    tok = b64encode(rb).decode('utf-8')
    return tok

def hashp(p):
    if not type(p) is bytes:
        p = p.encode()
    ho = hashlib.sha512(p)
    hd = ho.digest()
    return hd

s1 = get_salt()
print('Salt: '+str(s1))
print('Salt Len: '+str(len(s1)))

p1 = 'Gart5TAG'
p2 = 'M0racl3!1234'
v1 = math.factorial(round(len(p1)/2.2))
v2 = math.factorial(round(len(p2)/2.2))
print('V1: '+str(v1)+' V2: '+str(v2))
lv1 = round(math.log1p(v1))
lv2 = round(math.log1p(v2))
p1h = hashp(p1)
p2h = hashp(p2)
print('HP1: '+str(p1h)+' HP2: '+str(p2h))
print('Len: '+str(len(p1h)))
gcd = math.gcd(v1, v2)
print('gcd: '+str(gcd))
m = int(math.fabs(lv1 - lv2))
print('M: '+str(m))
cp = p1[:6]+p2[-6:]
cp = cp.encode()
print(str(cp))


sa=0
ncs = []
for c in cp:
    if c != 32:
        ncs.append(chr(c*m))
dp=u"\u0047"+u'\u0307'+u'\u0043'+u'\u0307'
print('NCS: '+str(ncs))
for l in ncs:
    ordv = ord(l)
    if ord(l) < 33:
        l = chr(35)
    if ord(l) > 126 and ord(l) < 161:
        l = u'Ä'
    dp += l
dp+=u'\u0076'+u'\u0323'+u'\u0078'

print('DynPass: '+str(dp).strip(' '))
