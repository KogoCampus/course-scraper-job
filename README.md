# Course Scraper


## Setup
1. Install UV package manager (skip if already installed)
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies
```
uv sync
```

3. Copy the .env.example file to .env and populate with your values.
```
cp .env.example .env
```

4. Enable virtual environment
```
source venv/bin/activate
```

## Run the scraper
Check the `run_task.py` file and task scripts in `app/tasks` to see the available tasks.  
`run_task.py` is a CLI tool to run tasks directly. This will dynamically import the task module with the provided task name arguments.  

Example:
```
python run_task.py scraper_task sample
```
