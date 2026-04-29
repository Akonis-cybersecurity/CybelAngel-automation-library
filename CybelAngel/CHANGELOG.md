# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2026-04-29 - 1.0.0

### Added
- CybelAngelClient with OAuth2 client credentials flow and token caching
- 429 rate-limit backoff (3 retries: 60s, 120s, 240s)
- ReportsTrigger: sliding window on created_at, GET /v2/reports
- CredentialsTrigger: limit/skip pagination on last_detection_date, GET /v1/credentials
- ClaimedAttacksTrigger: limit/skip pagination on claimed_at, GET /v1/threat-intelligence/claimed-attacks
- GetReportById action
- UpdateReportStatus action
- UpdateMultipleStatuses action (bulk)
- GetReportComments action
- PostReportComment action
- GetReportAttachments action
- GetReportPdf action (base64-encoded)
- GetReportArchive action (base64-encoded ZIP)
- GetMirrorDetails action
- CreateRemediationRequest action
- UpdateCredentialStatus action (bulk)
- GetClaimedAttacks action (on-demand)
- GetInventoryAssets action
- UpdateInventoryAssetStatus action
