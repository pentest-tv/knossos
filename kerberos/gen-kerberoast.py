#!/usr/bin/env python3
"""Generate the Kerberoast TGS-REP (etype 23 / RC4-HMAC) hash for the offline Kerberoasting
module, in hashcat -m 13100 / john krb5tgs format, for a known service-account password.

Why this works where a naive version does not: hashcat/John do NOT just verify the RC4-HMAC
checksum. After decrypting with a candidate key they also run a structural sanity check on
the plaintext, which must be a well-formed EncTicketPart ASN.1 blob (APPLICATION 3, 0x63...).
A hash whose plaintext is junk (e.g. zero padding) can have a perfectly valid checksum and
still be reported as "not cracked", because the structure check rejects it before the match
is accepted. So the plaintext here is a genuine EncTicketPart skeleton, lifted from a known-
good ticket, with a freshly randomised 16-byte session key so the ciphertext is our own.

The RC4-HMAC construction below is byte-for-byte identical to impacket's _RC4.encrypt for
key usage 2 (the TGS ticket enc-part): ki = HMAC-MD5(NTLM, le32(2)), checksum over
confounder+plaintext, ke = HMAC-MD5(ki, checksum), cipher = checksum + RC4(ke, blob). The
output was validated in two ways: (1) it decrypts and passes the EncTicketPart structure
check, and (2) the identical pipeline recovers "hashcat" from hashcat's official -m 13100
example hash. Dependency-free on purpose so it runs anywhere.

Re-run only to change the service account or password; the committed artifact is
attacker/captures/kerberoast.txt. The password must be in attacker/wordlists/lab-passwords.txt.
"""
import struct, hmac, hashlib, os

PASSWORD = "Winter2024"            # the flag students recover; also in lab-passwords.txt
USER = "svc_sql"
REALM = "PENTESTTV.LOCAL"
SPN = "MSSQLSvc/db-01.pentesttv.local"   # no :port -> no colon (John splits login:hash on ':')

# A real EncTicketPart ASN.1 skeleton (APPLICATION 3 / 0x63). The 16 bytes after the
# "a1 12 04 10" session-key header are re-randomised below; the rest (flags, realm, cname,
# transited, timestamps) is opaque filler the cracker never inspects but must be well-formed.
TEMPLATE = bytes.fromhex(
    "6381b03081ada00703050050a00000"
    "a11b3019a003020117a112041058e0d77776e8b8e03991f2966939222a"
    "a2171b154d594b5242544553542e434f4e544f534f2e434f4d"
    "a3133011a003020102a10a30081b067472616e6365"
    "a40b3009a003020101a1020400"
    "a511180f32303136303231353134343735305a"
    "a611180f32303136303231353134343735305a"
    "a711180f32303136303231363030343735305a"
    "a811180f32303136303232323134343735305a"
)
# Offset of the 16-byte session key value within TEMPLATE (right after "a1 12 04 10").
_KEY_HDR = bytes.fromhex("a1120410")
_koff = TEMPLATE.index(_KEY_HDR) + len(_KEY_HDR)
plaintext = TEMPLATE[:_koff] + os.urandom(16) + TEMPLATE[_koff + 16:]
assert len(plaintext) == len(TEMPLATE)
assert plaintext[0] == 0x63                       # APPLICATION 3 == EncTicketPart


def md4(data: bytes) -> bytes:
    def lrot(x, n): return ((x << n) | (x >> (32 - n))) & 0xffffffff
    msg = bytearray(data); ml = len(msg) * 8; msg.append(0x80)
    while len(msg) % 64 != 56: msg.append(0)
    msg += struct.pack('<Q', ml)
    A, B, C, D = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
    for off in range(0, len(msg), 64):
        X = list(struct.unpack('<16I', msg[off:off + 64])); a, b, c, d = A, B, C, D
        F = lambda x, y, z: (x & y) | (~x & z)
        G = lambda x, y, z: (x & y) | (x & z) | (y & z)
        H = lambda x, y, z: x ^ y ^ z
        for i in [0, 4, 8, 12]:
            a = lrot((a + F(b, c, d) + X[i]) & 0xffffffff, 3); d = lrot((d + F(a, b, c) + X[i + 1]) & 0xffffffff, 7)
            c = lrot((c + F(d, a, b) + X[i + 2]) & 0xffffffff, 11); b = lrot((b + F(c, d, a) + X[i + 3]) & 0xffffffff, 19)
        for i in [0, 1, 2, 3]:
            a = lrot((a + G(b, c, d) + X[i] + 0x5a827999) & 0xffffffff, 3); d = lrot((d + G(a, b, c) + X[i + 4] + 0x5a827999) & 0xffffffff, 5)
            c = lrot((c + G(d, a, b) + X[i + 8] + 0x5a827999) & 0xffffffff, 9); b = lrot((b + G(c, d, a) + X[i + 12] + 0x5a827999) & 0xffffffff, 13)
        for i in [0, 2, 1, 3]:
            a = lrot((a + H(b, c, d) + X[i] + 0x6ed9eba1) & 0xffffffff, 3); d = lrot((d + H(a, b, c) + X[i + 8] + 0x6ed9eba1) & 0xffffffff, 9)
            c = lrot((c + H(d, a, b) + X[i + 4] + 0x6ed9eba1) & 0xffffffff, 11); b = lrot((b + H(c, d, a) + X[i + 12] + 0x6ed9eba1) & 0xffffffff, 15)
        A = (A + a) & 0xffffffff; B = (B + b) & 0xffffffff; C = (C + c) & 0xffffffff; D = (D + d) & 0xffffffff
    return struct.pack('<4I', A, B, C, D)


def rc4(key, data):
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xff; S[i], S[j] = S[j], S[i]
    out = bytearray(); i = j = 0
    for b in data:
        i = (i + 1) & 0xff; j = (j + S[i]) & 0xff; S[i], S[j] = S[j], S[i]
        out.append(b ^ S[(S[i] + S[j]) & 0xff])
    return bytes(out)


def rc4hmac_encrypt(nt, usage, plaintext, confounder):
    k1 = hmac.new(nt, struct.pack('<I', usage), hashlib.md5).digest()
    blob = confounder + plaintext
    checksum = hmac.new(k1, blob, hashlib.md5).digest()
    k3 = hmac.new(k1, checksum, hashlib.md5).digest()
    return checksum + rc4(k3, blob)


def verify(nt, usage, checksum, edata):
    k1 = hmac.new(nt, struct.pack('<I', usage), hashlib.md5).digest()
    k3 = hmac.new(k1, checksum, hashlib.md5).digest()
    dec = rc4(k3, edata)
    if hmac.new(k1, dec, hashlib.md5).digest() != checksum:
        return False
    return dec[8:9] == b"\x63"          # confounder(8) stripped -> EncTicketPart tag


nt = md4(PASSWORD.encode('utf-16-le'))
cipher = rc4hmac_encrypt(nt, 2, plaintext, os.urandom(8))   # key usage 2 = TGS ticket enc-part
checksum, edata = cipher[:16], cipher[16:]
assert verify(nt, 2, checksum, edata), "self-verify failed (checksum or structure)"

h = f"$krb5tgs$23$*{USER}${REALM}${SPN}*${checksum.hex()}${edata.hex()}"
assert ":" not in h
open("../attacker/captures/kerberoast.txt", "w").write(h + "\n")
print("password:", PASSWORD, "-> wrote attacker/captures/kerberoast.txt")
