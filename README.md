# Course Scraper


## Setup
1. Copy .env.example to .env and populate with your values.
```
cp .env.example .env
```

2. Run docker compose to build and run the container:
```
docker compose up
# or
sudo docker compose up --build
```


## Monitoring & Task Management Console

- Flower Dashboard: http://localhost:5555
- Celery Beat: http://localhost:8000/


## Triggering Tasks Manually via CLI (Local Testing)

```bash
curl -X POST http://localhost:5555/api/task/async-apply/scraper_task -d '{"args": ["task_name"]}'
```
for example:
```bash
curl -X POST http://localhost:5555/api/task/async-apply/scraper_task -d '{"args": ["sample"]}'
```


## Edit the environment variables for the production environments

1. Install SOPS:
```
brew install sops
```

2. Decrypt the environment file:
```
sops --config .sops/sops.yaml -d -i prod.env
```

3. Fill in the missing values in the `values.env` file.

4. Encrypt the environment file:
```
sops --config .sops/sops.yaml -e -i prod.env
```
