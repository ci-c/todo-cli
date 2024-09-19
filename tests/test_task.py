import pytest
from datetime import date, datetime, timedelta
from todo_cli.task import Task


@pytest.mark.parametrize("input_string, expected_task", [
    ("(A) High priority task", {
        "description": "High priority task",
        "priority": 0,
        "completed": False,
        "creation_date": None,
        "due_date": None,
        "dependencies": [],
        "contexts": [],
        "tags": {}
    }),
    ("x Completed task", {
        "description": "Completed task",
        "priority": None,
        "completed": True,
        "creation_date": None,
        "due_date": None,
        "dependencies": [],
        "contexts": [],
        "tags": {}
    }),
    ("2023-05-15 Task with creation date", {
        "description": "Task with creation date",
        "priority": None,
        "completed": False,
        "creation_date": date(2023, 5, 15),
        "due_date": None,
        "dependencies": [],
        "contexts": [],
        "tags": {}
    }),
    ("+project1 Task with project", {
        "description": "Task with project",
        "priority": None,
        "completed": False,
        "creation_date": None,
        "due_date": None,
        "dependencies": ["project1"],
        "contexts": [],
        "tags": {}
    }),
    ("@home Task with context", {
        "description": "Task with context",
        "priority": None,
        "completed": False,
        "creation_date": None,
        "due_date": None,
        "dependencies": [],
        "contexts": ["home"],
        "tags": {}
    }),
    ("Task with tag:important", {
        "description": "Task with",
        "priority": None,
        "completed": False,
        "creation_date": None,
        "due_date": None,
        "dependencies": [],
        "contexts": [],
        "tags": {"tag": "important"}
    }),
    ("(B) 2023-06-30 Task with priority and due date due:2023-06-30", {
        "description": "Task with priority and due date",
        "priority": 1,
        "completed": False,
        "creation_date": date(2023, 6, 30),
        "due_date": date(2023, 6, 30),
        "dependencies": [],
        "contexts": [],
        "tags": {}
    }),
    ("x 2023-01-01 Completed task with completion date", {
        "description": "Completed task with completion date",
        "priority": None,
        "completed": True,
        "creation_date": date(2023, 1, 1),
        "due_date": None,
        "dependencies": [],
        "contexts": [],
        "tags": {}
    }),
    ("+project1 @work Task with project and context", {
        "description": "Task with project and context",
        "priority": None,
        "completed": False,
        "creation_date": None,
        "due_date": None,
        "dependencies": ["project1"],
        "contexts": ["work"],
        "tags": {}
    }),
    ("Task with multiple tags tag:urgent tag:important", {
        "description": "Task with multiple tags",
        "priority": None,
        "completed": False,
        "creation_date": None,
        "due_date": None,
        "dependencies": [],
        "contexts": [],
        "tags": {"tag": ["urgent", "important"]}
    }),
])
def test_task_from_string(input_string, expected_task):
    """Test task creation from string."""
    task = Task().from_string(input_string)

    assert task.description == expected_task["description"]
    assert task.priority == expected_task["priority"]
    assert task.completed == expected_task["completed"]
    assert task.creation_date == expected_task["creation_date"]
    assert task.due_date == expected_task["due_date"]
    assert task.dependencies == expected_task["dependencies"]
    assert task.contexts == expected_task["contexts"]
    assert task.tags == expected_task["tags"]


def test_task_validation():
    """Test task validation."""
    with pytest.raises(ValueError):
        Task(priority=26)
    with pytest.raises(ValueError):
        Task(priority=-1)


def test_task_is_overdue():
    """Test task overdue functionality."""
    overdue_task = Task(due_date=date(2022, 1, 1))
    assert overdue_task.is_overdue(virtual_now=date(2023, 1, 1))

    future_task = Task(due_date=date(2024, 1, 1))
    assert not future_task.is_overdue(virtual_now=date(2023, 1, 1))


def test_task_merge():
    """Test task merge functionality."""
    task1 = Task(priority=1, description="Task 1", contexts=["work"])
    task2 = Task(priority=2, description="Task 2", contexts=["home"])

    conflict = task1.merge(task2)

    assert task1.priority == 1
    assert task1.description == "Task 1"
    assert set(task1.contexts) == {"work", "home"}
    assert conflict["priority"]
    assert conflict["description"]


