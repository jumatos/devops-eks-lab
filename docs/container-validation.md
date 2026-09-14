# Container validation

Validation date: 2026-09-14

## Image

- Local tag: devops-eks-lab-api:trixie
- Base: python:3.11-slim-trixie
- Base index digest: sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534

## Functional validation

- 35 application tests passed locally after dependency updates.
- Container dependency check passed.
- Application import passed.
- GET /health returned 200.
- GET /ready returned 503 because DynamoDB was not configured.
- GET /metrics returned 200 and recorded HTTP requests.
- Real DynamoDB connectivity was not tested.

## Runtime restrictions verified

- UID/GID: 10001:10001.
- Read-only root filesystem.
- Privileged mode disabled.
- All Linux capabilities dropped.
- Process effective and bounding capability sets were empty.
- NoNewPrivs was enabled.

These restrictions were verified on the local container.
Deployment configuration must explicitly preserve them.

## Vulnerability scan

Scanner: Trivy 0.74.0.
Selected severities: HIGH and CRITICAL.

- Python packages: 0 HIGH/CRITICAL findings.
- Debian packages: 44 HIGH, 0 CRITICAL.
- The 44 findings correspond to 8 distinct CVE identifiers.
- No fixed versions were listed for the remaining findings.

These results reflect the scanned image and vulnerability database
used on the validation date. They do not establish the absence of
other vulnerabilities.

The strict zero-HIGH/CRITICAL scan criterion is NOT met.

## Applicability investigation

- systemd-homed and systemd-homework were absent at the checked paths.
- Perl could not load Archive::Tar from its configured module paths.
- These observations support further applicability review.
- mount, nsenter and infocmp were present.
- Package removal simulation identified util-linux and ncurses-bin
  as essential packages. Their removal was not performed.
- No scanner exclusions have been configured.

The investigation is incomplete. Runtime restrictions provide
mitigations but do not fix the vulnerable packages.

## Lab decision

The project owner accepted proceeding with the remaining 44 HIGH
findings for this learning lab. Further vulnerability investigation
and remediation are deferred.

The strict zero-HIGH/CRITICAL scan criterion remains unmet.
This decision does not constitute production approval.

Vulnerability scanning will be retained for visibility, and the
verified runtime restrictions will be preserved.

## Outstanding work

- Preserve runtime restrictions in future deployment manifests.
- Repeat scanning when the image or vulnerability database changes.
- Reassess the remaining findings before any production use.
