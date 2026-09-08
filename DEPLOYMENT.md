# Deploying HireWise to Production

**Target architecture** (always-on, $0/month):

| Component | Host | Why |
|---|---|---|
| Frontend (Next.js) | **Vercel** (free) | Zero-config Next.js hosting, global CDN, automatic HTTPS |
| Backend (Flask + ML) | **Oracle Cloud Always Free** VM | Always-on (no cold starts), persistent disk for the SQLite database and uploaded resumes |

> The backend must be HTTPS because the Vercel frontend runs on HTTPS — browsers block API calls from an HTTPS page to a plain-HTTP backend ("mixed content"). Caddy in the Docker Compose stack handles that automatically with Let's Encrypt.

---

## Part 1 — Oracle Cloud VM (one-time, ~15 min)

### 1. Sign up

1. Go to <https://www.oracle.com/cloud/free/> and click **Start for free**.
2. Create the account. A **credit/debit card is required for identity verification** — it is **never charged** for Always Free resources (a small temporary authorization hold may appear and disappears).

> Known gotchas: some debit cards from certain countries fail verification; if the Ampere shape shows **"Out of capacity"** during instance creation, just retry later or pick another home region.

### 2. Create the instance

In the Oracle Cloud console: **Compute → Instances → Create instance**

| Setting | Value |
|---|---|
| Name | `hirewise` |
| Image | **Canonical Ubuntu 24.04** (click *Edit* next to Image and Shape if it shows Oracle Linux) |
| Shape | **Ampere** `VM.Standard.A1.Flex` — **2 OCPU, 4 GB RAM** (Always Free allows up to 4 OCPU / 24 GB total) |
| SSH keys | **Generate a key pair** → **Save Private Key** + **Save Public Key** — keep both files |
| Boot volume | Defaults (47 GB is free) |

After creation, copy the **Public IP**.

### 3. Open ports 80 and 443

**Networking → Virtual Cloud Networks → *your VCN* → Security Lists → Default Security List → Add Ingress Rules**, twice:

| Field | Value |
|---|---|
| Source CIDR | `0.0.0.0/0` |
| IP Protocol | TCP |
| Destination Port Range | `80` (then repeat with `443`) |

Port `22` (SSH) is already open by default.

### 4. Get a free HTTPS domain

1. Sign in at <https://duckdns.org> (GitHub or Google login).
2. Create a subdomain, e.g. `hirewise-yourname.duckdns.org`.
3. Point it at the VM's **public IP** and save.

> DuckDNS asks you to log in at least once every 30 days to keep the subdomain. If you own a real domain, use it instead — an `A` record to the VM IP works the same.

### 5. Hand over to deployment

You now have three things:

- the VM **public IP**
- the **SSH private key** file
- the **DuckDNS domain**

The rest is automated: the VM gets Docker, the repo, your `.env` (SMTP credentials — never committed to git), and `docker compose up -d --build`. See `backend/docker-compose.yml`, `backend/Dockerfile` and `backend/Caddyfile`.

---

## Part 2 — Backend (on the VM)

```bash
# 1. SSH in (username is "ubuntu" for Oracle's Ubuntu images)
ssh -i <path-to-private-key> ubuntu@<vm-public-ip>

# 2. Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu && exit   # re-login afterwards

# 3. Get the code
git clone https://github.com/haseebsaleem962/Hirewise.git
cd Hirewise/backend

# 4. Configure secrets (copy values from your local backend/.env)
cp .env.example .env
nano .env    # SECRET_KEY, SMTP_USER, SMTP_PASS, SMTP_SENDER

# 5. Set your domain in the Caddyfile
nano Caddyfile    # replace hirewise.duckdns.org

# 6. Open firewall (Oracle images ship restrictive iptables rules)
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo apt-get install -y iptables-persistent && sudo netfilter-persistent save

# 7. Build and start (first build trains the ML model, ~5 min)
docker compose up -d --build

# 8. Verify
curl https://<your-domain>/api/health
```

**Updating after code changes:**

```bash
git pull && docker compose up -d --build
```

The database (`docker-data/instance/`) and uploaded resumes (`docker-data/uploads/`) are mounted volumes — they survive rebuilds and redeploys.

---

## Part 3 — Frontend (Vercel)

```bash
cd frontend

# Set the production API URL (baked in at build time by Next.js)
# via dashboard: Settings → Environment Variables, or CLI:
vercel env add NEXT_PUBLIC_API_URL production
# value: https://<your-domain>/api

npm run build          # sanity-check the production build
vercel --prod
```

**Updating:** push to GitHub, then `vercel --prod` again (or connect the repo in the Vercel dashboard for automatic deploys on push).

---

## Operations cheat-sheet

| Task | Command (on the VM) |
|---|---|
| Backend logs | `docker compose logs -f backend` |
| Restart stack | `docker compose restart` |
| Update code | `git pull && docker compose up -d --build` |
| Disk usage of candidate data | `du -sh docker-data/` |
| Caddy status/certs | `docker compose logs caddy` |
