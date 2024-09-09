# todo-cli - A command-line interface tool for managing tasks using the Todo.txt format

## SYNOPSIS

```sh
python todo_cli/cli.py [COMMAND] [OPTIONS]
```

## DESCRIPTION

Todo-cli is a powerful task management tool that allows you to organize, track, and manage your to-do list directly from the terminal. It follows the Todo.txt format for maximum compatibility and portability.

## COMMANDS

| Command | Description |
|---------|-------------|
| `add`, `a`, `addm` | Add a new task or multiple tasks |
| `do` | Mark a task or multiple tasks as completed |
| `rm`, `r`, `del`, `delete` | Remove a task or multiple tasks |
| `ls`, `list` | List tasks |
| `archive` | Archive completed tasks |
| `update` | Update an existing task |
| `merge` | Merge tasks from another file |
| `sort` | Sort tasks based on priority, due date, or other criteria |
| `get_priority_task` | Retrieve the task with the highest priority |
| `deduplicate` | Remove duplicate tasks from the list |
| `tag` | Add, remove, or list tags for tasks |
| `project` | Add, remove, or list projects for tasks |
| `context` | Add, remove, or list contexts for tasks |
| `search` | Search for tasks based on various criteria |
| `stats` | Display statistics about your tasks |

## GLOBAL OPTIONS

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message and exit |
| `-V`, `--version` | Show version and exit |
| `-v`, `--verbose` | Increase verbosity of output |
| `-f`, `--file FILE` | Specify the path to the todo.txt file |
| `--archive-file FILE` | Specify the path to the archive.txt file |
| `-c`, `--no-color` | Disable colored output |
| `--todotxt` | Use Todo.txt format (default) |
| `-j`, `--json` | Use JSON format for input/output |

## FILES

| File | Description |
|------|-------------|
| `todo.txt` | The main file containing the task list |
| `done.txt` | The file containing completed tasks |
| `archive.txt` | The file containing archived tasks |

## ENVIRONMENT

| Variable | Description |
|----------|-------------|
| `TODO_FILE` | Path to the todo.txt file (overrides the default) |
| `TODO_DONE_FILE` | Path to the done.txt file (overrides the default) |
| `TODO_ARCHIVE_FILE` | Path to the archive.txt file (overrides the default) |

## SEE ALSO

[Todo.txt Format Specification](https://github.com/todotxt/todo.txt)

## BUGS

Report bugs to: <https://github.com/ci-c/todo-cli/issues>

## AUTHOR

Written by ci-c

## COPYRIGHT

Copyright © 2024 ci-c. License MIT: <https://opensource.org/licenses/MIT>
