#!/usr/bin/env bash
#
# apply_repo_metadata.sh - the two-minute-per-repo pass that the audit flagged.
#
# WHY
#   The API audit scored repository metadata 10/30. Not because the projects are
#   thin, but because the fields that feed GitHub search, Google indexing, and the
#   About box are empty: 0 topics across all five repos, 1 of 5 licensed, 0 of 5
#   with a link in the About box. Topics in particular are a real discovery
#   channel and cost nothing.
#
# REQUIREMENTS
#   gh CLI, authenticated:  gh auth login
#
# USAGE
#   bash apply_repo_metadata.sh            # show what would change
#   bash apply_repo_metadata.sh --apply    # actually change it
#
# Run this BEFORE triggering the profile-card workflow, so the hygiene bars on
# the card reflect the fixed state rather than the current one.

set -euo pipefail

USER="adamalizeerj"
APPLY=false
[[ "${1:-}" == "--apply" ]] && APPLY=true

run() {
  if $APPLY; then
    echo "+ $*"
    "$@"
  else
    echo "would run: $*"
  fi
}

# ---------------------------------------------------------------------------
# aws-anomaly-soar
# ---------------------------------------------------------------------------
run gh repo edit "$USER/aws-anomaly-soar" \
  --description "Behavioural anomaly detection on AWS CloudTrail with a human-gated SOAR containment playbook. Per-principal IAM baselines in DynamoDB, six-step Step Functions response, mapped to ATT&CK for Cloud and D3FEND. All Terraform." \
  --add-topic aws \
  --add-topic cloud-security \
  --add-topic detection-engineering \
  --add-topic soar \
  --add-topic incident-response \
  --add-topic security-automation \
  --add-topic terraform \
  --add-topic cloudtrail \
  --add-topic guardduty \
  --add-topic step-functions \
  --add-topic dynamodb \
  --add-topic aws-lambda \
  --add-topic iam \
  --add-topic anomaly-detection \
  --add-topic mitre-attack \
  --add-topic d3fend \
  --add-topic python \
  --add-topic infrastructure-as-code

# The About box link is the single most-clicked element for a reviewer deciding
# whether to spend time. The demo video is the strongest thing to point at, but
# swap in a GitHub Pages write-up if you would rather not depend on Dropbox.
run gh repo edit "$USER/aws-anomaly-soar" \
  --homepage "https://github.com/adamalizeerj/aws-anomaly-soar/blob/main/docs/mitre-attack-coverage.md"

# ---------------------------------------------------------------------------
# llm-sectest
# ---------------------------------------------------------------------------
run gh repo edit "$USER/llm-sectest" \
  --description "Automated OWASP Top 10 for LLM Applications (2025) security testing. Every attack ships a programmatic oracle that asserts the exploit actually landed. 5 of 6 categories exploitable before hardening, 0 of 6 after. Runs fully local on Ollama." \
  --add-topic llm-security \
  --add-topic ai-security \
  --add-topic owasp \
  --add-topic owasp-llm-top10 \
  --add-topic prompt-injection \
  --add-topic security-testing \
  --add-topic red-teaming \
  --add-topic guardrails \
  --add-topic python \
  --add-topic pytest \
  --add-topic fastapi \
  --add-topic ollama \
  --add-topic security-tools \
  --add-topic cli

run gh repo edit "$USER/llm-sectest" \
  --homepage "https://github.com/adamalizeerj/llm-sectest/blob/main/docs/METHODOLOGY.md"

# ---------------------------------------------------------------------------
# dns-tunnel-vuln-mgmt
# ---------------------------------------------------------------------------
run gh repo edit "$USER/dns-tunnel-vuln-mgmt" \
  --description "Full vulnerability management lifecycle for a covert DNS tunnelling C2 channel, from red-team discovery through four-control remediation and verified retest. CVSS 4.0 7.6, custom Suricata rules, BIND9 RPZ, Wazuh, five-VM isolated lab." \
  --add-topic dns-tunneling \
  --add-topic detection-engineering \
  --add-topic vulnerability-management \
  --add-topic threat-detection \
  --add-topic network-security \
  --add-topic suricata \
  --add-topic bind9 \
  --add-topic pfsense \
  --add-topic wazuh \
  --add-topic siem \
  --add-topic mitre-attack \
  --add-topic cvss \
  --add-topic nist-800-53 \
  --add-topic homelab \
  --add-topic blue-team

run gh repo edit "$USER/dns-tunnel-vuln-mgmt" \
  --homepage "https://github.com/adamalizeerj/dns-tunnel-vuln-mgmt/blob/main/04-verification/retest-results.md"

# ---------------------------------------------------------------------------
# Profile repo
# ---------------------------------------------------------------------------
run gh repo edit "$USER/$USER" \
  --description "Profile README. Detection and automated response for cloud, network, and LLM systems." \
  --add-topic profile \
  --add-topic config \
  --add-topic readme

# ---------------------------------------------------------------------------
# Account fields the audit flagged as empty
# ---------------------------------------------------------------------------
run gh api -X PATCH /user \
  -f bio="Security engineer. Detection and automated response for cloud, network, and LLM systems. I attack what I build, then measure what held." \
  -f blog="https://github.com/adamalizeerj/aws-anomaly-soar" \
  -f location="Fayetteville, NC"

cat <<'NOTE'

STILL MANUAL, in order of value
-------------------------------
1. LICENSE on aws-anomaly-soar and dns-tunnel-vuln-mgmt.
   Web UI: Add file -> Create new file -> type "LICENSE" -> "Choose a license template".
   A repo with no license is technically not open source.

2. Social preview images, 1280x640, on all three project repos.
   Settings -> General -> Social preview -> Upload.
   Generated for you at assets/social/. These are what render in your LinkedIn
   Featured section, so they matter more than they look like they do.

3. Delete or archive cg-adamalizeerj.
   Its README is byte-identical to the profile README, so it reads as a
   duplicate in the repo list and drags the hygiene ratios down.
   gh repo delete adamalizeerj/cg-adamalizeerj

4. llm-sectest README references SCOPE.md, which returns 404.
   Either add the file or drop the reference.

5. Settings -> Profile -> "Include private contributions on my profile".
   Shows activity volume without revealing repositories.

6. Pin exactly three repos, in this order:
   aws-anomaly-soar, llm-sectest, dns-tunnel-vuln-mgmt.
   Three strong beats six padded, and nothing forces the slots to be full.

NOTE
