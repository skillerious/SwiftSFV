# checksum_utils.py

import hashlib
import zlib
import logging

def calculate_checksum(file_path, algorithm):
    """
    Calculate the checksum of a file using the specified algorithm.

    Parameters:
        file_path (str): The path to the file.
        algorithm (str): The checksum algorithm to use.

    Returns:
        str: The calculated checksum in hexadecimal format.
    """
    logging.debug(f"Calculating checksum for {file_path} using {algorithm} algorithm.")

    if algorithm == "CRC32":
        return calculate_crc32(file_path)
    else:
        try:
            hash_func = get_hash_function(algorithm)
        except ValueError as e:
            logging.error(str(e))
            raise

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        checksum = hash_func.hexdigest()
        logging.debug(f"Checksum for {file_path}: {checksum}")
        return checksum

def calculate_crc32(file_path):
    """
    Calculate the CRC32 checksum of a file.

    Parameters:
        file_path (str): The path to the file.

    Returns:
        str: The calculated CRC32 checksum in hexadecimal format.
    """
    logging.debug(f"Calculating CRC32 checksum for {file_path}.")
    buf_size = 65536  # Read in chunks of 64KB
    crc32 = 0
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            crc32 = zlib.crc32(data, crc32)
    # Format as unsigned integer and convert to uppercase hexadecimal
    checksum = format(crc32 & 0xFFFFFFFF, '08X')
    logging.debug(f"CRC32 checksum for {file_path}: {checksum}")
    return checksum

def get_hash_function(algorithm):
    """
    Get the hash function corresponding to the specified algorithm.

    Parameters:
        algorithm (str): The name of the algorithm.

    Returns:
        hashlib._hashlib.HASH: The hash function object.

    Raises:
        ValueError: If the algorithm is not supported.
    """
    algorithm = algorithm.lower()
    if algorithm in hashlib.algorithms_available:
        return hashlib.new(algorithm)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
