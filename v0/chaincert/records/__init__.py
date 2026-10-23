"""
ChainCert Module 1: Certificate & Record Management exports.
"""

from chaincert.records.parser import parse_certificate_text, parse_certificate_file
from chaincert.records.certificate import ExtendedCertificateRecord
from chaincert.records.database import (
    init_db,
    add_certificate,
    get_certificate,
    list_certificates,
    update_certificate,
    assign_batch_and_proofs,
    update_batch_block_id,
    delete_certificate,
    clear_database,
    get_connection,
    issue_certificate,
)

__all__ = [
    "parse_certificate_text",
    "parse_certificate_file",
    "ExtendedCertificateRecord",
    "init_db",
    "add_certificate",
    "get_certificate",
    "list_certificates",
    "update_certificate",
    "assign_batch_and_proofs",
    "update_batch_block_id",
    "delete_certificate",
    "clear_database",
    "get_connection",
    "issue_certificate",
]
