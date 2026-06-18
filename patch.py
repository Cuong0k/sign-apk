import zipfile, sys

SRC = 'slagclient.apk'
OUT = 'vpnclient_patched.apk'

# Patch 1: xboard= prefix (33 chars)
OLD1 = b'xboard=https://xbdemo.slaglab.com'
NEW1 = b'xboard=https://apk1.jiangsuhk.com'

# Patch 2: bare URL dùng cho API calls (26 chars)
OLD2 = b'https://xbdemo.slaglab.com'
NEW2 = b'https://apk1.jiangsuhk.com'

assert len(OLD1)==len(NEW1) and len(OLD2)==len(NEW2), "length mismatch!"

with zipfile.ZipFile(SRC) as z:
    data = bytearray(z.read('lib/arm64-v8a/libapp.so'))

# Patch tất cả occurrences
count = 0
pos = 0
while True:
    idx = data.find(OLD1, pos)
    if idx < 0: break
    data[idx:idx+len(OLD1)] = NEW1
    print(f"Patch1 at {idx}: {bytes(data[idx:idx+len(NEW1)])}")
    count += 1
    pos = idx + len(NEW1)

pos = 0
while True:
    idx = data.find(OLD2, pos)
    if idx < 0: break
    data[idx:idx+len(OLD2)] = NEW2
    print(f"Patch2 at {idx}: {bytes(data[idx:idx+len(NEW2)])}")
    count += 1
    pos = idx + len(NEW2)

print(f"Total patches: {count}")

with zipfile.ZipFile(SRC, 'r') as zin:
    with zipfile.ZipFile(OUT, 'w') as zout:
        for item in zin.infolist():
            raw = zin.read(item.filename)
            if item.filename == 'lib/arm64-v8a/libapp.so':
                item.compress_type = zipfile.ZIP_STORED
                zout.writestr(item, data)
                print(f"Stored libapp.so ({len(data)//1024}KB)")
            else:
                zout.writestr(item, raw)

print(f"Done: {OUT}")
