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
GitHub push ──poll──▶ Jenkins EC2 ──build backend+frontend──▶ ECR
                          │
                          └──scp compose + SSH──▶ App EC2: docker compose pull && up -d
                                      ├─ frontend (nginx :80, serves SPA + proxies API)
                                      ├─ backend (FastAPI, internal :8000)
                                      ├─ qdrant
                                      └─ mongo
```

The frontend nginx reverse-proxies `/documents`, `/chat`, `/health`, `/docs` to the backend, so
the browser only ever talks to one origin (port 80) — no CORS in production. The whole site is at
`http://<app-ec2-ip>/`.

## Security groups (rules, not IDs)

- **app**: 22 (operator IP + jenkins SG), 80 (operator IP only — the site is private, demo-only),
  8000 (operator IP, legacy/backend now internal).
- **jenkins**: 22 + 8080 (operator IP only).

> The whole site is locked to the operator's IP — there is no public access, so the unauthenticated
> API (which spends OpenAI credits and exposes a destructive `DELETE`) can't be abused. When the
> operator IP changes, re-point port 80:
> `aws ec2 authorize-security-group-ingress --group-id <app-sg> --protocol tcp --port 80 --cidr <newip>/32`
> (and revoke the old one). Defense-in-depth still recommended: set a hard monthly spend cap in the
> OpenAI dashboard as a backstop.

SSH / Jenkins ingress is pinned to the operator's public IP. When that IP changes, update the
rule (the concrete SG IDs are in the local inventory file):

```bash
aws ec2 authorize-security-group-ingress --group-id <app-sg> --protocol tcp --port 22 --cidr <newip>/32
```

## Progress

- [x] **5a — Foundation (free)**: billing alarm, ECR repos, key pair, security groups.
- [x] **5b — App EC2** *(billable)*: t4g.medium (Graviton/arm64) running Docker; `compose.prod.yml`
  pulls the backend image from ECR and runs backend + mongo + qdrant. Backend is published on
  port 80; the API is publicly reachable (`/health`, `/docs`). The `ANTHROPIC_API_KEY` and the
  `BACKEND_IMAGE` ECR URI are set in the server-side `.env` only.
- [x] **5c — Jenkins EC2** *(billable)*: t4g.medium running Jenkins (Java 21). Pipeline
  (`Jenkinsfile`) builds the backend image, pushes to ECR, and SSH-deploys to the App server.
  End-to-end verified: a build recreates only the App's backend container.

### CI/CD notes

- Jenkins env vars (Manage Jenkins → System → Global properties): `ECR_REGISTRY`, `APP_HOST`.
- SSH credential id `app-ssh` (ec2-user + key) drives the deploy step.
- **`APP_HOST` must be the App server's *private* IP**, not public. Security-group source-group
  references only match traffic inside the VPC; dialing the public IP makes the source appear as
  Jenkins's public IP and the rule won't match (SSH times out). Private IP also survives stop/start.
- Trigger: Poll SCM (or manual Build Now). A GitHub webhook would require exposing Jenkins :8080
  publicly, which we avoid.

### App server operations

```bash
ssh -i ~/.ssh/ragdocs-key.pem ec2-user@<app-ip>
cd ~/ragdocs
sudo docker compose -f compose.prod.yml ps          # status
sudo docker compose -f compose.prod.yml logs backend # logs
sudo docker compose -f compose.prod.yml pull && \
  sudo docker compose -f compose.prod.yml up -d      # redeploy latest image
```

> **Cost**: stop the instance when not demoing — `aws ec2 stop-instances --instance-ids <id>`
> (you keep the EBS volume + data, pay only storage). `start-instances` to bring it back; the
> public IP changes on stop/start unless an Elastic IP is attached.

## Cost control

- Two medium instances running ≈ $60/mo. **Stop them when not demoing** — you only pay for
  running time + EBS storage.
- A `$30` CloudWatch billing alarm emails the operator (confirmed).
