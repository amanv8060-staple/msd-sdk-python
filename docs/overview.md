# MSD SDK Overview

This document provides a comprehensive overview of the **msd-sdk-python** codebase—the Python SDK for Meta Structured Data.

---

## Vision

**Meta Structured Data (MSD)** is an open-source protocol for creating verifiable, composable, and trustworthy data in a world where authenticity matters more than ever.

In an age of AI-generated content, deepfakes, and information manipulation, MSD provides a cryptographically sound foundation for **signed, structured data** that can be:

- **Verified** by anyone, anywhere, without trusting intermediaries
- **Composed** into larger structures while preserving provenance
- **Distributed** across systems while maintaining integrity

Think of it as "git for data" meets "digital signatures for everything."

*For the full vision statement, see [_vision_and_naming.md](../notes/_vision_and_naming.md).*

---

## Core Concepts

### Signed Data

The fundamental unit in the Python SDK is **Signed Data** — a piece of data combined with its cryptographic signature. Every signed data envelope contains four essential elements:

| Component | Purpose |
|-----------|---------|
| **Data** | The actual content being signed (any structured data) |
| **Metadata** | Context about the data (author, timestamp, schema, etc.) |
| **Timestamp** | When the signature was created (cryptographic time anchor) |
| **Signature** | Ed25519 digital signature proving authenticity |

### Cryptographic Choices

- **Ed25519 Signatures**: Industry-standard, fast, secure (used by SSH, Signal, etc.)
- **MSD Content Hashing**: BLAKE3-based, modern, cryptographically secure
- **Content-Addressed**: Data is identified by its hash, not arbitrary IDs

*For detailed protocol specification, see [_GRANITE_PROTOCOL_SUMMARY.zef.md](../notes/_GRANITE_PROTOCOL_SUMMARY.zef.md).*

---

## Repository Structure

```
msd-sdk-python/
├── src/msd_sdk/
│   ├── __init__.py          # Public API exports and import checks
│   ├── core.py              # Sign, embed, verify, hash, extract, strip
│   ├── key_management.py    # Key generation, storage, env loading
│   └── trust_network.py     # Local trust-network store
├── docs/                    # User and maintainer documentation
├── tests/                   # SDK tests
├── pyproject.toml           # Package configuration
├── publish.py               # PyPI publishing script
├── README.md                # User-facing documentation
└── LICENSE / LICENSE-APACHE # Dual MIT/Apache-2.0 license
```

---

## SDK Implementation

### Current State

The SDK is at v0.2.4. The current implementation provides:

- Version declaration (`__version__ = "0.2.4"`)
- Zef package verification (checks for the rust-based `zef` dependency)
- Signing, embedding, verification, content hashing, key storage, and a local trust-network store

### API

```python
import msd_sdk as msd

# Key management
my_key = msd.key_from_env()  # reads MSD_SIGNING_KEY by default

# Sign data
signed = msd.sign(data, metadata, my_key)

# Embed signature into data
embedded = msd.embed(signed)

# Content hashing (without signature)
my_content_hash = msd.content_hash(data)

# Verify signatures
result = msd.verify(signed_data)
result['signature_is_valid']  # True/False
```

*For API naming exploration, see [_api_naming_alternatives.md](../notes/_api_naming_alternatives.md).*

---

## Key Management

Keys in MSD use Ed25519 elliptic curve cryptography with emoji-prefixed formats:

| Emoji | Purpose | Example |
|-------|---------|---------|
| 🔑 | Public key | `🔑-8614d100b3cdb5ff...` |
| 🗝️ | Private key | `🗝️-61250af6bf8b9332...` |
| 🍃 | Entity UID | `🍃-8d1dc8766070c87a...` |
| 🪨 | Content hash | `🪨-3f79bb7b435b0532...` |
| 🔏 | Signature | `🔏-2406ff6af58a5c72...` |

### Key Pair Structure

```python
{
  '__type': 'ET.Ed25519KeyPair',
  '__uid': '🍃-8d1dc8766070c87a4bb1',
  'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
  'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}
```

*For comprehensive key management patterns, see [_PRIVATE_KEY_MANAGEMENT.zef.md](../notes/_PRIVATE_KEY_MANAGEMENT.zef.md).*

---

## Signature Protocol

### Signature Core Fields

The signature is computed over three concatenated components:

1. **Data Merkle BLAKE3 Hash** (32 bytes raw binary)
2. **Metadata Merkle BLAKE3 Hash** (32 bytes raw binary)
3. **Unix Timestamp** (UTF-8 encoded string)

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│   DATA HASH (32B)   │  METADATA HASH (32B)│    TIMESTAMP        │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

### Signed Data Structure

```python
{
  '__type': 'ET.SignedData',
  'data': 'Hello, Meta Structured Data!',
  'metadata': {'creator': 'Alice', 'description': 'sample data'},
  'signature_time': {'__type': 'Time', 'zef_unix_time': '1769247795.03406592'},
  'signature': {
    '__type': 'ET.Ed25519Signature',
    'signature': '🔏-2406ff6af58a5c72878ee0f2df374cd63396c0adaca6905b2d1881ca45442658...'
  },
  'key': {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
  }
}
```

---

## Dependencies

The SDK depends on **zef**, a Rust-based library published on PyPI that provides:

- `merkle_hash` / `msd_hash` – Content hashing
- `blake3_hash_content` – BLAKE3 hashing
- `sign_with` / `verify_signature` – Ed25519 operations
- `to_json_like` / `from_json_like` – Type serialization
- Functional composition with `|` pipe operator

---

## Publishing

The SDK is published to PyPI at: **https://pypi.org/project/msd-sdk/**

### Installation

```bash
pip install msd-sdk
```

### Publishing Updates

```bash
# Bump patch version and publish
python publish.py --bump

# Bump minor/major version
python publish.py --bump minor
python publish.py --bump major
```

*For detailed publishing instructions, see [PUBLISHING.md](PUBLISHING.md).*

---

## MSD Ecosystem

MSD is available through multiple interfaces:

| Interface | Description |
|-----------|-------------|
| **MSD Explorer** | Web dashboard at https://network.msd-protocol.org/dashboard |
| **MSD CLI** | Command-line interface for developers |
| **MSD Desktop** | Graphical desktop application |
| **MSD SDKs** | Language-specific libraries (Python, JS, Rust) |



---

## Source Repository

**GitHub**: https://github.com/msd-protocol/msd-sdk-python

---

## License

Dual-licensed under MIT and Apache-2.0.
