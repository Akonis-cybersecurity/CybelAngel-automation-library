# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-29

### Added
- Initial release of the unified CybelAngel intake format.
- Parser for Report events (GET /v2/reports): IP/hostname extraction, severity mapping (0-4), ECS intrusion_detection categorisation.
- Parser for Credential events (GET /v1/credentials): user.email, user.name, ECS authentication categorisation.
- Parser for Claimed Attack events (GET /v1/threat-intelligence/claimed-attacks): per-category action (ransomware-detected, ddos-detected, defacement-detected, data-leak-detected).
- ECS mapping: event.provider=cybelangel, event.kind=alert for all threat types, event.kind=enrichment for data_leak claimed attacks.
- threat.indicator fields: ipv4-addr for reports with IP, email-addr for credential events, domain-name for claimed attacks.
- Custom fields under cybelangel.report.*, cybelangel.credential.*, cybelangel.claimed_attack.*.
- related.ip, related.hosts, related.user aggregation for all event types.

[1.0.0]: https://github.com/Akonis-cybersecurity/CybelAngel-automation-library/releases/tag/v1.0.0
