import struct
import os
import sys
import ctypes
import zlib
import tempfile

class ZFSReader:
    def __init__(self, zfs_path):
        self.zfs_path = zfs_path
        self.lzo_dll = self._load_lzo_dll()
        self.records = []
        self.header = {}
        self.f = None

    def _load_lzo_dll(self):
        try:
            addon_dir = os.path.dirname(__file__)
            dll_path = os.path.join(addon_dir, 'lib', 'lzo_bridge.dll')
            if not os.path.exists(dll_path):
                print(f"ZFSReader: DLL not found at {dll_path}")
                return None
            
            lzo_dll = ctypes.WinDLL(dll_path)
            lzo_dll.lzo_init_dll.restype = ctypes.c_int
            
            lzo_dll.compress_buffer.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
            lzo_dll.compress_buffer.restype = ctypes.c_int
            
            lzo_dll.decompress_buffer.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
            lzo_dll.decompress_buffer.restype = ctypes.c_int
            
            if lzo_dll.lzo_init_dll() != 0:
                print("LZO Init failed")
                return None
            return lzo_dll
        except Exception as e:
            print(f"ZFSReader: Failed to load DLL: {e}")
            return None

    def open(self):
        if self.f: self.close()
        self.f = open(self.zfs_path, 'rb')
        self.records = []
        
        # Read Header
        h = struct.unpack('<4sIIIIII', self.f.read(28))
        self.header = {
            'sig': h[0],
            'version': h[1],
            'name_len': h[2],
            'entries_per_block': h[3],
            'total_files': h[4],
            'key': h[5],
            'first_tab': h[6]
        }
        
        if self.header['sig'] != b'ZFSF':
            self.close()
            raise Exception("Invalid ZFS signature")

        self.f.seek(0, os.SEEK_END)
        f_size = self.f.tell()
        
        dir_key = self.header['key']
        next_tab = self.header['first_tab']
        limit = self.header['total_files']
        
        # Simple decryption for start pointer if needed
        if next_tab >= f_size and dir_key != 0:
            dec_next = struct.unpack('<I', self.xor_data(struct.pack('<I', next_tab), dir_key))[0]
            if dec_next < f_size:
                next_tab = dec_next

        while next_tab != 0 and len(self.records) < limit:
            if next_tab < 0 or next_tab >= f_size: break
            self.f.seek(next_tab)
            
            b_head = self.f.read(4)
            if len(b_head) < 4: break
            
            raw_next = struct.unpack('<I', b_head)[0]
            block_encrypted = False
            
            if raw_next >= f_size and dir_key != 0:
                dec_head = self.xor_data(b_head, dir_key)
                dec_next = struct.unpack('<I', dec_head)[0]
                if dec_next == 0 or dec_next < f_size:
                    b_head = dec_head
                    next_tab = dec_next
                    block_encrypted = True
                else:
                    next_tab = raw_next
            else:
                next_tab = raw_next
            
            for _ in range(self.header['entries_per_block']):
                if len(self.records) >= limit: break
                fmt = f'<{self.header["name_len"]}sIIIII'
                rec_size = struct.calcsize(fmt)
                chunk = self.f.read(rec_size)
                if len(chunk) < rec_size: break
                
                if block_encrypted:
                    chunk = self.xor_data(chunk, dir_key)

                name_raw, offset, rnum, c_size, time, flags = struct.unpack(fmt, chunk)
                name = name_raw.split(b'\x00')[0].decode('ascii', errors='ignore').strip()
                if not name: continue

                u_size = flags >> 8
                p_size = c_size
                is_encrypted = self.header['key'] != 0
                
                if is_encrypted:
                    curr_pos = self.f.tell()
                    self.f.seek(offset)
                    p_byte_raw = self.f.read(1)
                    if p_byte_raw:
                        p_byte = p_byte_raw[0]
                        p_size ^= p_byte
                        u_size ^= p_byte
                    self.f.seek(curr_pos)

                self.records.append({
                    'name': name,
                    'ext': os.path.splitext(name)[1].lower(),
                    'size': u_size,
                    'packed': p_size,
                    'method': flags & 0x6, # 2 = LZO1X, 4 = LZO1Y
                    'offset': offset,
                    'flags': flags,
                    'encrypted': is_encrypted
                })

    def close(self):
        if self.f:
            self.f.close()
            self.f = None

    def build_key_stream(self, key_val):
        if not key_val: return b""
        if isinstance(key_val, int):
            return struct.pack('<I', key_val & 0xFFFFFFFF)
        pwd_bytes = key_val.encode('utf-8')
        header_key = zlib.crc32(pwd_bytes) & 0xFFFFFFFF
        return bytes([len(pwd_bytes)]) + struct.pack('<I', header_key) + pwd_bytes

    def xor_data(self, data, key_val):
        key_stream = self.build_key_stream(key_val)
        if not key_stream: return data
        res = bytearray(len(data))
        k_len = len(key_stream)
        for i in range(len(data)):
            res[i] = data[i] ^ key_stream[i % k_len]
        return bytes(res)

    def extract(self, filename, out_dir):
        rec = next((r for r in self.records if r['name'].lower() == filename.lower()), None)
        if not rec: return None
        
        self.f.seek(rec['offset'])
        key = self.header['key']
        is_encrypted = rec['encrypted']
        
        if is_encrypted:
            # XOR decryption for Redux ZFS - includes 2-byte prefix
            encrypted_data = self.f.read(rec['packed'] + 2)
            decrypted_block = self.xor_data(encrypted_data, key)
            data = decrypted_block[2:]
        else:
            data = self.f.read(rec['packed'])

        # Decompress
        if rec['method'] and self.lzo_dll:
            algo = 2 if (rec['method'] & 0x0002) else 4
            u_size = rec['size']
            dst_size = max(u_size, 10 * 1024 * 1024) 
            dst = ctypes.create_string_buffer(dst_size + 4096)
            d_len = ctypes.c_size_t(u_size)

            try:
                ret = self.lzo_dll.decompress_buffer(algo, data, ctypes.c_size_t(len(data)), dst, ctypes.byref(d_len))
                if ret == 0:
                    content = dst.raw[:d_len.value]
                else:
                    print(f"ZFSReader: Decompression error {ret} for {filename}")
                    content = data
            except Exception as e:
                print(f"ZFSReader: Decompression crash for {filename}: {e}")
                content = data
        else:
            content = data

        out_path = os.path.join(out_dir, rec['name'])
        with open(out_path, 'wb') as out_f:
            out_f.write(content)
        return out_path

    def list_files(self):
        return [r['name'] for r in self.records]
