# Release Signing and Download Verification

[中文](SIGNING.md) | **English**

Release artifacts use **OpenSSH Ed25519** signatures. macOS and most Linux systems can verify them without installing GPG.

## Release files

When downloading from GitHub Releases, get all of these:

- `project-health-macos-<version>.zip`: the skill package
- `SHA256SUMS`: the zip checksum
- `SHA256SUMS.sig`: the OpenSSH signature over `SHA256SUMS`
- `allowed_signers`: the permitted signing identity and public key
- `release-signing-key.pub`: the public key used to check the fingerprint; it matches the key in `allowed_signers`

Both the repository and the Release provide `release-signing-key.pub`.

`SHA256SUMS` and `SHA256SUMS.sig` are release assets created after the zip. They are not placed inside the zip, which avoids a recursive hash change caused by embedding the archive's own checksum.

## Signing identity

- Principal: `project-health-macos-release`
- Algorithm: Ed25519
- Public key fingerprint: `SHA256:DBDrYR50w0G+UuqtNAIgKZsXX4AjZAh3nvv0/zMCN8M`
- Public key file: `release-signing-key.pub`

Check the fingerprint before verifying:

```bash
ssh-keygen -lf release-signing-key.pub
```

## macOS verification

macOS normally bundles `shasum` but does not always provide `sha256sum`. From the download directory:

```bash
shasum -a 256 -c SHA256SUMS
ssh-keygen -Y verify -f allowed_signers \
  -I project-health-macos-release \
  -n file -s SHA256SUMS.sig < SHA256SUMS
```

## Linux verification

GNU coreutils distributions normally provide `sha256sum`. From the download directory:

```bash
sha256sum -c SHA256SUMS
ssh-keygen -Y verify -f allowed_signers \
  -I project-health-macos-release \
  -n file -s SHA256SUMS.sig < SHA256SUMS
```

On macOS or Linux, both commands must succeed. A successful signature check alone is not enough; also confirm that the filename in `SHA256SUMS` matches the file you downloaded.

## Check the zip hash only

If the public key is not available yet, at least compare the hash.

macOS:

```bash
shasum -a 256 project-health-macos-<version>.zip
```

Linux:

```bash
sha256sum project-health-macos-<version>.zip
```

A matching hash proves only that the download was not corrupted. It does not prove the publisher's identity; identity verification requires `SHA256SUMS.sig`.

## Maintainer signing procedure

Keep the private key on the maintainer's machine. **Never commit it, upload it to a Release, or print it in CI logs.** For each release:

1. Sign `SHA256SUMS` with the fixed release key.
2. Generate `SHA256SUMS.sig`.
3. Upload the zip, `SHA256SUMS`, and `SHA256SUMS.sig` to the same Release.
4. Recheck the public-key fingerprint and signature verification.

When rotating the key, publish a new `release-signing-key.pub` and `allowed_signers` and record the rotation date in `CHANGELOG.md`. Old signatures remain tied to the old key; do not silently overwrite the identity.