def test_task_is_full_task():
    """Test if a task is a full task."""
    full_task = Task(description="Full task", priority=1, due_date=date.today())
    assert full_task.is_full_task()

    incomplete_task = Task(description="Incomplete task")
    assert not incomplete_task.is_full_task()


def test_task_is_full_event():
    """Test if a task is a full event."""
    full_event = Task(description="Full event", due_date=datetime.now(), tags={"dur": "2h"})
    assert full_event.is_full_event()

    incomplete_event = Task(description="Incomplete event", due_date=date.today())
    assert not incomplete_event.is_full_event()


def test_task_get_next_due_date():
    """Test getting the next due date for a task."""
    task = Task(due_date=date(2023, 5, 1), tags={"rec": "1w"})
    next_due = task.get_next_due_date()
    assert next_due == date(2023, 5, 8)

    task = Task(due_date=date(2023, 5, 1), tags={"rec": "+1m"})
    next_due = task.get_next_due_date()
    assert next_due == date(2023, 6, 1)


def test_task_mark_as_completed():
    """Test marking a task as completed."""
    task = Task(description="Recurring task", tags={"rec": "1d"}, due_date=date(2023, 5, 1))
    old_task = task.mark_as_completed()
    assert old_task is not None
    assert old_task.completed
    assert task.due_date == date(2023, 5, 2)
    assert not task.completed

    non_recurring_task = Task(description="Non-recurring task")
    result = non_recurring_task.mark_as_completed()
    assert result is None
    assert non_recurring_task.completed


def test_task_to_dict():
    """Test converting a task to a dictionary."""
    task = Task(
        priority=1,
        description="Test task",
        completed=False,
        due_date=date(2023, 5, 1),
        contexts=["work"],
        tags={"important": "yes"},
        dependencies=["project1"],
        creation_date=date(2023, 4, 30)
    )
    task_dict = task.to_dict()
    assert task_dict == {
        'priority': 1,
        'description': "Test task",
        'completed': False,
        'due_date': '2023-05-01',
        'contexts': ["work"],
        'tags': {"important": "yes"},
        'dependencies': ["project1"],
        'creation_date': '2023-04-30'
    }


def test_task_from_dict():
    """Test creating a task from a dictionary."""
    task_dict = {
        'priority': 2,
        'description': "From dict task",
        'completed': True,
        'due_date': '2023-06-01',
        'contexts': ["home"],
        'tags': {"urgent": "no"},
        'dependencies': ["chore1"],
        'creation_date': '2023-05-31'
    }
    task = Task()
    task.from_dict(task_dict)
    assert task.priority == 2
    assert task.description == "From dict task"
    assert task.completed
    assert task.due_date == date(2023, 6, 1)
    assert task.contexts == ["home"]
    assert task.tags == {"urgent": "no"}
    assert task.dependencies == ["chore1"]
    assert task.creation_date == date(2023, 5, 31)


def test_task_merge_extended():
    """Test merging tasks with extended functionality."""
    task1 = Task(priority=1, description="Task 1", contexts=["work"], tags={"important": "yes"})
    task2 = Task(priority=2, description="Task 2", contexts=["home"], tags={"urgent": "no"})

    conflict = task1.merge(task2)

    assert task1.priority == 1
    assert task1.description == "Task 1"
    assert set(task1.contexts) == {"work", "home"}
    assert task1.tags == {"important": "yes", "urgent": "no"}
    assert conflict['priority']
    assert conflict['description']
    assert not conflict['contexts']
    assert not conflict['tags']['urgent']


def test_task_is_plannable_task():
    """Test if a task is plannable."""
    plannable_task = Task(description="Plannable task", tags={"dur": "2h"})
    assert plannable_task.is_plannable_task()

    non_plannable_task = Task(description="Non-plannable task")
    assert not non_plannable_task.is_plannable_task()


def test_task_is_overdue_extended():
    """Test if a task is overdue with extended functionality."""
    overdue_task = Task(due_date=date.today() - timedelta(days=1))
    assert overdue_task.is_overdue()

    future_task = Task(due_date=date.today() + timedelta(days=1))
    assert not future_task.is_overdue()

    no_due_date_task = Task(description="No due date")
    assert not no_due_date_task.is_overdue()


if __name__ == "__main__":
    pytest.main()
