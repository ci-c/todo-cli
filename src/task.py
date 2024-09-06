from dataclasses import dataclass, field
from typing import List, Optional, Callable, Iterator, Any, Tuple
import re
from datetime import datetime, timedelta, date
from functools import total_ordering
import click
from dateutil import parser as dtparser
from dateutil.relativedelta import relativedelta
from contextlib import suppress


@total_ordering
@dataclass
class Task:
    """
    Represents a task with various attributes such as priority, completion status,
    creation and completion dates, associated projects and contexts, tags, and a description.

    The `Task` class provides methods to compare tasks based on priority, creation date,
    and description.
    """

    priority: Optional[int] = None
    completed: bool = False
    creation_date: Optional[datetime|date] = None
    completion_date: Optional[datetime|date] = None
    projects: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    tags: dict = field(default_factory=dict)
    description: str = ""

    def __clear(self):
        self.completed = False
        self.priority = None
        self.creation_date = None
        self.completion_date = None
        self.projects = []
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
        if self.priority is not None and not (0 <= self.priority <= 25):
            raise ValueError("Priority must be a number between 0 and 25 (inclusive).")

    def __hash__(self):
        return hash((
        self.priority,
        self.completed,
        self.creation_date, 
        self.completion_date, #TODO rename to due_date
        tuple(self.projects), #TODO rename to dependedes
        tuple(self.contexts),
        frozenset(self.tags.items()),
        self.description
    ))
    
    def _get_real_priority(self) -> Tuple[bool, datetime, int, datetime, int, str]:
        """
        Returns the priority tuple for sorting tasks.

        The tuple includes:
            - Completion status (bool): `True` if not completed.
            - Due date (datetime): Adjusted due date with a default of tomorrow.
            - Priority (int): Task priority or `-1` if not set.
            - Creation date (datetime): Task creation date or `datetime.min`.
            - Context count (int): Negative count of associated projects, contexts, and tags.
            - Description (str): Task description for tie-breaking.
        """
        due_var: datetime|date = self.completion_date or (datetime.now() + timedelta(days=1))
        if isinstance(due_var, date) and not isinstance(due_var, datetime):
            due_var = datetime.combine(due_var, datetime.min.time())
        
        if due_var > datetime.now():
            due_var += timedelta(days=1)
        
        creation_date: Optional[datetime | date] = self.creation_date or datetime.now()
        if isinstance(creation_date, date) and not isinstance(creation_date, datetime):
            creation_date = datetime.combine(creation_date, datetime.min.time())

        return (
            self.completed,
            due_var,
            self.priority if self.priority is not None else -1,
            creation_date or datetime.min,
            -(len(self.projects) + len(self.contexts) + len(self.tags)),
            self.description
        )

    def __eq__(self, other: 'Task') -> bool:
        """
        Checks if this task is equal to another task based on their real priorities.

        Args:
            other (Task): The other task to compare with.

        Returns:
            bool: True if the tasks are equal, False otherwise.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self._get_real_priority() == other._get_real_priority()

    def __lt__(self, other: 'Task') -> bool:
        """
        Checks if this task is less than another task based on their real priorities.

        Args:
            other (Task): The other task to compare with.

        Returns:
            bool: True if this task is less than the other task, False otherwise.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self._get_real_priority() < other._get_real_priority()

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
        return f"Task(priority={self.priority}, completed={self.completed}, creation_date={self.creation_date}, completion_date={self.completion_date}, projects={self.projects}, contexts={self.contexts}, tags={self.tags}, description='{self.description}')"

    def from_string(self, task_string: str) -> 'Task':
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
                    priority = ord(priority_char.upper()) - 65 if priority_char.isalpha() else None
                    line = f'pri:{parts[1][1:].strip()}'
            return priority, line

        def extract_creation_date(line: str) -> tuple:
            from contextlib import suppress

            words = line.split()
            creation_date = None
            if words:
                first_word = words[0]
                with suppress(ValueError, OverflowError):
                    creation_date = dtparser.isoparse(first_word) if 'T' in first_word else dtparser.parse(first_word).date()
                    words.pop(0)
            line = ' '.join(words)
            return creation_date, line

        # Reset the task attributes
        self.__clear()

        # Extract completion status
        self.completed = task_string.startswith('x ')
        task_string = task_string[2:].strip() if self.completed else task_string

        # Extract priority
        self.priority, task_string = extract_priority(task_string)

        # Extract creation date
        self.creation_date, task_string = extract_creation_date(task_string)

        # Process remaining words
        words = task_string.split()
        for word in words:
            if word.startswith('+'):
                self.projects.append(word[1:])
            elif word.startswith('@'):
                self.contexts.append(word[1:])
            elif ':' in word:
                key, value = word.split(':', 1)
                if key == 'due':
                    with suppress(ValueError, OverflowError):
                        self.completion_date = dtparser.isoparse(value) if 'T' in value else dtparser.parse(value).date()
                else:
                    self.tags[key] = value
            else:
                self.description += f'{word} '

        self.description = self.description.strip()

        return self
    
    def to_string(self, color=False, todotxt_format:bool=True) -> str: #TOD custom postprocess function
        """
        Converts the task to a string representation in the todo.txt format.

        Returns:
            str: The string representation of the task in todo.txt format.
        """
        
        parts:list[str] = []
        
        def post_process(
            str:Optional[str|list[str]],
            soft_function:Optional[Callable[[str],str]]=None,
            hard_function:Optional[Callable[[str],str]]=None,
            is_itter:bool=False
            ):
            if str is None:
                pass
            elif is_itter:
                for i in str:
                    post_process(str=i,soft_function=soft_function,hard_function=hard_function,is_itter=False)
            else:
                if soft_function: #WARNING this is a soft function not for color? this for formatinf string
                    str = soft_function(str)
                if color:
                    if hard_function:
                        str = hard_function(str)
                    elif self.priority == 0:
                        str = click.style(str, fg="red")
                    elif self.priority == 1:
                        str = click.style(str, fg="yellow")
                    elif self.priority == 2:
                        str = click.style(str, fg="green")
                    elif self.priority == 3:
                        str = click.style(str, fg="blue")
                parts.append(str.__str__())
        if todotxt_format:
            post_process(self.completed,soft_function=lambda x: 'x' if self.completed else '')
            post_process(self.creation_date,soft_function=lambda x:x.isoformat(),hard_function=lambda str: click.style(str, fg="bright_black")) 
            post_process(self.priority, soft_function=lambda x:f"({chr(65 + x)})")
        else:
            post_process(self.completed,soft_function=lambda x: '[x]' if self.completed else '[ ]')
            post_process(f"({chr(65 + self.priority)})" if self.priority is not None else '   ')
        post_process(self.description)
        post_process(self.completion_date, soft_function=lambda x: f'due:{x.isoformat()}',hard_function=lambda str: click.style(str, fg="blue")) 
        post_process(self.projects, soft_function=lambda x: f"+{x}", hard_function=lambda str: click.style(str, fg="magenta"), is_itter=True)
        post_process(self.contexts, soft_function=lambda x: f"@{x}", hard_function=lambda str: click.style(str, fg="cyan"), is_itter=True)
        for key, value in self.tags.items():
            if key == "rec":
                hard_f = lambda str: click.style(str, fg="blue")
            else:
                hard_f = lambda str: click.style(str, fg="bright_white")
            post_process(f"{key}:{value}",hard_function=hard_f)
    
        output:str = " ".join(parts)
        if color: # post-post-process...
            if self.completed:
                output = click.unstyle(output)
                output = click.style(output, fg='bright_black',strikethrough=True)
        return output

    def mark_as_completed(self) -> Optional['Task']:
        """
        Marks the task as completed. If recurring, updates the due date and returns the old task.
        
        Returns:
            Optional['Task']: The old task if it was recurring, otherwise `None`.
        """
        self.completed = True
        if 'rec' in self.tags.keys():
            old:Task = self
            self.completion_date = self.calculate_next_due_date()
            self.completed = False
            return old
        return None

    def get_next_due_date(self) -> datetime | date:
        """
        Calculates the next due date based on the recurrence pattern.
        """
        # This implementation handles both 'rec:1d' and 'rec:+1d' formats
        current_date:datetime | date = self.completion_date or datetime.now()
        def parse_recurring_interval(interval_str: str) -> tuple[relativedelta, bool]:
            is_strict:bool = interval_str.startswith('+')
            if is_strict:
                interval_str = interval_str[1:]
            time_units = {
                'd': lambda n: relativedelta(days=n),
                'b': lambda n: relativedelta(days=n),  #TODO! Busness days counting is not worked correctly
                'w': lambda n: relativedelta(weeks=n),
                'm': lambda n: relativedelta(months=n),
                'y': lambda n: relativedelta(years=n)
            }
            
            # Регулярное выражение для поиска всех пар "число + единица времени (необязательно)"
            matches = re.findall(r'(\d+)([dbwmy]?)', interval_str)
            
            total_delta:relativedelta = relativedelta()
            
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
        out:bool = True
        out = out and self.description is not None
        out = out and self.priority is not None
        out = out and self.completion_date is not None
        return out
    def is_full_event(self) -> bool: #TODO
        """
        Checks if the event has all the required fields
        """
        pass
    def merge(self, other_task:'Task', hard:bool=False,self_priority:bool=True)->bool: #TODO
        """_summary_

        Args:
            other_task (Task): _description_
            hard (bool, optional): _description_. Defaults to False.
            self_priority (bool, optional): _description_. Defaults to True.

        Returns:
            bool: return True if found merge conflict.
        """
        return True
    def is_planed_event(self)->bool:#TODO
        pass
    def is_planable_task(self)->bool:#TODO
        pass
    def is_overdue(self)->bool:
        if self.completion_date is None:
            return False
        if isinstance(self.completion_date, date):
            return self.completion_date < date.today()
        else:
            return self.completion_date < datetime.now()
    def to_dict(self) -> dict:
        out: dict = {
            'priority': self.priority,
            'description': self.description,
            'complited': self.completed,
            'completion_date': (
                self.completion_date.isoformat() if self.completion_date else None
            ),
        }
        out['contexts'] = self.contexts
        out['tags'] = self.tags
        out['projects'] = self.projects
        out['creation_date'] = self.creation_date.isoformat() if self.creation_date else None
        return out
