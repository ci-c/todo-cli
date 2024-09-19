import pytest
from datetime import date
from todo_cli.task import Task

@pytest.mark.parametrize("input_string, expected_task", [
    ("(A) High priority task", {
        "description": "High priority task",
        "priority": "A",
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
        "priority": "B",
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
    with pytest.raises(ValueError):
        Task(priority=26)
    with pytest.raises(ValueError):
        Task(priority=-1)

@pytest.mark.parametrize(
    "task_string, expected_priority, expected_completed, expected_description",
    [
        ("(A) Priority task", 0, False, "Priority task"),
        ("x Completed task", None, True, "Completed task"),
        ("2023-01-01 Task with date", None, False, "Task with date"),
        ("+project @context Task with project and context", None, False, "Task with project and context"),
        ("Task with due:2023-12-31 tag", None, False, "Task with tag"),
    ]
)
def test_task_from_string(task_string, expected_priority, expected_completed, expected_description):
    task = Task().from_string(task_string)
    assert task.priority == expected_priority
    assert task.completed == expected_completed
    assert task.description == expected_description

def test_task_is_overdue():
    overdue_task = Task(due_date=date(2022, 1, 1))
    assert overdue_task.is_overdue(virtual_now=date(2023, 1, 1))

    future_task = Task(due_date=date(2024, 1, 1))
    assert not future_task.is_overdue(virtual_now=date(2023, 1, 1))

def test_task_merge():
    task1 = Task(priority=1, description="Task 1", contexts=["work"])
    task2 = Task(priority=2, description="Task 2", contexts=["home"])

    conflict = task1.merge(task2)

    assert task1.priority == 1
    assert task1.description == "Task 1"
    assert set(task1.contexts) == {"work", "home"}
    assert conflict["priority"]
    assert conflict["description"]

if __name__ == "__main__":
    pytest.main()
