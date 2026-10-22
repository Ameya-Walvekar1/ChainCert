"""
Benchmarking Script for ChainCert Module 2: Hashing Engine.
Measures canonicalization and SHA-256 hash execution times across varying batch sizes.
"""

import time
from typing import Dict, Any, List
from chaincert.utils.data_generator import generate_synthetic_certificates
from chaincert.hashing.hasher import hash_certificate


def run_hashing_benchmark(sizes: List[int] = [10, 50, 100, 250, 500, 1000]) -> List[Dict[str, Any]]:
    """
    Run timing benchmark for canonicalization + SHA-256 hashing across batch sizes.

    Args:
        sizes (List[int]): List of dataset sizes to benchmark.

    Returns:
        List[Dict[str, Any]]: List of benchmark performance metrics per batch size.
    """
    results = []

    for size in sizes:
        dataset = generate_synthetic_certificates(count=size, seed=42)

        start_time = time.perf_counter()
        for cert in dataset:
            hash_certificate(cert)
        end_time = time.perf_counter()

        total_time_ms = (end_time - start_time) * 1000.0
        avg_time_per_cert_us = (total_time_ms / size) * 1000.0
        certs_per_second = size / (end_time - start_time) if (end_time - start_time) > 0 else 0

        res = {
            "batch_size": size,
            "total_time_ms": round(total_time_ms, 3),
            "avg_time_per_cert_us": round(avg_time_per_cert_us, 2),
            "throughput_certs_per_sec": round(certs_per_second, 1),
        }
        results.append(res)

    return results


def print_benchmark_report(results: List[Dict[str, Any]]) -> None:
    """Print formatted benchmark table."""
    print("\n" + "=" * 65)
    print("      CHAINCERT MODULE 2 — HASHING ENGINE BENCHMARK REPORT")
    print("=" * 65)
    print(f"{'Batch Size':<12} | {'Total Time (ms)':<16} | {'Avg/Cert (µs)':<14} | {'Throughput (cert/s)':<18}")
    print("-" * 65)

    for r in results:
        print(f"{r['batch_size']:<12} | {r['total_time_ms']:<16.3f} | {r['avg_time_per_cert_us']:<14.2f} | {r['throughput_certs_per_sec']:<18.1f}")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    benchmark_results = run_hashing_benchmark()
    print_benchmark_report(benchmark_results)
