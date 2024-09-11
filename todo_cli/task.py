"""
Represents a task with various attributes such as priority, completion status,
creation and completion dates, associated dependencies and contexts, tags, and
a description.

The `Task` class provides methods to compare tasks based on priority, creation
date, and description.
"""

import re
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from functools import total_ordering
from typing import Callable, List, Optional, Tuple

import click
from dateutil import parser as dtparser
from dateutil.relativedelta import relativedelta


@total_ordering
@dataclass
class Task:
    """
    Represents a task with various attributes such as priority, completion
    status, creation and completion dates, associated dependencies
    and contexts, tags, and a description.

    The `Task` class provides methods to compare tasks based on priority,
    creation date, and description.
    """

    priority: Optional[int] = None
    completed: bool = False
    creation_date: Optional[datetime | date] = None
    due_date: Optional[datetime | date] = None
    dependencies: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    tags: dict = field(default_factory=dict)
    description: str = ""

    def __clear(self):
        self.completed = False
        self.priority = None
        self.creation_date = None
        self.due_date = None
        self.dependencies = []
        self.contexts = []
        self.tags = {}
        self.description = ""

    def __post_init__(self):
        """
        Validates the task's priority and dates after initialization.
        """
        self._validate_priority()

    def _validate_priority(self):
        """
        Validates that the priority is a number between 0 and 25 (inclusive).
        Raises ValueError if the priority is invalid.
        """
        if self.priority is not None and not 0 <= self.priority <= 25:
            raise ValueError(
                "Priority must be a number between 0 and 25 (inclusive)."
            )

    def __hash__(self):
        return hash((
            self.priority,
            self.completed,
            self.creation_date,
            self.due_date,
            tuple(self.dependencies),
            tuple(self.contexts),
            frozenset(self.tags.items()),
            self.description
        ))

    def get_real_priority(self) -> Tuple[
            bool, datetime, int, datetime, int, str
    ]:
        """
        Returns the priority tuple for sorting tasks.

        The tuple includes:
            - Completion status (bool): `True` if not completed.
            - Due date (datetime): Adjusted due date.
            - Priority (int): Task priority or `-1` if not set.
            - Creation date (datetime): Task creation date or `datetime.min`.
            - Context count (int): Negative count of associated context.
            - Description (str): Task description for tie-breaking.
        """
        due_var: datetime | date = self.due_date or (
            datetime.now() + timedelta(days=1)
        )
        if isinstance(due_var, date) and not isinstance(due_var, datetime):
            due_var = datetime.combine(due_var, datetime.min.time())

        if due_var > datetime.now():
            due_var += timedelta(days=1)

        creation_date: Optional[datetime | date] = (
            self.creation_date or datetime.now()
        )
        if isinstance(creation_date, date) and not isinstance(
            creation_date, datetime
        ):
            creation_date = datetime.combine(
                creation_date, datetime.min.time()
                )

        return (
            self.completed,
            due_var,
            self.priority if self.priority is not None else -1,
            creation_date or datetime.min,
            -(len(self.dependencies) + len(self.contexts) + len(self.tags)),
            self.description
        )

    def __eq__(self, other: 'Task') -> bool:
        """
        Checks if this task is equal to another task based on their real
        priorities.

        Args:
            other (Task): The other task to compare with.

        Returns:
            bool: True if the tasks are equal, False otherwise.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self.get_real_priority() == other._get_real_priority()

    def __lt__(self, other: 'Task') -> bool:
        """
        Checks if this task is less than another task based on their real
        priorities.

        Args:
            other (Task): The other task to compare with.

        Returns:
            bool: True if this task is less than the other task, False
            otherwise.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self.get_real_priority() < other._get_real_priority()

    def __str__(self) -> str:
        """
        Returns a string representation of the task in the todo.txt format.

        Returns:
            str: The string representation of the task.
        """
        return self.to_string()

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Task object.

        Returns:
            str: A string containing all the attributes of the Task object.
        """
        return (
            f"Task(priority={self.priority}, completed={self.completed}, "
            f"creation_date={self.creation_date}, "
            f"due_date={self.due_date}, "
            f"dependencies={self.dependencies}, contexts={self.contexts}, "
            f"tags={self.tags}, description='{self.description}')"
        )

    def copy(self) -> 'Task':
        """
        Creates and returns a deep copy of the Task object.

        Returns:
            Task: A new Task object with the same attributes as the original.
        """
        return Task(
            priority=self.priority,
            completed=self.completed,
            creation_date=self.creation_date,
            due_date=self.due_date,
            dependencies=self.dependencies.copy(),
            contexts=self.contexts.copy(),
            tags=self.tags.copy(),
            description=self.description
        )

    def from_dict(self, task_dict: dict) -> None:
        """
        Constructs a Task object from a dictionary representation.
        Args:
            task_dict (dict): A dictionary containing the attributes of the
            task.
        """
        self.priority = task_dict.get('priority')
        self.completed = task_dict.get('completed')
        self.creation_date = task_dict.get('creation_date')
        self.due_date = task_dict.get('due_date')
        self.dependencies = task_dict.get('dependencies', [])
        self.contexts = task_dict.get('contexts', [])
        self.tags = task_dict.get('tags', [])
        self.description = task_dict.get('description')

    def from_other(self, other: 'Task') -> None:
        """
        Copies the attributes of another Task object to this Task object.
        Args:
            other (Task): The other Task object to copy attributes from.
        """
        self.priority = other.priority
        self.completed = other.completed
        self.creation_date = other.creation_date
        self.due_date = other.due_date
        self.dependencies = other.dependencies.copy()
        self.contexts = other.contexts.copy()
        self.tags = other.tags.copy()
        self.description = other.description

    def from_string(self, task_string: str) -> 'Task':
        """
        Constructs a Task object from a string representation in
        the todo.txt format.

        Args:
            task_string (str): The string representation of the task
            in todo.txt format.

        Returns:
            Task: A Task object constructed from the input string.
        """
        def extract_priority(line: str) -> tuple:
            priority = None
            if line.startswith('(') and ')' in line:
                end_paren_index = line.index(')')
                priority_char = line[1:end_paren_index]
                if priority_char.isalpha() and len(priority_char) == 1:
                    priority = ord(priority_char.upper()) - 65
                    line = line[end_paren_index + 1:].strip()
            elif 'pri:' in line:
                parts = line.split('pri:')
                if len(parts) > 1 and parts[1]:
                    priority_char = parts[1][0]
                    priority = (
                        ord(priority_char.upper()) - 65
                        if priority_char.isalpha() else None
                    )
                    line = f'pri:{parts[1][1:].strip()}'
            return priority, line

        def extract_creation_date(line: str) -> tuple:
            words = line.split()
            creation_date = None
            if words:
                first_word = words[0]
                with suppress(ValueError, OverflowError):
                    creation_date = (
                        dtparser.isoparse(first_word)
                        if 'T' in first_word
                        else dtparser.parse(first_word).date()
                    )
                    words.pop(0)
            line = ' '.join(words)
            return creation_date, line

        # Reset the task attributes
        self.__clear()

        # Extract completion status
        self.completed = task_string.startswith('x ')
        task_string = (
            task_string[2:].strip() if self.completed else task_string
        )

        # Extract priority
        self.priority, task_string = extract_priority(task_string)

        # Extract creation date
        self.creation_date, task_string = extract_creation_date(task_string)

        # Process remaining words
        words = task_string.split()
        for word in words:
            if word.startswith('+'):
                self.dependencies.append(word[1:])
            elif word.startswith('@'):
                self.contexts.append(word[1:])
            elif ':' in word:
                key, value = word.split(':', 1)
                if key == 'due':
                    with suppress(ValueError, OverflowError):
                        self.due_date = (
                            dtparser.isoparse(value)
                            if 'T' in value
                            else dtparser.parse(value).date()
                        )
                else:
                    self.tags[key] = value
            else:
                self.description += f'{word} '

        self.description = self.description.strip()

        return self

    def to_string(self, color=False, todotxt_format: bool = True) -> str:
        """
        Converts the task to a string representation in the todo.txt format.

        Returns:
            str: The string representation of the task in todo.txt format.
        """

        parts: list[str] = []

        def post_process(
            text_value: Optional[str | list[str]],
            soft_function: Optional[Callable[[str], str]] = None,
            hard_function: Optional[Callable[[str], str]] = None,
            is_itter: bool = False
        ):
            if text_value is None or text_value == '' or text_value == []:
                pass
            elif is_itter:
                for i in text_value:
                    post_process(
                        text_value=i,
                        soft_function=soft_function,
                        hard_function=hard_function,
                        is_itter=False
                    )
            else:
                if soft_function:
                    text_value = soft_function(text_value)
                if color:
                    if hard_function:
                        text_value = hard_function(text_value)
                    elif self.priority == 0:
                        text_value = click.style(text_value, fg="red")
                    elif self.priority == 1:
                        text_value = click.style(text_value, fg="yellow")
                    elif self.priority == 2:
                        text_value = click.style(text_value, fg="green")
                    elif self.priority == 3:
                        text_value = click.style(text_value, fg="blue")
                parts.append(str(text_value))

        if todotxt_format:
            post_process(
                self.completed,
                soft_function=lambda x: 'x' if self.completed else ''
            )
            post_process(
                self.creation_date,
                soft_function=lambda x: x.isoformat(),
                hard_function=lambda text_value: click.style(
                    text_value, fg="bright_black"
                    )
            )
            post_process(
                self.priority,
                soft_function=lambda x: f"({chr(65 + x)})"
            )
        else:
            post_process(
                self.completed,
                soft_function=lambda x: '[x]' if self.completed else '[ ]'
            )
            post_process(
                f"({chr(65 + self.priority)})"
                if self.priority is not None else '   '
            )
        post_process(self.description)
        post_process(
            self.due_date,
            soft_function=lambda x: f'due:{x.isoformat()}',
            hard_function=lambda text_value: click.style(text_value, fg="blue")
        )
        post_process(
            self.dependencies,
            soft_function=lambda x: f"+{x}",
            hard_function=lambda text_value: click.style(
                text_value, fg="magenta"
                ),
            is_itter=True
        )
        post_process(
            self.contexts,
            soft_function=lambda x: f"@{x}",
            hard_function=lambda text_value: click.style(
                text_value, fg="cyan"
                ),
            is_itter=True
        )
        for key, value in self.tags.items():
            def hard_f_rec(text_value):
                return click.style(text_value, fg="blue")

            def hard_f_other(text_value):
                return click.style(text_value, fg="bright_white")

            if key == "rec":
                post_process(f"{key}:{value}", hard_function=hard_f_rec)
            else:
                post_process(f"{key}:{value}", hard_function=hard_f_other)

        output: str = " ".join(filter(bool, parts))
        if color and self.completed:
            output = click.unstyle(output)
            output = click.style(output, fg='bright_black', strikethrough=True)
        return output

    def mark_as_completed(self) -> Optional['Task']:
        """
        Marks the task as completed. If recurring, updates the due date and
        returns the old task.

        Returns:
            Optional['Task']: The old task if it was recurring, otherwise
            `None`.
        """
        self.completed = True
        if 'rec' in self.tags:
            old: Task = self
            self.due_date = self.get_next_due_date()
            self.completed = False
            return old
        return None

    def get_next_due_date(self) -> datetime | date:
        """
        Calculates the next due date based on the recurrence pattern.
        """
        # This implementation handles both 'rec:1d' and 'rec:+1d' formats
        current_date: datetime | date = self.due_date or datetime.now()

        def parse_recurring_interval(interval_str: str) -> tuple[
            relativedelta, bool
        ]:
            is_strict: bool = interval_str.startswith('+')
            if is_strict:
                interval_str = interval_str[1:]
            time_units = {
                'd': lambda n: relativedelta(days=n),
                'b': lambda n: relativedelta(days=n),  # TODO! Busness days
                'w': lambda n: relativedelta(weeks=n),  # counting is not
                'm': lambda n: relativedelta(months=n),  # worked correctly
                'y': lambda n: relativedelta(years=n)
            }

            matches = re.findall(r'(\d+)([dbwmy]?)', interval_str)

            total_delta: relativedelta = relativedelta()

            for number, unit in matches:
                if unit == '':
                    unit = 'd'
                if unit in time_units:
                    total_delta += time_units[unit](int(number))
                else:
                    raise ValueError(f"Unknow time unit: {unit}")

            return total_delta, is_strict

        strict, interval = parse_recurring_interval(self.tags['rec'])
        if not strict:
            if isinstance(current_date, datetime):
                current_date = date.today()
            else:
                current_date = datetime.now()
        return current_date + interval

    def is_full_task(self) -> bool:
        """
        Determines if the task is considered full based on its attributes.

        A task is deemed full if it has a description, a priority, and a
        due date. This method checks these attributes and returns a
        boolean indicating the completeness of the task.

        Args:
            self: The instance of the task.

        Returns:
            bool: True if the task is full, False otherwise.
        """
        return (
            self.description is not None
            and self.priority is not None
            and self.due_date is not None
        )

    def is_full_event(self) -> bool:
        """
        Checks if the event has all the required fields
        """
        return (
            self.description is not None
            and isinstance(datetime, self.due_date)
            and self.tags.get('dur') is not None
        )

    def merge(self, other_task: 'Task', hard: bool = False,
              self_priority: bool = True) -> dict[str, dict[str, bool] | bool]:
        """
        Merges the current task with another task, updating various
        attributes based on specified rules. This function allows
        for the combination of task properties such as priority,
        completion status, dates, dependencies, contexts, tags, and
        description, while also handling potential conflicts.

        Args:
            other_task (Task): The task to merge with the current task.
            hard (bool, optional): If True, forces the description to be
            replaced regardless of conflicts. Defaults to False.
            self_priority (bool, optional): If True, retains the
            current task's priority when merging. Defaults to True.

        Returns:
            dict[str, bool]: A dictionary indicating the status of the
            merge operation for each attribute.
        """

        def merge_property(self_value, other_value,
                           hard: bool, self_priority: bool):
            conflict = False
            if not self_value:
                self_value = other_value
            elif self_value != other_value and other_value:
                conflict = True
                if hard and not self_priority:
                    self_value = other_value
            return self_value, conflict

        conflict: dict[str, dict[str, bool] | bool] = {}
        self.priority, conflict['priority'] = merge_property(
            self.priority, other_task.priority, hard, self_priority
        )
        self.description, conflict['description'] = merge_property(
            self.description, other_task.description, hard, self_priority
        )
        self.completed, conflict['completed'] = merge_property(
            self.completed, other_task.completed, hard, self_priority
        )
        self.due_date, conflict['due_date'] = merge_property(
            self.due_date, other_task.due_date, hard, self_priority
        )
        for context in other_task.contexts:
            if context not in self.contexts:
                self.contexts.append(context)
        conflict['tags'] = {}
        for tag in other_task.tags:
            if tag not in self.tags:
                self.tags[tag] = other_task.tags[tag]
            else:
                self.tags[tag], conflict['tags'][tag] = merge_property(
                    self.tags[tag], other_task.tags[tag], hard, self_priority
                )
        for dependency in other_task.dependencies:
            if dependency not in self.dependencies:
                self.dependencies.append(dependency)
        self.creation_date, conflict['creation_date'] = merge_property(
            self.creation_date, other_task.creation_date, hard, self_priority
        )
        return conflict

    def is_planable_task(self) -> bool:
        """
        Check if the task is a plannable task.

        Returns:
            bool: True if the task is plannable, False otherwise.
        """
        return (
            self.description is not None
            and self.tags.get('dur') is not None
        )

    def is_overdue(self,
                   virtual_now: Optional[date | datetime] = None
                   ) -> bool:
        """
        Check if the task is overdue.

        Args:
            virtual_now (Optional[date | datetime]): The current date/time
            to compare against. Defaults to None.

        Returns:
            bool: True if the task is overdue, False otherwise.
        """
        if self.due_date is None:
            return False

        current_time = virtual_now or (
            date.today() if isinstance(self.due_date, date) else datetime.now()
            )

        return self.due_date < current_time

    def to_dict(self) -> dict:
        """
        Convert the task to a dictionary representation.

        Returns:
            dict: A dictionary containing the task's attributes.
        """
        return {
            'priority': self.priority,
            'description': self.description,
            'completed': self.completed,
            'due_date': (self.due_date.isoformat() if self.due_date else None),
            'contexts': self.contexts,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'creation_date': (self.creation_date.isoformat()
                              if self.creation_date else None),
        }
