# Course Scraper Job

A Celery web scraper to automate collection of course information from various schools.

## Setup

1. Copy the example environment file to a new file named `.env`:

    ```bash
    cp .env.example .env
    ```

2. Populate the `.env` file with your credentials and configuration.

- Get your AWS credentials and add them to the `.env` file.
    ```bash
    cat ~/.aws/credentials
    ```

- Add your OpenAI API key to the `.env` file.


3. Build and run
```
docker-compose up
```

first time you run it, you may need to run the following command instead.
```
sudo docker-compose up --build
```


## Monitoring & Task Management

- Flower Dashboard: http://localhost:5555
- Celery Beat: http://localhost:8000/

### Triggering Tasks Manually

```bash
curl -X POST http://localhost:5555/api/task/async-apply/scraper_task -d '{"args": ["task_name"]}'
```
for example:
```bash
curl -X POST http://localhost:5555/api/task/async-apply/scraper_task -d '{"args": ["sample"]}'
```
