# [WiP] Todo.txt CLI Manager

Todo.txt CLI Manager is a command-line interface tool for managing your tasks using the Todo.txt format. This simple and efficient tool helps you organize your to-do list directly from the terminal. However, it's important to note that the Todo.txt format does not provide backward compatibility, so users may need to adjust their existing todo.txt files to work with this tool.

## Features

- Add new tasks
- List all tasks
- Mark tasks as complete
- Remove tasks
- Filter tasks by project or context
- Sort tasks by priority or due date

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/ci-c/todo-cli.git
   cd todo-cli
   ```

2. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

To use the Todo.txt CLI Manager, run the following command:

```sh
python src/cli.py [COMMAND] [OPTIONS]
```

Available commands:

- `add`: Add a new task
- `do`: Mark a task as completed
- `rm`: Remove a task
- `ls`: List tasks
- `archive`: Archive completed tasks
- `update`: Update a task

For detailed information on each command and its options, use the `--help` flag:

```sh
python src/cli.py [COMMAND] --help
```

## Examples

1. Add a new task:

   ```sh
   python src/cli.py add "Buy groceries" -p A -d 2023-05-01 -t shopping:food -j personal -c errands
   ```

2. List all tasks:

   ```sh
   python src/cli.py ls
   ```

3. Mark a task as completed:

   ```sh
   python src/cli.py do 1
   ```

4. Update a task:

   ```sh
   python src/cli.py update 2 -p B -d 2023-05-15 --description "Finish project report"
   ```

5. Archive completed tasks:

   ```sh
   python src/cli.py archive
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License
