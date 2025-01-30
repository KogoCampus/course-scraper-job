import asyncio
from typing import TypeVar, Callable, List, Any, Awaitable

# Configurable window size for concurrent requests
DEFAULT_WINDOW_SIZE = 3
DEFAULT_DELAY_BETWEEN_WINDOWS = 1  # seconds

T = TypeVar('T')  # Generic type for the result of each task
U = TypeVar('U')  # Generic type for the input to each task

async def sliding_window_request(
    items: List[U],
    task_fn: Callable[[U], Awaitable[T]],
    window_size: int = DEFAULT_WINDOW_SIZE,
    delay_between_windows: float = DEFAULT_DELAY_BETWEEN_WINDOWS,
) -> List[T]:
    """
    Process a list of items using a sliding window approach for concurrent async requests.
    
    Args:
        items: List of items to process
        task_fn: Async function to process each item
        window_size: Number of concurrent tasks to run at once
        delay_between_windows: Delay in seconds between processing each window
        
    Returns:
        List of results from processing all items
    
    Example:
        async def process_page(page_num: int) -> dict:
            # Some async processing
            return {"page": page_num, "data": ...}
            
        pages = list(range(10))  # [0,1,2,3,4,5,6,7,8,9]
        results = await sliding_window_request(
            items=pages,
            task_fn=process_page,
            window_size=3,  # Process 3 pages at a time
            delay_between_windows=1  # Wait 1 second between each window
        )
    """
    results = []
    
    # Process items in windows
    for i in range(0, len(items), window_size):
        window = items[i:i + window_size]
        
        # Create tasks for current window
        tasks = [task_fn(item) for item in window]
        
        # Wait for all tasks in current window to complete
        window_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and exceptions
        for result in window_results:
            if isinstance(result, Exception):
                # Log exception but continue processing
                print(f"Error processing task: {str(result)}")
                continue
            results.append(result)
        
        # Delay before processing next window if not the last window
        if i + window_size < len(items):
            await asyncio.sleep(delay_between_windows)
    
    return results

async def sliding_window_request_with_state(
    items: List[U],
    task_fn: Callable[[U, List[T]], Awaitable[T]],
    window_size: int = DEFAULT_WINDOW_SIZE,
    delay_between_windows: float = DEFAULT_DELAY_BETWEEN_WINDOWS,
) -> List[T]:
    """
    Process a list of items using a sliding window approach, passing accumulated state to each task.
    
    Similar to sliding_window_request but passes the list of accumulated results to each task.
    Useful when tasks need to know about the results of previous tasks.
    
    Args:
        items: List of items to process
        task_fn: Async function that takes (item, accumulated_results) and returns a result
        window_size: Number of concurrent tasks to run at once
        delay_between_windows: Delay in seconds between processing each window
        
    Returns:
        List of results from processing all items
        
    Example:
        async def process_page(page_num: int, previous_results: List[dict]) -> dict:
            # Can access previous_results if needed
            return {"page": page_num, "data": ...}
            
        results = await sliding_window_request_with_state(
            items=pages,
            task_fn=process_page
        )
    """
    results = []
    
    for i in range(0, len(items), window_size):
        window = items[i:i + window_size]
        
        # Create tasks for current window, passing current results
        tasks = [task_fn(item, results.copy()) for item in window]
        
        # Wait for all tasks in current window to complete
        window_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and exceptions
        for result in window_results:
            if isinstance(result, Exception):
                print(f"Error processing task: {str(result)}")
                continue
            results.append(result)
        
        if i + window_size < len(items):
            await asyncio.sleep(delay_between_windows)
    
    return results 