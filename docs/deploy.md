# Deployment (AWS)

Real deployment of the RAG chatbot to AWS EC2, with a separate Jenkins CI server.

- **Region**: `us-west-2`
- **Topology**: two EC2 instances — one App server, one Jenkins server.
- **Images**: AWS ECR.

> **Secrets and concrete resource identifiers are NOT committed.** The AWS account ID,
> VPC/security-group/instance IDs, and public endpoints live in `docs/infra-inventory.local.md`,
> which is gitignored. The SSH private key lives at `~/.ssh/ragdocs-key.pem` on the operator
> machine; `ANTHROPIC_API_KEY` is injected on the App server at runtime. None of these ever
> enter the repo.

## Architecture

```
GitHub push ──webhook──▶ Jenkins EC2 ──build image──▶ ECR
                              │
                              └──SSH──▶ App EC2: docker compose pull && up -d
                                          ├─ backend (FastAPI)
                                          ├─ frontend (nginx, Phase 3)
                                          ├─ qdrant
                                          └─ mongo
```

## Security groups (rules, not IDs)

- **app**: 22 (operator IP only), 80 + 443 (public), 8000 (operator IP, backend testing).
- **jenkins**: 22 + 8080 (operator IP only).

SSH / Jenkins ingress is pinned to the operator's public IP. When that IP changes, update the
rule (the concrete SG IDs are in the local inventory file):

```bash
aws ec2 authorize-security-group-ingress --group-id <app-sg> --protocol tcp --port 22 --cidr <newip>/32
```

## Progress

- [x] **5a — Foundation (free)**: billing alarm, ECR repos, key pair, security groups.
- [ ] **5b — App EC2** *(billable)*: launch instance, install Docker, pull image from ECR, `docker compose up`.
- [ ] **5c — Jenkins EC2** *(billable)*: launch instance, install Jenkins, configure GitHub webhook + pipeline (build → push ECR → SSH deploy to App server).

## Cost control

- Two medium instances running ≈ $60/mo. **Stop them when not demoing** — you only pay for
  running time + EBS storage.
- A `$30` CloudWatch billing alarm emails the operator (confirmed).
