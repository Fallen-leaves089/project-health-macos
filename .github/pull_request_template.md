## Summary

Describe the change and the user-facing effect.

## Verification

- [ ] `python scripts/verify_package.py`
- [ ] `python -B -m unittest discover -s tests -p 'test_*.py'`
- [ ] `python scripts/check_redaction.py --self-test`
- [ ] macOS CI: `macOS Apple Silicon / Python 3.9` and `macOS Apple Silicon / Python 3.12`

## Release hygiene

- [ ] Version and `CHANGELOG.md` updated for user-visible changes
- [ ] `PROVENANCE.md` / `NOTICE` updated when license or attribution changes
- [ ] No private keys, secrets, customer data, or real `/Users/<name>` paths
