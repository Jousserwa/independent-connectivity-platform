# Phone-Only Development Guide

## Goal

Use the Android phone as the project management and source-editing device while keeping development at $0. This guide assumes no computer is currently available.

## Recommended workflow

1. Use the GitHub mobile app or mobile browser to inspect issues, commits, files, and Actions results.
2. Use GitHub's web editor for small changes and pull requests. Avoid editing large files on a small screen when possible.
3. If comfortable with a terminal, Termux from its official F-Droid or GitHub distribution can provide a local Python environment. Install only from the official project source; avoid repackaged APK sites.
4. Run the dependency-free control-plane unit tests locally in Termux:
   ```sh
   pkg update
   pkg install python
   git clone https://github.com/Jousserwa/independent-connectivity-platform.git
   cd independent-connectivity-platform/control-plane
   python -m unittest -v
   ```
5. Alternatively, inspect the public GitHub Actions results when the repository validation workflow is added.

## Important Android limitation

A normal Android app cannot simply turn the phone into a reliable always-on Linux gateway. Android's VPN service is intended for client-side VPN use and only one active VPN service can normally be in control. Running a WireGuard server, forwarding traffic, and managing firewall rules on the same unrooted phone is not the first prototype target.

The phone can develop and test control-plane rules. A separate authorized Linux host will still be needed for the full gateway proof. We will not rent one under the current $0 budget.

## Security

- Never paste private keys, passwords, API tokens, or recovery codes into GitHub files or public issues.
- Do not grant untrusted apps broad device access.
- Do not install unofficial "free internet" or modified VPN APKs as development dependencies.
- Keep local test credentials disposable.
