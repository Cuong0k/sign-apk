import zipfile, struct, sys
from pathlib import Path

SRC = 'slagclient.apk'
OUT = 'vpnclient_patched.apk'

OLD_STR = b'xboard=https://xbdemo.slaglab.com'   # 33 bytes
NEW_STR = b'xboard=https://client-user.jiangsuhk.com'  # 40 bytes
OLD_LEN_BYTE = (33 * 2) | 0x80  # 0xC2
NEW_LEN_BYTE = (40 * 2) | 0x80  # 0xD0

with open('lib_patched.so', 'wb') as fo:
    with zipfile.ZipFile(SRC) as z:
        data = bytearray(z.read('lib/arm64-v8a/libapp.so'))

idx = data.find(OLD_STR)
if idx < 0:
    sys.exit("ERROR: old URL not found")
print(f"Found old URL at offset {idx}")
assert data[idx-1] == OLD_LEN_BYTE, f"length byte mismatch: {data[idx-1]:#x}"
# patch length byte + string (33 bytes) + 7 padding = 40 bytes total
data[idx-1] = NEW_LEN_BYTE
data[idx:idx+40] = NEW_STR
print(f"Patched: {bytes(data[idx:idx+40])}")

with open('lib_patched.so', 'wb') as f:
    f.write(data)

# Repack APK: copy tất cả file từ gốc, replace libapp.so với STORED (không nén)
with zipfile.ZipFile(SRC, 'r') as zin:
    with zipfile.ZipFile(OUT, 'w') as zout:
        for item in zin.infolist():
            raw = zin.read(item.filename)
            if item.filename == 'lib/arm64-v8a/libapp.so':
                # PHẢI dùng ZIP_STORED cho .so file (extractNativeLibs=false)
                item.compress_type = zipfile.ZIP_STORED
                zout.writestr(item, data)
                print(f"Stored libapp.so (uncompressed, {len(data)//1024}KB)")
            else:
                # Giữ nguyên compress type của file gốc
                item.compress_type = item.compress_type
                zout.writestr(item, raw)

print(f"Done: {OUT}")
import os; print(f"Size: {os.path.getsize(OUT)//1024//1024}MB")
