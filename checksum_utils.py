# checksum_utils.py

import hashlib
import zlib
import logging

def calculate_checksum(file_path, algorithm):
    """
    Calculate the checksum of a file using the specified algorithm.

    Parameters:
        file_path (str): The path to the file.
        algorithm (str): The checksum algorithm to use ('CRC32', 'MD5', 'SHA1', 'SHA256', 'SHA384', 'SHA512', 'BLAKE2B', 'BLAKE2S').

    Returns:
        str: The calculated checksum in uppercase hexadecimal format, or an error string.
    """
    if algorithm == 'CRC32':
        try:
            checksum = 0
            with open(file_path, 'rb') as f:
                while chunk := f.read(4096):
                    checksum = zlib.crc32(chunk, checksum)
            return f"{checksum & 0xFFFFFFFF:08X}"
        except Exception as e:
            logging.error(f"Error calculating CRC32 for {file_path}: {e}")
            return 'ERROR'
    else:
        hash_obj = getattr(hashlib, algorithm.lower(), None)
        if not hash_obj:
            logging.error(f"Unsupported algorithm: {algorithm}")
            return 'UNKNOWN_ALGORITHM'
        hash_instance = hash_obj()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(4096):
                    hash_instance.update(chunk)
            return hash_instance.hexdigest().upper()
        except Exception as e:
            logging.error(f"Error reading file {file_path} for checksum calculation: {e}")
            return 'ERROR'
