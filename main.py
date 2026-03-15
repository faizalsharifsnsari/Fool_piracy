import os
import sys
import random
import hashlib
import struct

BLOCK_SIZE = 1024

def get_seed_from_key(key: str) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest(), 16)

def generate_permutation(length: int, key: str):
    rng = random.Random(get_seed_from_key(key))
    indices = list(range(length))
    rng.shuffle(indices)
    return indices

def pad_data(data: bytes):
    original_size = len(data)
    padding_needed = (BLOCK_SIZE - (original_size % BLOCK_SIZE)) % BLOCK_SIZE
    padded_data = data + b'\x00' * padding_needed
    return padded_data, original_size

def split_blocks(data: bytes):
    return [data[i:i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]

def scramble(input_path: str, output_path: str, key: str):
    with open(input_path, "rb") as f:
        data = f.read()
    padded_data, original_size = pad_data(data)
    blocks = split_blocks(padded_data)
    permutation = generate_permutation(len(blocks), key)
    scrambled_blocks = [blocks[i] for i in permutation]

    with open(output_path, "wb") as f:
        # Write original size as 8-byte header
        f.write(struct.pack(">Q", original_size))
        for block in scrambled_blocks:
            f.write(block)
    print("Binary file scrambled successfully.")

def restore(input_path: str, output_path: str, key: str):

    with open(input_path, "rb") as f:
        original_size = struct.unpack(">Q", f.read(8))[0]
        data = f.read()
    blocks = split_blocks(data)
    permutation = generate_permutation(len(blocks), key)
    restored_blocks = [None] * len(blocks)
    for i, perm_index in enumerate(permutation):
        restored_blocks[perm_index] = blocks[i]

    restored_data = b''.join(restored_blocks)
    restored_data = restored_data[:original_size]
    with open(output_path, "wb") as f:
        f.write(restored_data)
    os.chmod(output_path, 0o775)
    print("Binary file restored successfully with executable permissions.")

def main():
    if len(sys.argv) < 6:
        print("Usage:")
        print("Scramble: python3 main.py file.exe -S output.bin -K KEY")
        print("Restore : python3 main.py file.bin -R output.exe -K KEY")
        sys.exit(1)
    input_file = sys.argv[1]
    key = sys.argv[sys.argv.index("-K") + 1]

    if "-S" in sys.argv:
        output_file = sys.argv[sys.argv.index("-S") + 1]
        scramble(input_file, output_file, key)
    elif "-R" in sys.argv:
        output_file = sys.argv[sys.argv.index("-R") + 1]
        restore(input_file, output_file, key)
    else:
        print("Error: Must specify -S or -R.")

if __name__ == "__main__":
    main()