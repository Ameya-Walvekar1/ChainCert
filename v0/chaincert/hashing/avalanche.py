"""
Avalanche Effect Analysis & Bitwise Hamming Metrics Module.
Demonstrates the cryptographic property where a single-character change in input
causes a drastic, unpredictable change in SHA-256 digest output.
"""

from typing import Dict, Any


def hex_to_bin_256(hex_str: str) -> str:
    """Convert 64-char hexadecimal string into 256-bit binary string."""
    return bin(int(hex_str, 16))[2:].zfill(256)


def compute_hamming_distance(binary_a: str, binary_b: str) -> int:
    """Count number of bit positions where binary_a and binary_b differ."""
    return sum(b1 != b2 for b1, b2 in zip(binary_a, binary_b))


def compute_avalanche_effect(hash_a: str, hash_b: str) -> Dict[str, Any]:
    """
    Compute avalanche effect metrics between two SHA-256 hashes.

    Args:
        hash_a (str): First SHA-256 hex string (64 chars).
        hash_b (str): Second SHA-256 hex string (64 chars).

    Returns:
        Dict[str, Any]: Avalanche metrics including Hamming distance, bit flip ratio, and bit diff.
    """
    bin_a = hex_to_bin_256(hash_a)
    bin_b = hex_to_bin_256(hash_b)

    hamming_dist = compute_hamming_distance(bin_a, bin_b)
    total_bits = 256
    bit_flip_ratio = (hamming_dist / total_bits) * 100.0

    # Character-level hex diff
    hex_diff_count = sum(c1 != c2 for c1, c2 in zip(hash_a, hash_b))

    return {
        "hash_a": hash_a,
        "hash_b": hash_b,
        "binary_a": bin_a,
        "binary_b": bin_b,
        "total_bits": total_bits,
        "hamming_distance": hamming_dist,
        "bit_flip_ratio_percent": round(bit_flip_ratio, 2),
        "hex_differing_chars": hex_diff_count,
        "hex_differing_ratio_percent": round((hex_diff_count / 64) * 100.0, 2),
        "is_avalanche_significant": hamming_dist >= 90,  # Typically ~128 bits flip
    }


def format_avalanche_report(metrics: Dict[str, Any]) -> str:
    """Format avalanche metrics into clean text report for CLI / Academic Evaluator."""
    lines = [
        "=" * 70,
        "           AVALANCHE EFFECT & CRYPTOGRAPHIC FINGERPRINT REPORT",
        "=" * 70,
        f"Hash A (Original):  {metrics['hash_a']}",
        f"Hash B (Modified):  {metrics['hash_b']}",
        "-" * 70,
        f"Hex Character Differences: {metrics['hex_differing_chars']} / 64 characters ({metrics['hex_differing_ratio_percent']}%)",
        f"Bitwise Hamming Distance:  {metrics['hamming_distance']} / 256 bits",
        f"Bit Flip Ratio:            {metrics['bit_flip_ratio_percent']}% (Theoretical Ideal: ~50.0%)",
        f"Avalanche Status:          {'PASS (Significant Cryptographic Avalanche)' if metrics['is_avalanche_significant'] else 'WEAK'}",
        "=" * 70,
    ]
    return "\n".join(lines)
