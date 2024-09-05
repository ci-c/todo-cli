# Todo.txt CLI Manager

A command-line interface (CLI) for managing tasks in the Todo.txt format.

## Features

- Add, update, and remove tasks
- Mark tasks as completed
- List tasks with sorting and filtering options
- Archive completed tasks
- Support for priorities, due dates, projects, contexts, and tags

## Installation

1. Clone the repository:

   git clone https://github.com/yourusername/todo-cli.git
   cd todo-cli

2. Install the required dependencies:

   pip install -r requirements.txt

## Usage

Run the CLI with the following command:

python src/cli.py [COMMAND] [OPTIONS]

Available commands:

- `add`: Add a new task
- `do`: Mark a task as completed
- `rm`: Remove a task
- `ls`: List tasks
- `archive`: Archive completed tasks
- `update`: Update a task

For detailed information on each command and its options, use the `--help` flag:

python src/cli.py [COMMAND] --help

## Examples

1. Add a new task:

   python src/cli.py add "Buy groceries" -p A -d 2023-05-01 -t shopping:food -j personal -c errands

2. List all tasks:

   python src/cli.py ls

3. Mark a task as completed:

   python src/cli.py do 1

4. Update a task:

   python src/cli.py update 2 -p B -d 2023-05-15 --description "Finish project report"

5. Archive completed tasks:

   python src/cli.py archive

## File Structure

- `src/cli.py`: Main CLI application
- `src/task.py`: Task class definition
- `src/tasklist.py`: TaskList class for managing multiple tasks
- `src/parser.py`: Parser for Todo.txt format

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License