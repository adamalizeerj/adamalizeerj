# Adam

Cybersecurity undergraduate focused on **detection engineering, cloud security, and security automation**. I design, build, and document defensive systems end to end, telemetry pipelines, behavioral detections, and automated incident response, as reproducible IaC, then validate them with adversary emulation.

CompTIA Security+ certified. CySA+ in progress. Graduating 2028.

<a href="https://linkedin.com/in/aalizeerj"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" /></a>

---

## Focus Areas

- **Detection Engineering** — behavioral and signature-based detections, alert tuning, false-positive reduction, MITRE ATT&CK mapping
- **Cloud Security** — AWS and Azure telemetry, IAM analysis, audit logging, threat detection
- **Security Automation / SOAR** — orchestrated, auditable incident response with human-in-the-loop controls
- **Incident Response** — triage, containment, forensic evidence capture, runbook development
- **Infrastructure-as-Code** — reproducible security infrastructure built and torn down with Terraform

---

## Certifications

- CompTIA Security+
- CompTIA CySA+ *(in progress)*

---

## Selected Projects

### AWS Behavioral Anomaly Detection with SOAR Auto-Response
A behavioral detection-and-response pipeline built entirely on native AWS services and managed with Terraform. It learns each IAM principal's normal behavior, flags activity that deviates from that baseline, and runs an automated, human-gated incident response playbook, containment, forensic evidence capture, notification, and incident ticketing.

- Per-principal behavioral baselining with ASN enrichment and a warm-up guard, backed by DynamoDB
- Six-step Step Functions playbook with a native callback-token human-approval gate
- Detections and responses mapped to MITRE ATT&CK for Cloud and D3FEND
- SOC-style runbooks and a full architecture diagram included

**[View repository →](https://github.com/adamalizeerj/aws-anomaly-soar)**

### DNS Tunneling Detection & Vulnerability Management
A full vulnerability-management-lifecycle lab, from discovery through verified remediation, simulating a covert C2 channel tunneled through DNS, a technique that evades perimeter controls because firewalls rarely inspect DNS contents.

- Five-VM isolated lab on Apple Silicon (pfSense, Windows victim, BIND9 resolver, Kali attacker, Wazuh SIEM)
- Discovered via internal red-team simulation, scored with CVSS 4.0, mapped to ATT&CK T1071.004 and T1572
- Four-control defense-in-depth remediation aligned to NIST SP 800-40r4 and the CISA Vulnerability Management Lifecycle
- Custom Suricata rules, BIND9 Response Policy Zones, manual ARM64 Wazuh stack, and Slack alerting, with end-to-end remediation verification

**[View repository →](https://github.com/adamalizeerj/dns-tunnel-vuln-mgmt)**

---

## Skills & Tooling

**Cloud & SOC**

![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white)
![Microsoft Azure](https://img.shields.io/badge/Microsoft%20Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Microsoft Sentinel](https://img.shields.io/badge/Microsoft%20Sentinel-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)

**SIEM & Detection**

![Wazuh](https://img.shields.io/badge/Wazuh-005571?style=for-the-badge&logo=wazuh&logoColor=white)
![Elastic](https://img.shields.io/badge/Elastic%20(ELK)-005571?style=for-the-badge&logo=elastic&logoColor=white)
![Sysmon](https://img.shields.io/badge/Sysmon-003366?style=for-the-badge&logo=windows&logoColor=white)
![Suricata](https://img.shields.io/badge/Suricata-EE3124?style=for-the-badge&logoColor=white)

**Automation & Infrastructure-as-Code**

![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

**Network Security**

![pfSense](https://img.shields.io/badge/pfSense-212121?style=for-the-badge&logo=pfsense&logoColor=white)
![Wireshark](https://img.shields.io/badge/Wireshark-1679A7?style=for-the-badge&logo=wireshark&logoColor=white)

**Adversary Emulation & Detection Validation**

![Kali Linux](https://img.shields.io/badge/Kali%20Linux-268BEE?style=for-the-badge&logo=kalilinux&logoColor=white)
![Nmap](https://img.shields.io/badge/Nmap-00457C?style=for-the-badge&logo=nmap&logoColor=white)

**Frameworks & Standards**

![MITRE ATT&CK](https://img.shields.io/badge/MITRE%20ATT%26CK-000000?style=for-the-badge&logo=mitre&logoColor=white)
![NIST](https://img.shields.io/badge/NIST-005EA2?style=for-the-badge&logoColor=white)

---

## GitHub Activity

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=adamalizeerj&show_icons=true&hide_border=true&theme=github_dark)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=adamalizeerj&layout=compact&hide_border=true&theme=github_dark)
