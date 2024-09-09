"""
Represents a list of Task objects with various operations to manipulate and
query the list.

The TaskList class provides methods to add, remove, sort, filter, and perform
other operations on a list of Task objects. It also includes utility methods
like `to_string()` to generate a string representation of the task list, and
`merge()` to synchronize different versions of the same list.

The class also includes methods to check for orphan dependencies, detect
circular dependencies, and remove duplicate tasks based on their unique IDs.
"""

from typing import Any, Callable, Dict, Iterator, List, Optional

from todo_cli.task import Task


class TaskList:
    """
    Represents a list of Task objects with various operations to manipulate
    and query the list.
    """

    def __init__(self, tasks: Optional[List[Task]] = None):
        """
        Initializes a TaskList with an optional list of Task objects.

        Args:
            tasks (List[Task], optional): Initial list of tasks. Defaults to
            None.
        """
        self.tasks: List[Task] = tasks or []

    def __iter__(self) -> Iterator[Task]:
        """
        Returns an iterator over the tasks in the list.

        Returns:
            Iterator[Task]: An iterator over the tasks.
        """
        return iter(self.tasks)

    def __len__(self) -> int:
        """
        Returns the number of tasks in the list.

        Returns:
            int: The number of tasks.
        """
        return len(self.tasks)

    def __getitem__(self, index: int) -> Task:
        """
        Returns the task at the specified index.

        Args:
            index (int): The index of the task to retrieve.

        Returns:
            Task: The task at the specified index.
        """
        return self.tasks[index]

    def __setitem__(self, index: int, value: Task) -> None:
        self.tasks[index] = value

    def get[D: Any](self, index: int, default: 'D' = None) -> Task | 'D':
        """
        Returns the task at the specified index or a default value if the
        index is out of bounds.
        """
        try:
            return self.tasks[index]
        except IndexError:
            return default

    def __eq__(self, other: Any) -> bool:
        """
        Checks if this TaskList is equal to another TaskList.

        Args:
            other (Any): The object to compare with.

        Returns:
            bool: True if the TaskLists are equal, False otherwise.
        """
        if not isinstance(other, TaskList):
            return NotImplemented
        return self.tasks == other.tasks

    def __repr__(self) -> str:
        """
        Returns a string representation of the TaskList.

        Returns:
            str: A string representation of the TaskList.
        """
        return str(self.tasks)

    def __contains__(self, task: Task) -> bool:
        """
        Checks if a task is in the TaskList.

        Args:
            task (Task): The task to check for.

        Returns:
            bool: True if the task is in the TaskList, False otherwise.
        """
        return task in self.tasks

    def add_task(self, task: Task) -> None:
        """
        Adds a task to the list.

        Args:
            task (Task): The task to add.
        """
        self.tasks.append(task)

    def index(
        self,
        task: Task,
        start: Optional[int] = None,
        stop: Optional[int] = None
    ) -> int:
        """
        Returns the index of the specified task in the task list.

        This method searches for the given task within the list of tasks and
        returns its index. If the task is not found, a ValueError will be
        raised.

        Args:
            task (Task): The task to find in the list.
            start (Optional[int]): The starting index for the search
                (inclusive). Defaults to None.
            stop (Optional[int]): The ending index for the search (exclusive).
                Defaults to None.

        Returns:
            int: The index of the task in the list.

        Raises:
            ValueError: If the task is not found in the list.
        """
        return self.tasks.index(value=task, start=start, stop=stop)

    def remove_task(self, task: Task) -> None:
        """
        Removes a task from the list.

        Args:
            task (Task): The task to remove.
        """
        self.tasks.remove(task)

    def selfcheck(self, autorepiar: bool = False) -> dict:
        """
        Performs a self-check on the task list.
        Args:
            autorepiar (bool, optional): Whether to automatically repair the
            task list. Defaults to False.
        Returns:
            dict: A dictionary containing the result of the self-check.
        """
        pass  # return result, errors, autofixed tasks for diff

    def sort(
        self,
        key: Optional[Callable[[Task], Any]] = None,
        reverse: bool = False
    ) -> None:
        """
        Sorts the tasks in the list based on the given key function or real
        priority.

        Args:
            key (Optional[Callable[[Task], Any]], optional): The key function
            for sorting. Defaults to None.
            reverse (bool, optional): Whether to sort in reverse order.
            Defaults to False.
        """
        def default_key(task: Task) -> Any:
            return task.get_real_priority()

        if key is None:
            key = default_key
        self.tasks.sort(key=key, reverse=reverse)

    def filter(self, condition: Callable[[Task], bool]) -> 'TaskList':
        """
        Returns a new TaskList containing tasks that satisfy the given
        condition.

        Args:
            condition (Callable[[Task], bool]): The condition function.

        Returns:
            TaskList: A new TaskList with filtered tasks.
        """
        return TaskList([task for task in self.tasks if condition(task)])

    def find(self, condition: Callable[[Task], bool]) -> Optional[Task]:
        """
        Returns the first task that satisfies the given condition, or None if
        no such task is found.

        Args:
            condition (Callable[[Task], bool]): The condition function.

        Returns:
            Optional[Task]: The first task that satisfies the condition, or
            None.
        """
        return next((task for task in self.tasks if condition(task)), None)

    def find_all(self, condition: Callable[[Task], bool]) -> List[Task]:
        """
        Returns a list of all tasks that satisfy the given condition.
        Args:
            condition (Callable[[Task], bool]): The condition function.

        Returns:
            List[Task]: A list of tasks that satisfy the condition.
        """
        return [task for task in self.tasks if condition(task)]

    def map(self, func: Callable[[Task], Any]) -> List[Any]:
        """
        Applies the given function to each task and returns a list of the
        results.

        Args:
            func (Callable[[Task], Any]): The function to apply to each task.

        Returns:
            List[Any]: A list of results after applying the function to each
            task.
        """
        return list(map(func, self.tasks))

    def to_list(self) -> List[Task]:
        """
        Returns a copy of the internal list of tasks.

        Returns:
            List[Task]: A copy of the list of tasks.
        """
        return self.tasks.copy()

    def to_string(
        self,
        color: bool = False,
        todotxt_format: bool = True
    ) -> str:
        """
        Generates a string representation of the TaskList, with
        each task's string representation separated by a newline.

        Args:
            color (bool): Whether to include ANSI color codes in the output.
            todotxt_format (bool): Whether to format the output
            in the todo.txt format.

        Returns:
            str: A string representation of the TaskList.
        """

        return '\n'.join(
            task.to_string(color=color, todotxt_format=todotxt_format)
            for task in self.tasks
        )

    def __str__(self) -> str:
        return self.to_string()

    def archive(self) -> 'TaskList':
        """
        Archives the completed tasks in the list, returning a new TaskList
        containing the archived tasks.
        """
        archived_tasks = TaskList(
            [task for task in self.tasks if task.completed]
            )
        self.tasks = [task for task in self.tasks if not task.completed]
        return archived_tasks

    def merge(self, other_list: 'TaskList', hard: bool = False,
              self_priority: bool = True) -> Any:   # TODO: fix return type
        """
        Merges this TaskList with another TaskList, combining tasks from both
        lists.
        This function is designed to synchronize different versions of the
        same list.

        The merge process follows these rules:
        1. Tasks present in both lists are updated with the latest
           information.
        2. Tasks present only in the other list are added to this list.
        3. Tasks present only in this list are retained.

        Args:
            other_list (TaskList): Another TaskList to merge with this one.

        Returns:

        """

        conflicts: Dict[Task, Dict[str, dict[str, bool] | bool]] = {}
        for other_task in other_list.tasks:
            existing_task = self.find(
                lambda t, other_task=other_task:
                    t.to_string() == other_task.to_string()
            )
            existing_task_by_id = False
            if other_task.tags.get("id", default=None) is not None:
                existing_task_by_id = self.find(
                    lambda t, other_task=other_task:
                        t.tags.get("id", default=None) == other_task.tags["id"]
                )
            if existing_task:
                pass
            elif existing_task_by_id:
                task_id: int = self.index(existing_task_by_id)
                self[task_id], conflicts[existing_task_by_id] = (
                    existing_task_by_id.merge(
                        other_task=other_task, hard=hard,
                        self_priority=self_priority
                    )
                )
            else:
                self.add_task(other_task)
        return conflicts

    def from_string(self, tasks_string: str) -> None:
        """
        Parses a todotxt string representation of tasks.
        """
        for line in tasks_string.split('\n'):
            if line.startswith('#'):
                continue
            if line := line.strip():
                task = Task().from_string(line)
                self.add_task(task)

    def chek_orphan_dependencies(self) -> List[Task]:
        """
        Checks for orphan dependencies in the task list.
        """
        output: TaskList = TaskList()
        for task in self.tasks:
            for dep_id in task.projects:
                dep = self.find(
                    lambda t, dep_id=dep_id:
                        t.tags.get("id", default=None) == dep_id
                )
                if dep is None:
                    output.add_task(task)

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Builds a graph where keys are task IDs and values are lists of
        dependent task IDs.
        Returns a dictionary representing the dependency graph.
        """
        graph: Dict[str, List[str]] = {task.id: [] for task in self.tasks}
        for task in self.tasks:
            for dep_id in task.projects:
                if dep_id not in graph:
                    graph[dep_id] = []
                graph[dep_id].append(task.id)
        return graph

    def check_circle_dependencies(self) -> List[List[Task]]:
        """
        Finds all cycles in the task dependency graph.
        Returns a list of cycles, where each cycle is represented as a list
        of tasks.
        """
        graph = self._build_dependency_graph()
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: List[List[Task]] = []

        def dfs(task_id: str, path: List[str]) -> None:
            if task_id in rec_stack:
                # Found a cycle
                cycle_start_index = path.index(task_id)
                cycle = [
                    self.find(lambda t, pid=path_id: t.id == pid)
                    for path_id in path[cycle_start_index:]
                ]
                cycles.append(cycle)
                return

            if task_id in visited:
                return

            visited.add(task_id)
            rec_stack.add(task_id)
            path.append(task_id)

            for neighbor in graph.get(task_id, []):
                dfs(neighbor, path)

            rec_stack.remove(task_id)
            path.pop()

        for task in self.tasks:
            if task.id not in visited:
                dfs(task.id, [])

        return cycles

    def check_duplicate_tasks_by_id(self):
        """
        Checks for duplicate tasks in the task list.
        """
        return [
            self.find_all(lambda t, task_id=task.tags.get("id"):
                          t.tags.get("id") == task_id)
            for task in self.tasks
            if task.tags.get("id") is not None
        ]

    def deduplicate(self) -> None:
        """
        Removes duplicate tasks from the task list.
        """
        duplicates = [
            self.find_all(lambda t, task_dict=task.to_dict():
                          t.to_dict() == task_dict)
            for task in self.tasks
        ]
        for duplicate_group in duplicates:
            if len(duplicate_group) > 1:
                for duplicate in duplicate_group[1:]:
                    self.remove_task(duplicate)

    def replan_overdue_tasks(self):
        """
        Replans all overdue tasks in the task list.

        This method iterates through all tasks in the task list and checks if
        each task is overdue. If a task is overdue, it calls the `plan_task`
        method to replan the task.
        """
        for task in self.tasks:
            if task.is_overdue():
                self.plan_task(task)

    def plan_task(self, task: Task) -> Optional[Task]:  # if error return None
        """
        Plans a task by updating its due date, priority, and other properties
        as needed.

        Args:
            task (Task): The task to be planned.

        Returns:
            Optional[Task]: The planned task, or None if an error occurred
            during planning.
        """
        pass
