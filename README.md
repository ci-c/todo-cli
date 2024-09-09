# [WIP] Todo.txt CLI Manager

Todo.txt CLI Manager is a command-line interface tool for managing your tasks using the Todo.txt format. This simple and efficient tool helps you organize your to-do list directly from the terminal.

## Features

- Add new tasks
- List all tasks
- Mark tasks as complete
- Remove tasks
- Update tasks
- Archive completed tasks
- Merge tasks from another file
- Sort tasks
- Get the highest priority task
- Deduplicate tasks

## Installation

Clone the repository:

```sh
git clone https://github.com/ci-c/todo-cli.git
cd todo-cli
```

Install the required dependencies:

```sh
pip install -r requirements.txt
```

## Usage

To use the Todo.txt CLI Manager, run the following command:

```sh
python todo_cli/main.py [COMMAND] [OPTIONS]
```

Available commands:

- `add` (`a`, `addm`): Add a new task(s)
- `do`: Mark a task(s) as completed
- `rm` (`r`, `del`, `delete`): Remove a task(s)
- `ls` (`list`): List tasks
- `archive`: Archive completed tasks
- `update`: Update a task
- `merge`: Merge tasks from another file
- `sort`: Sort tasks
- `get_priority_task`: Get the task with the highest priority
- `deduplicate`: Remove duplicate tasks

For detailed information on each command and its options, use the `--help` flag:

```sh
python todo_cli/main.py [COMMAND] --help
```

### Global Options

- `-h`, `--help`: Show help message and exit
- `-V`, `--version`: Show version and exit
- `-v`, `--verbose`: Be more verbose
- `-f`, `--file`: Path to the todo.txt file
- `--archive-file`: Path to the archive.txt file
- `-c`, `--no-color`: Disable colors in output
- `--todotxt`: Use Todo.txt format
- `-j`, `--json`: Use JSON format

### Available todo.txt format options

Basic todo.txt format:

- Description
- Priority (`(A)`, `(B)`, `(C)`, etc.)
- Done flag (`[x]`)
- Projects (`+example`) (using for dependencies)
- Contexts (`@example`)
- Tags (`example:abc`)
- Creation date or date and time in ISO format (`2023-05-01T12:00`)

Tags:

- `pri` alternative priority (`A`, `B`, `C`, etc.)
- `rec:` repeating task (`1d`, `+4y`, `1m1d`)
- `id:` task id
- `due:` due date or date and time in ISO format (`2023-05-01`)
- `dur:` duration (WIP)
- `cost:` (WIP)
- `deadline:` deadline date or date and time in ISO format (`2023-05-01T12:00`) (WIP)
- `edit:` last edit date and time in ISO format (`2023-05-01T12:00`) (WIP)
- `redue:` counter of overdueing (WIP)

Other features:

- comments - start line with `#`

## Examples

Add a new task:

```sh
python todo_cli/main.py add "Buy groceries -p A -d 2023-05-01 -t shopping:food -j personal -c errands"
# not supported
```

List all tasks:

```sh
python todo_cli/main.py ls
```

Mark a task as completed:

```sh
python todo_cli/main.py do 1
```

Update a task:

```sh
python todo_cli/main.py update 2 -p B -d 2023-05-15 --description "Finish project report"
```

Archive completed tasks:

```sh
python todo_cli/main.py archive
```

Merge tasks from another file:

```sh
python todo_cli/main.py merge other_todo.txt
```

Sort tasks:

```sh
python todo_cli/main.py sort
```

Get the highest priority task:

```sh
python todo_cli/main.py get_priority_task
```

Deduplicate tasks:

```sh
python todo_cli/main.py deduplicate
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
