# MSD SDK Tutorial — Hands On

*Sign it. Embed it. Verify it.*

A hands-on walkthrough of the MSD SDK — using an **accounting audit trail** as the running example. Every code block is **self-contained**: run any block on its own.

> **Prerequisites:** `msd-sdk` and `zef` installed in the same virtual environment.

> **About keys in this tutorial:** Every example uses an inline test key. This is fine for learning. For real use, generate your keys in [MSD Explorer](https://network.msd-protocol.org/dashboard) — so verifiers can trace signatures back to your identity. An unendorsed key produces valid signatures, but not *trusted* ones.


---

## 1. Your First Signed Invoice

**Signed Data** is the fundamental unit of MSD: data + metadata + timestamp + cryptographic signature, bundled into a tamper-proof envelope.

```python
import msd_sdk as msd

# Test key pair — never use in production!
my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

invoice = {
    "invoice_id": "INV-2025-0042",
    "vendor": "Acme Supplies",
    "amount": 1250.00,
    "currency": "EUR",
    "line_items": [
        {"description": "Office chairs (x5)", "amount": 750.00},
        {"description": "Standing desks (x2)", "amount": 500.00},
    ]
}

audit = {
    "approved_by": "CFO Jane Chen",
    "department": "Operations",
    "approval_date": "2025-01-15",
}

signed = msd.sign(invoice, audit, my_key)
signed
```

The signed data contains `data` (the invoice), `metadata` (the audit trail), `signature_time`, `signature`, and `key` (public only — your private key never leaks).


---

## 2. Verify Before You Pay

Anyone with the public key can check: *has this invoice been tampered with since approval?*

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

signed = msd.sign(
    {"invoice_id": "INV-2025-0042", "amount": 1250.00, "vendor": "Acme Supplies"},
    {"approved_by": "CFO Jane Chen", "department": "Operations"},
    my_key
)

result = msd.verify(signed)
result['signature_is_valid']
```
````Result
True
````

`verify()` returns a rich dict with `signature_is_valid`, `data_hash`, `metadata_hash`, `signature_timestamp`, and more.


---

## 3. Content-Addressable Invoices

Need a unique fingerprint for deduplication or lookups — without signing? `content_hash` gives you a deterministic BLAKE3 Merkle hash.

```python
import msd_sdk as msd

inv_a = msd.content_hash({"invoice_id": "INV-2025-0042", "amount": 1250.00})
inv_b = msd.content_hash({"invoice_id": "INV-2025-0042", "amount": 1250.00})
inv_c = msd.content_hash({"invoice_id": "INV-2025-0043", "amount": 89.99})

("same invoice, same hash:", inv_a == inv_b, "different invoice, different hash:", inv_a != inv_c)
```
````Result
('same invoice, same hash:', True, 'different invoice, different hash:', True)
````


---

## 4. The Invisible Audit Trail — Unicode Steganography 🔏

Signed data wraps your data in a new structure. But what if you want to keep the original dict shape — say, for an API response or a JSON export — while still carrying a cryptographic audit trail?

`sign()` + `embed()` hides the full signature inside a single `🔏` emoji using **Unicode steganography**. Invisible variation selectors carry the complete metadata, timestamp, and Ed25519 signature. The dict stays clean and uncluttered.

```python
import msd_sdk as msd
import json

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

payment = {
    "invoice_id": "INV-2025-0042",
    "amount": 1250.00,
    "currency": "EUR",
    "vendor": "Acme Supplies",
    "paid_on": "2025-01-20",
}

audit_trail = {
    "approved_by": "CFO Jane Chen",
    "reviewed_by": "Controller Bob Park",
    "compliance_check": "passed",
}

signed = msd.sign(payment, audit_trail, my_key)
embedded = msd.embed(signed)

# The original data is untouched — plus a steganographic __msd key
# Survives JSON round-trips
json.loads(json.dumps(embedded)) == embedded
```
````Result
True
````


---

## 5. Reading the Audit Trail

Extract the metadata and signature hidden inside an embedded dict:

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

signed = msd.sign(
    {"invoice_id": "INV-2025-0042", "amount": 1250.00},
    {"approved_by": "CFO Jane Chen", "compliance_check": "passed"},
    my_key
)
embedded = msd.embed(signed)

meta = msd.extract_metadata(embedded)
sig = msd.extract_signature(embedded)

{
    "audit_trail": meta,
    "signed_at": sig["signature_time"],
    "signing_key": sig["key"]["__uid"],
}
```


---

## 6. Catching Fraud

Change anything in an embedded dict — a value, add a key, remove a key — and `verify()` catches it.

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

expense = {"vendor": "Acme Supplies", "amount": 1250.00, "category": "office"}
signed = msd.sign(expense, {"approved_by": "CFO Jane Chen"}, my_key)
embedded = msd.embed(signed)

# Untouched: valid
original = msd.verify(embedded)['signature_is_valid']

# Inflated amount
t1 = dict(embedded); t1["amount"] = 9999.00
inflated = msd.verify(t1)['signature_is_valid']

# Snuck in a bonus line
t2 = dict(embedded); t2["bonus"] = 500.00
added = msd.verify(t2)['signature_is_valid']

# Removed the category to hide it
t3 = {k: v for k, v in embedded.items() if k != "category"}
removed = msd.verify(t3)['signature_is_valid']

{"original": original, "inflated_amount": inflated, "added_key": added, "removed_key": removed}
```
````Result
{'original': True, 'inflated_amount': False, 'added_key': False, 'removed_key': False}
````


---

## 7. Signing the Receipts

MSD can embed signatures directly into binary files — the signed file stays viewable by standard programs.

Supported formats: **PNG, JPG, PDF, DOCX, XLSX, PPTX**.

```python
import msd_sdk as msd
import base64, struct, zlib

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

# Minimal 1x1 red PNG (stand-in for a scanned receipt)
def make_tiny_png():
    sig = b'\x89PNG\r\n\x1a\n'
    def chunk(ct, d):
        c = ct + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    return sig + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00')) + chunk(b'IEND', b'')

receipt_png = make_tiny_png()
png_data = {'__type': 'PngImage', 'data': base64.b64encode(receipt_png).decode()}

signed = msd.sign(
    png_data,
    {'expense_report': 'EXP-2025-007', 'scanned_by': 'Accounting Dept'},
    my_key
)
embedded = msd.embed(signed)

meta = msd.extract_metadata(embedded)
result = msd.verify(embedded)
clean = msd.strip_metadata_and_signature(embedded)

{
    "embedded_audit": meta,
    "signature_valid": result['signature_is_valid'],
    "original_recovered": base64.b64decode(clean['data']) == receipt_png,
}
```
````Result
{'embedded_audit': {'expense_report': 'EXP-2025-007', 'scanned_by': 'Accounting Dept'}, 'signature_valid': True, 'original_recovered': True}
````


---

## Quick Reference

| What you want to do | Function |
|---|---|
| Sign data | `msd.sign(data, metadata, key)` |
| Embed signature (dict steganography or file binary) | `msd.embed(signed_data)` |
| Verify any signed data | `result = msd.verify(x); result['signature_is_valid']` |
| Extract metadata | `msd.extract_metadata(signed_data)` |
| Extract signature info | `msd.extract_signature(signed_data)` |
| Content hash (no signing) | `msd.content_hash(data)` |
| Strip signature from file | `msd.strip_metadata_and_signature(signed_file)` |
| Load key from env var | `msd.key_from_env()` |
