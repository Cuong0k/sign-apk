import zipfile, sys

SRC = 'slagclient.apk'
OUT = 'vpnclient_patched.apk'

OLD_STR = b'xboard=https://xbdemo.slaglab.com'
NEW_STR = b'xboard=https://apk1.jiangsuhk.com'
assert len(OLD_STR) == len(NEW_STR), "length mismatch!"

with zipfile.ZipFile(SRC) as z:
    data = bytearray(z.read('lib/arm64-v8a/libapp.so'))

idx = data.find(OLD_STR)
if idx < 0:
    sys.exit("ERROR: old URL not found")
print(f"Found at offset {idx}")

# Chỉ replace đúng 33 bytes, không đụng gì khác
data[idx:idx+33] = NEW_STR
print(f"Patched: {bytes(data[idx:idx+33])}")

with zipfile.ZipFile(SRC, 'r') as zin:
    with zipfile.ZipFile(OUT, 'w') as zout:
        for item in zin.infolist():
            raw = zin.read(item.filename)
            if item.filename == 'lib/arm64-v8a/libapp.so':
                item.compress_type = zipfile.ZIP_STORED
                zout.writestr(item, data)
                print(f"Stored libapp.so uncompressed ({len(data)//1024}KB)")
            else:
                zout.writestr(item, raw)

print(f"Done: {OUT}")
