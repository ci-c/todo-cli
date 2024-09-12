import pytest
from datetime import date
from todo_cli.task import Task


@pytest.fixture
def sample_task():
    return Task(
        priority=1,
        completed=False,
        creation_date=date(2023, 1, 1),
        due_date=date(2023, 12, 31),
        dependencies=["project1"],
        contexts=["work"],
        tags={"tag": "tag1"},
        description="Sample task"
    )


def test_task_initialization(sample_task):
    assert sample_task.priority == 1
    assert not sample_task.completed
    assert sample_task.creation_date == date(2023, 1, 1)
    assert sample_task.due_date == date(2023, 12, 31)
    assert sample_task.dependencies == ["project1"]
    assert sample_task.contexts == ["work"]
    assert sample_task.tags == {"tag": "tag1"}
    assert sample_task.description == "Sample task"


def test_task_validation():
    with pytest.raises(ValueError):
        Task(priority=26)
    with pytest.raises(ValueError):
        Task(priority=-1)


@pytest.mark.parametrize(
    "task_string, expected_priority, expected_completed, expected_description", [
        ("(A) Priority task", 0, False, "Priority task"),
        ("x Completed task", None, True, "Completed task"),
        ("2023-01-01 Task with date", None, False, "Task with date"),
        ("+project @context Task with project and context", None, False,
         "Task with project and context"),
        ("Task with due:2023-12-31 tag", None, False, "Task with tag"),
    ])
def test_task_from_string(task_string, expected_priority, expected_completed,
                          expected_description):
    task = Task().from_string(task_string)
    assert task.priority == expected_priority
    assert task.completed == expected_completed
    assert task.description == expected_description


def test_task_to_string(sample_task):
    expected_output = ("2023-01-01 (B) Sample task due:2023-12-31 +project1 "
                       "@work tag:tag1")
    assert sample_task.to_string() == expected_output


def test_task_mark_as_completed(sample_task):
    sample_task.mark_as_completed()
    assert sample_task.completed
    assert sample_task.due_date is not None


def test_task_is_full_task(sample_task):
    assert sample_task.is_full_task()
    minimal_task = Task(description="Minimal task")
    assert not minimal_task.is_full_task()


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


def test_task_to_dict(sample_task):
    task_dict = sample_task.to_dict()
    assert task_dict["priority"] == 1
    assert task_dict["description"] == "Sample task"
    assert task_dict["due_date"] == "2023-12-31"
    assert task_dict["completed"] is False
    assert task_dict["dependencies"] == ["project1"]
    assert task_dict["contexts"] == ["work"]
    assert task_dict["tags"] == {"tag": "tag1"}

if __name__ == "__main__":
    pytest.main()
