from typing import Dict, List, Optional, Set
from collections import defaultdict, deque

from ..state.models import TaskState, TaskStatus


class TaskGraph:
    """
    Task Dependency Graph - Manages task dependencies and execution order.
    
    Supports:
    - Sequential execution
    - Parallel execution (when dependencies allow)
    - Dependency tracking
    - Cycle detection
    """
    
    def __init__(self):
        self.tasks: Dict[str, TaskState] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.dependents: Dict[str, Set[str]] = defaultdict(set)
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
    
    def add_task(self, task: TaskState) -> None:
        """Add a task to the graph"""
        self.tasks[task.task_id] = task
        
        # Register dependencies
        for dep_id in task.dependencies:
            self.dependencies[task.task_id].add(dep_id)
            self.dependents[dep_id].add(task.task_id)
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_ready_tasks(self) -> List[TaskState]:
        """
        Get tasks that are ready to execute.
        A task is ready if:
        - It's pending
        - All its dependencies are completed
        """
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                dependencies_met = all(
                    dep_id in self.completed_tasks for dep_id in task.dependencies
                )
                if dependencies_met:
                    ready_tasks.append(task)
        
        # Sort by priority (high > medium > low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        ready_tasks.sort(
            key=lambda t: priority_order.get(t.input_data.get("priority", "medium"), 1)
        )
        
        return ready_tasks
    
    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.completed_tasks.add(task_id)
    
    def mark_failed(self, task_id: str) -> None:
        """Mark a task as failed"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.failed_tasks.add(task_id)
    
    def is_complete(self) -> bool:
        """Check if all tasks are complete (either completed or failed)"""
        if not self.tasks:
            return True
        
        return all(
            task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            for task in self.tasks.values()
        )
    
    def has_pending_tasks(self) -> bool:
        """Check if there are pending tasks"""
        return any(
            task.status == TaskStatus.PENDING for task in self.tasks.values()
        )
    
    def has_cycles(self) -> bool:
        """Detect if the graph has cycles (should not happen in valid plans)"""
        visited = set()
        recursion_stack = set()
        
        def has_cycle_util(task_id: str) -> bool:
            visited.add(task_id)
            recursion_stack.add(task_id)
            
            for neighbor in self.dependencies[task_id]:
                if neighbor not in visited:
                    if has_cycle_util(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True
            
            recursion_stack.remove(task_id)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle_util(task_id):
                    return True
        
        return False
    
    def get_execution_order(self) -> List[str]:
        """
        Get a valid topological execution order.
        Returns task IDs in order they should be executed.
        """
        in_degree = {task_id: 0 for task_id in self.tasks}
        
        # Calculate in-degrees
        for task_id in self.tasks:
            for dep_id in self.dependencies[task_id]:
                in_degree[task_id] += 1
        
        # Initialize queue with tasks having no dependencies
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        execution_order = []
        
        while queue:
            task_id = queue.popleft()
            execution_order.append(task_id)
            
            # Reduce in-degree for dependent tasks
            for dependent_id in self.dependents[task_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # If not all tasks are in execution_order, there's a cycle
        if len(execution_order) != len(self.tasks):
            raise ValueError("Graph has a cycle, cannot determine execution order")
        
        return execution_order
    
    def get_parallel_groups(self) -> List[List[str]]:
        """
        Group tasks that can be executed in parallel.
        Returns a list of groups, where each group contains task IDs
        that can be executed simultaneously.
        """
        execution_order = self.get_execution_order()
        groups = []
        current_group = []
        completed_in_group = set()
        
        for task_id in execution_order:
            task = self.tasks[task_id]
            
            # Check if all dependencies are in previous groups or current group
            dependencies_satisfied = all(
                dep_id in completed_in_group for dep_id in task.dependencies
            )
            
            if dependencies_satisfied:
                current_group.append(task_id)
            else:
                # Start a new group
                if current_group:
                    groups.append(current_group)
                    completed_in_group.update(current_group)
                current_group = [task_id]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def get_critical_path(self) -> List[str]:
        """
        Calculate the critical path (longest path through the graph).
        Useful for estimating minimum execution time.
        """
        # Estimate task durations
        def get_duration(task: TaskState) -> float:
            return task.input_data.get("estimated_time", 30)
        
        # Calculate earliest start times
        earliest_start = {task_id: 0 for task_id in self.tasks}
        
        execution_order = self.get_execution_order()
        for task_id in execution_order:
            task = self.tasks[task_id]
            max_dep_finish = 0
            for dep_id in task.dependencies:
                dep_task = self.tasks[dep_id]
                dep_finish = earliest_start[dep_id] + get_duration(dep_task)
                max_dep_finish = max(max_dep_finish, dep_finish)
            earliest_start[task_id] = max_dep_finish
        
        # Calculate latest finish times (reverse topological order)
        latest_finish = {task_id: float('inf') for task_id in self.tasks}
        
        # Set finish time for tasks with no dependents
        for task_id in self.tasks:
            if not self.dependents[task_id]:
                latest_finish[task_id] = earliest_start[task_id] + get_duration(self.tasks[task_id])
        
        for task_id in reversed(execution_order):
            task = self.tasks[task_id]
            if self.dependents[task_id]:
                min_dependent_start = min(
                    earliest_start[dep_id] for dep_id in self.dependents[task_id]
                )
                latest_finish[task_id] = min_dependent_start
        
        # Find tasks with zero slack (on critical path)
        critical_tasks = []
        for task_id in execution_order:
            task = self.tasks[task_id]
            slack = latest_finish[task_id] - (earliest_start[task_id] + get_duration(task))
            if abs(slack) < 0.01:  # Essentially zero
                critical_tasks.append(task_id)
        
        return critical_tasks
    
    def estimate_total_time(self) -> float:
        """
        Estimate total execution time considering parallel execution.
        """
        parallel_groups = self.get_parallel_groups()
        
        def get_duration(task: TaskState) -> float:
            return task.input_data.get("estimated_time", 30)
        
        # Time is sum of the slowest task in each parallel group
        total_time = 0
        for group in parallel_groups:
            group_time = max(
                get_duration(self.tasks[task_id]) for task_id in group
            )
            total_time += group_time
        
        return total_time
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary representation"""
        return {
            "tasks": {task_id: task.model_dump() for task_id, task in self.tasks.items()},
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "completed_tasks": list(self.completed_tasks),
            "failed_tasks": list(self.failed_tasks),
            "execution_order": self.get_execution_order(),
            "parallel_groups": self.get_parallel_groups(),
            "critical_path": self.get_critical_path(),
            "estimated_time": self.estimate_total_time(),
        }
