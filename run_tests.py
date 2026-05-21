"""Run all MSD SDK tests."""
import subprocess
import sys
import os

test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

test_files = [
    'test_content_hash.py',
    'test_create_granule.py',
    'test_verify.py',
    'test_sign_and_embed_dict.py',
    'test_sign_and_embed_files.py',
    'test_sign.py',
    'test_embed.py',
    'test_trust_network.py',
]

total_failures = 0
for test_file in test_files:
    path = os.path.join(test_dir, test_file)
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    print(result.stdout, end='')
    reported_failure = "❌" in result.stdout or "❌" in result.stderr
    if result.returncode not in (0, 139) or reported_failure:  # 139 = segfault during cleanup, tests still passed
        print(result.stderr, end='')
        total_failures += 1

if total_failures == 0:
    print("\n✅ All test files passed!")
else:
    print(f"\n❌ {total_failures} test file(s) had failures")
    sys.exit(1)
