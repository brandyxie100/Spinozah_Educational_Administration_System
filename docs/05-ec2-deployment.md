# Deploying to a single AWS EC2 instance (Docker Compose, HTTP, no domain)

Stack: Caddy (port 80) → Next.js (`web`) and FastAPI (`api`), plus Postgres 15.
Only port 80 is exposed. Postgres and the API are reachable only inside Docker.

## 1. AWS console
- Security group inbound: **22** from your IP only, **80** from anywhere. Do not open 5432 or 8000.
- Attach an **Elastic IP**. The IP is baked into the web build, so it must not change.
- If the instance has under 2 GB RAM, add swap before building (step 2).

## 2. Install Docker (Amazon Linux 2023)
```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user          # log out and back in afterwards
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version

# optional 2 GB swap for the Next.js build
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
```

## 3. Configure and start
```bash
git clone https://github.com/brandyxie100/Spinozah_Educational_Administration_System.git
cd Spinozah_Educational_Administration_System
cp .env.prod.example .env.prod
nano .env.prod        # set <EC2_IP>, POSTGRES_PASSWORD, JWT_SECRET (openssl rand -hex 32), OPENAI_API_KEY
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml ps
```

## 4. Create the first admin
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T \
  -e TENANT_NAME="My School" -e TENANT_SLUG=myschool \
  -e ADMIN_EMAIL=you@example.com -e ADMIN_NAME="Admin" -e ADMIN_PASSWORD='choose-a-strong-one' \
  api python - < deploy/seed_admin.py
```

## 5. Verify
- `curl http://<EC2_IP>/health`
- Open `http://<EC2_IP>/` and use **Staff sign in** with the tenant slug, email and password above.

## Updating
```bash
git pull
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```
Migrations run automatically through the `migrate` service.

## Later: HTTPS
Point a domain at the Elastic IP, change `:80` in `deploy/Caddyfile` to the domain name, expose port 443 in the
compose file and security group, set the `http://<EC2_IP>` values in `.env.prod` to `https://<domain>`, and set
`ENVIRONMENT=production`. Rebuild `web`, because `NEXT_PUBLIC_API_URL` is build-time.
Until HTTPS is on, keep `ENVIRONMENT=staging`, because the refresh cookie is `Secure` when it is `production` and browsers drop it over plain HTTP.

## Backups
Not configured. Consider a nightly `docker compose exec db pg_dump -U postgres spinozah` to S3.
