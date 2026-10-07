# Third-Party Notices

The original Knossos lab code (docker-compose configuration, the scoreboard
application, Dockerfiles, scripts, and lab content authored by Pentest.TV) is
released under the MIT License; see [LICENSE](LICENSE).

Knossos orchestrates third-party tools and intentionally vulnerable targets.
These are pulled or built from their upstream projects at deploy or build time
and remain under their own licenses. Each project's license governs that
component; consult the upstream repository for authoritative terms. Trademarks
and project names are the property of their respective owners, and inclusion
here does not imply endorsement.

## Intentionally vulnerable targets and offensive tooling

- OWASP Juice Shop - MIT License - https://github.com/juice-shop/juice-shop
- Damn Vulnerable Web Application (DVWA) - GPL-3.0 - https://github.com/digininja/DVWA
- Gophish - MIT License - https://github.com/gophish/gophish
- Sliver (Bishop Fox) - GPL-3.0 - https://github.com/BishopFox/sliver

## Base images and supporting services

Pulled as upstream container images and governed by their respective licenses:

- Metasploitable 2 (Rapid7) - see upstream - https://github.com/rapid7/metasploitable2
- MailHog - MIT License - https://github.com/mailhog/MailHog
- ISC BIND 9 - MPL-2.0 - https://www.isc.org/bind/
- Kali Linux, Debian, and Python base images - under their respective distribution licenses
