import asyncio
import random
from typing import List
from datetime import datetime
from app.tasks.scraper_task import run_scraper

async def process_job(job_id: int, school: str) -> str:
    """Run scraper task with job_id as pageNum"""
    start_time = datetime.now()
    try:
        # Run the scraper task with school and pageNum parameters
        result = await run_scraper.apply(args=[school, job_id])
        process_time = (datetime.now() - start_time).total_seconds()
        return f"Job {job_id} (Page {job_id}) completed in {process_time:.2f}s"
    except Exception as e:
        return f"Job {job_id} (Page {job_id}) failed: {str(e)}"

async def task_scheduler(total_jobs: int, window_size: int, school: str):
    """Schedule scraper tasks with a fixed window size"""
    # Initialize job pool and active tasks
    job_pool = list(range(0, total_jobs))
    active_tasks: List[asyncio.Task] = []
    completed_jobs = []

    print(f"\nStarting scheduler with {total_jobs} jobs and window size {window_size}")
    print(f"School: {school}")
    print("=" * 50)

    while job_pool or active_tasks:
        # Fill the window with new tasks if there's space and jobs available
        while len(active_tasks) < window_size and job_pool:
            job_id = job_pool.pop(0)
            task = asyncio.create_task(process_job(job_id, school))
            active_tasks.append(task)
            print(f"{datetime.now().strftime('%H:%M:%S')} | Started Job {job_id} (Page {job_id})")
            print(f"Active tasks: {len(active_tasks)}, Remaining in pool: {len(job_pool)}")

        if not active_tasks:
            break

        # Wait for at least one task to complete
        done, pending = await asyncio.wait(active_tasks, return_when=asyncio.FIRST_COMPLETED)

        # Process completed tasks
        for task in done:
            result = await task
            completed_jobs.append(result)
            active_tasks = list(pending)  # Update active tasks
            print(f"\n{datetime.now().strftime('%H:%M:%S')} | {result}")
            print(f"Active tasks: {len(active_tasks)}, Remaining in pool: {len(job_pool)}")
            print("-" * 50)

    print("\nAll jobs completed!")
    print("=" * 50)
    print(f"Total jobs processed: {len(completed_jobs)}")
    return completed_jobs

async def main():
    TOTAL_JOBS = 25
    WINDOW_SIZE = 5
    SCHOOL = "university_of_british_columbia"  # or any other school code
    
    await task_scheduler(TOTAL_JOBS, WINDOW_SIZE, SCHOOL)

if __name__ == "__main__":
    asyncio.run(main())
