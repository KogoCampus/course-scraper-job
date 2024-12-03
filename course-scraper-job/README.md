# Course Scraper Job

A Celery web scraper to automate collection of course information from various schools.

## Build and run
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
