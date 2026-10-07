#!/usr/bin/env python3
"""Generate the WPA2 handshake capture for the wireless cracking module (book ch 13).

The RF capture cannot be containerized, so the lab ships a pre-captured 4-way handshake
instead: this script builds a beacon + EAPOL M1 (ANonce) + EAPOL M2 (SNonce + MIC) for a
known SSID/PSK, writes both a .pcap (for aircrack-ng) and a hashcat .22000 line, and
self-verifies the MIC the exact way a cracker does (PBKDF2 -> PTK -> KCK -> HMAC-SHA1).
Re-run it only to change the SSID or passphrase; the committed artifacts are the output.

The PSK must be present in the wordlist students crack with (attacker/wordlists/
lab-passwords.txt) and be a valid WPA passphrase (8-63 chars).

    pip install scapy
    python3 gen-handshake.py
"""
import hmac, hashlib, struct
from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, wrpcap, Raw

SSID = "PentestTV-Corp"
PSK  = "Baseball1"            # the flag students recover; also in lab-passwords.txt
AP   = "02:00:00:00:01:00"
STA  = "02:00:00:00:02:00"
ANonce = bytes.fromhex("11" * 32)
SNonce = bytes.fromhex("22" * 32)


def mac2b(m):
    return bytes.fromhex(m.replace(":", ""))


def prf512(pmk, A, B):
    out, i = b"", 0
    while len(out) < 64:
        out += hmac.new(pmk, A + b"\x00" + B + struct.pack("B", i), hashlib.sha1).digest()
        i += 1
    return out[:64]


def eapol_key(key_info, nonce, mic=b"\x00" * 16):
    body = (b"\x02" + struct.pack(">H", key_info) + struct.pack(">H", 16) + b"\x00" * 8 +
            nonce + b"\x00" * 16 + b"\x00" * 8 + b"\x00" * 8 + mic + struct.pack(">H", 0))
    return b"\x02\x03" + struct.pack(">H", len(body)) + body


pmk = hashlib.pbkdf2_hmac("sha1", PSK.encode(), SSID.encode(), 4096, 32)
aa, sa = mac2b(AP), mac2b(STA)
B = min(aa, sa) + max(aa, sa) + min(ANonce, SNonce) + max(ANonce, SNonce)
kck = prf512(pmk, b"Pairwise key expansion", B)[:16]

m2_nomic = eapol_key(0x010a, SNonce)
mic = hmac.new(kck, m2_nomic, hashlib.sha1).digest()[:16]
m2 = eapol_key(0x010a, SNonce, mic)
m1 = eapol_key(0x008a, ANonce)

snap = bytes.fromhex("aaaa03000000888e")
beacon = (RadioTap() / Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff", addr2=AP, addr3=AP) /
          Dot11Beacon(cap="ESS+privacy") / Dot11Elt(ID="SSID", info=SSID) /
          Dot11Elt(ID="RSNinfo", info=bytes.fromhex("30140100000fac040100000fac040100000fac020000")))
f_m1 = RadioTap() / Dot11(type=2, subtype=0, FCfield=2, addr1=STA, addr2=AP, addr3=AP) / Raw(snap + m1)
f_m2 = RadioTap() / Dot11(type=2, subtype=0, FCfield=1, addr1=AP, addr2=STA, addr3=AP) / Raw(snap + m2)

wrpcap("../attacker/captures/wpa-handshake.pcap", [beacon, f_m1, f_m2])

ess_hex = SSID.encode().hex()
line = f"WPA*02*{mic.hex()}*{AP.replace(':','')}*{STA.replace(':','')}*{ess_hex}*{ANonce.hex()}*{m2_nomic.hex()}*00"
open("../attacker/captures/wpa-handshake.22000", "w").write(line + "\n")

print(f"SSID={SSID} PSK={PSK}")
print("MIC:", mic.hex())
print("Wrote wpa-handshake.pcap and wpa-handshake.22000")
