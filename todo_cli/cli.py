#!/usr/bin/env python3

"""
This function initializes the CLI application, sets up the context, and
handles global options.
"""

# TODO: вынести логику

import json
import os
import pathlib
from datetime import datetime
from typing import List, Optional
from dateutil import parser as dtparser

import click
from todo_cli.task import Task
from todo_cli.tasklist import TaskList

DEFAULT_PATH: pathlib.Path = pathlib.Path().cwd() / 'todo.txt'
DEFAULT_PATH_ARCHIVE: pathlib.Path = pathlib.Path().cwd() / 'todo.archive.txt'


@click.group()
@click.option('-h', '--help', is_flag=True, help='Show this message and exit.')
@click.option('-V', '--version', is_flag=True, help='Show version and exit.')
@click.option('-v', '--vebrose', is_flag=True, help='Be more vebrose.')
@click.option('-f', '--file', 'help_show', type=click.Path(),
              envvar='TODOTXT_PATH', default=DEFAULT_PATH,
              help='Path to the todo.txt file')
@click.option('--archive-file', type=click.Path(), envvar='ARCHIVE_PATH',
              default=DEFAULT_PATH_ARCHIVE,
              help='Path to the archive.txt file')
@click.option('-c', '--no-color', is_flag=True,
              help='Disable colors in output')
@click.option('--todotxt', is_flag=True)
@click.option('-j', '--json', 'json_f', is_flag=True)
@click.pass_context
def cli(ctx: click.Context, help_show: bool, file: pathlib.Path,
        archive_file, no_color: bool, todotxt: bool, json_f: bool,
        version: bool, vebrose: bool) -> None:
    """Todo.txt CLI manager

    This function initializes the CLI application, sets up the context, and
    handles global options.
    """
    if help_show:
        click.echo(ctx.get_help())
        ctx.exit()
    if version:
        click.echo("Todo.txt CLI version 0.1.0")
        ctx.exit()
    ctx.ensure_object(dict)
    todo_file = file
    ctx.obj['tasklist'] = TaskList()
    if os.path.exists(todo_file):
        with open(todo_file, 'r', encoding='utf-8') as f:
            todo_content = f.read()
            ctx.obj['tasklist'].from_string(todo_content)
    ctx.obj['todo_file'] = todo_file
    ctx.obj['archive_file'] = archive_file
    ctx.obj['color'] = not no_color
    ctx.obj['todotxt'] = todotxt
    ctx.obj['json'] = json_f
    ctx.obj['vebrose'] = vebrose


@cli.command(name='add')
@click.argument('task_string')
@click.pass_context
def add(ctx: click.Context, task_string: str):

    """
    Add a new task

    This function adds a new task to the task list.

    Args:
        ctx (click.Context): The Click context object.
        task_string (str): The task description to be added.
    """
    if ctx.obj["help"]:
        click.echo(ctx.get_help())
        ctx.exit()
    output = []
    for task_desc in task_string.splitlines():
        task = Task(creation_date=datetime.now())
        task.from_string(task_desc)
        ctx.obj['tasklist'].add_task(task)
        if ctx.obj['vebrose']:
            if ctx.obj['todotxt']:
                output.append(f"Task added: {task.to_string()}")
            elif ctx.obj['json']:
                output.append(task.to_dict())
            else:
                output.append(task)
    if ctx.obj['vebrose'] and ctx.obj['json']:
        output = json.dumps(output)
    save_tasklist(ctx=ctx, tasklist=None)
    click.echo(output)


cli.add_command(add, name='a')
cli.add_command(add, name='addm')


@cli.command()
@click.argument('indexes', type=int, nargs=-1)
@click.option('-h', '--help', is_flag=True, help='Show this message and exit.')
@click.pass_context
def do(ctx: click.Context, indexes: list[int], show_help):
    """
    Mark a task as completed

    This function marks one or more tasks as completed based on their indexes.

    Args:
        ctx (click.Context): The Click context object.
        indexes (list[int]): List of task indexes to mark as completed.
        show_help (bool): Flag to show help message.
    """
    if show_help:
        click.echo(ctx.get_help())
        ctx.exit()
    if not indexes:
        if ctx.obj['vebrose']:
            click.echo("No task index provided.")
        ctx.exit()
    tasklist: TaskList = ctx.obj['tasklist']
    for index in indexes:
        task: Optional[Task] = tasklist.get(index=index, default=None)
        if task:
            task.mark_as_completed()
        if ctx.obj['vebrose']:
            if not task:
                click.echo("Task not found.")
            elif task.tags.get('rec', None):
                click.echo(
                    f"Task's due date has been changed. New task: {task}"
                    )
            else:
                click.echo(f"Task marked as completed: {task}")
        save_tasklist(ctx=ctx, tasklist=None)


@cli.command()
@click.argument('indexes', type=int, nargs=-1)
@click.option('-h', '--help', is_flag=True, help='Show this message and exit.')
@click.pass_context
def rm(ctx: click.Context, indexes: list[int], show_help):
    """
    Remove a task

    This function removes a task from the task list based on its index.

    Args:
        ctx (click.Context): The Click context object.
        indexes (list[int]): List of task indexes to remove.
        show_help (bool): Flag to show help message.
    """
    if show_help:
        click.echo(ctx.get_help())
        ctx.exit()

    if not indexes:
        if ctx.obj['vebrose']:
            click.echo("No task index provided.")
        ctx.exit()

    tasklist: TaskList = ctx.obj['tasklist']
    remove_tasks: List[Task] = []
    not_found_indexes: List[int] = []

    for index in indexes:
        if task := tasklist.get(index=index):
            remove_tasks.append(task)
        else:
            not_found_indexes.append(str(index))
    for task in remove_tasks:
        tasklist.remove_task(task)
    if ctx.obj['vebrose']:
        if not_found_indexes:
            click.echo(f"Task(s) not found: {', '.join(not_found_indexes)}")
        if remove_tasks:
            click.echo(f"Task(s) removed:\n\t{'\n\t'.join(remove_tasks)}")
    save_tasklist(ctx=ctx, tasklist=None)


cli.add_command(rm, name='r')
cli.add_command(rm, name='del')
cli.add_command(rm, name='delete')


@cli.command()
@click.option('-s', '--sort', 'sorting', is_flag=True, help="Sort tasks")
@click.option('-h', '--help', name='show_help',
              is_flag=True, help='Show this message and exit.')
@click.argument('filter_a', type=Optional[str])
@click.pass_context
def ls(ctx: click.Context, filter_a: str,
       sorting: bool, show_help: bool) -> None:
    """List tasks

    This function lists all tasks in the task list, optionally sorting them.

    Args:
        ctx (click.Context): The Click context object.
        sort (bool): Flag to sort tasks.
        show_help (bool): Flag to show help message.
    """
    if show_help:
        click.echo(ctx.get_help())
        ctx.exit()
    task_list: TaskList = ctx.obj['tasklist']
    if sorting:
        task_list.sort()
    if filter_a:
        task_list.filter(lambda x: filter_a in x.to_string())
    if ctx.obj['json']:
        out = [task.to_dict() for task in task_list]
        click.echo(json.dumps(out, ensure_ascii=False))
    else:
        click.echo(task_list.to_string(color=not ctx.obj['no_color'],
                                       todotxt_format=ctx.obj['todotxt']))


cli.add_command(ls, "list")


@cli.command()
@click.option('-h', '--help', is_flag=True, help='Show this message and exit.')
@click.pass_context
def archive(ctx, show_help):
    """
    Archive completed tasks

    This function archives all completed tasks in the task list.

    Args:
        ctx (click.Context): The Click context object.
        show_help (bool): Flag to show help message.
    """

    if show_help:
        click.echo(ctx.get_help())
        ctx.exit()
    archived: TaskList = ctx.obj['tasklist'].archive()
    if ctx.obj['vebrose']:
        click.echo(f"Archived {len(archived)} completed tasks")


@cli.command()
@click.argument('index')
@click.option('-p', '--priority',
              type=click.Choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
              help='Update priority (A-Z)'
              )
@click.option('-d', '--due', type=click.DateTime(formats=["%Y-%m-%d"]),
              help='Update due date (YYYY-MM-DD)') # FIXME: type check is incorrect
@click.option('-t', '--tag', multiple=True, help='Update tags (key:value)')
@click.option('-d', '--dep', multiple=True, help='Update projects')  # FIXME: rename to dependedies
@click.option('-c', '--context', multiple=True, help='Update contexts')
@click.option('--description', help='Update description')
@click.option('-h', '--help', 'show_help', is_flag=True,
              help='Show this message and exit.'
              )
@click.pass_context
def update(ctx, task_description, priority, due, tag, project, context,
           description, show_help):   # TODO: is not working...
    """Update a task"""

    if show_help:
        click.echo(ctx.get_help())
        ctx.exit()
    if task := next(
        (
            t
            for t in ctx.obj['tasklist'].to_list()
            if t.description == task_description
        ),
        None,
    ):
        if priority:
            task.set_priority(ord(priority) - 65)
        if due:
            task.set_completion_date(due)
        if tag:
            task.tags.clear()
            for t in tag:
                key, value = t.split(':', 1)
                task.add_tag(key, value)
        if project:
            task.projects = list(project)
        if context:
            task.contexts = list(context)
        if description:
            task.set_description(description)
        click.echo(f"Task updated: {task}")
    else:
        click.echo("Task not found.")


@cli.command()
@click.argument('other_file', type=click.Path(exists=True))
@click.pass_context
def merge(ctx: click.Context, other_file: pathlib.Path):
    """
    Merge tasks from another file

    This function merges tasks from another file into the current task list.
    """
    with open(other_file, 'r', encoding='utf-8') as f:
        other_content = f.read()
    other_tasklist: TaskList = TaskList().from_string(other_content)
    conflicts = ctx.obj['tasklist'].merge(other_tasklist)
    if ctx.obj['vebrose']:
        if ctx.obj['json']:
            click.echo(json.dumps(conflicts, ensure_ascii=False))
        elif conflicts:
            click.echo(f"Conflicts found: {conflicts}")
        else:
            click.echo("No conflicts found.")
        if not ctx.obj['json']:
            click.echo(f"Merged tasks from {other_file}")
            click.echo(ctx.obj['tasklist'])

    save_tasklist(ctx)


@cli.command()
@click.option('-r', '--reverse', is_flag=True, help='Reverse the sort order')
@click.pass_context
def sort(ctx: click.Context, reverse: bool):
    """
    Sort tasks

    This function sorts the tasks in the task list.
    """
    ctx.obj['tasklist'].sort(reverse=reverse)


@cli.command()
@click.pass_context
def get_priority(ctx: click.Context):
    """
    Get the task with the highest priority

    This function retrieves and displays the task with the highest priority.
    """
    sorted_tasklist = ctx.obj['tasklist']
    sorted_tasklist.sort(reverse=False)
    click.echo(
        f"Task with the highest priority: {sorted_tasklist[0].to_string()}"
        )


@cli.command()
@click.pass_context
@click.option(
    '-t', '--time',
    type=str, help='Datetime or date in ISO format', required=False)
def get_now(ctx: click.Context, time: Optional[str]):
    """
    Get the event planned for the current time.
    """
    tasklist: TaskList = ctx.obj['tasklist']
    if time:
        time = (dtparser.isoparse(time) if 'T' in time
                else dtparser.parse(time).date())
    now_task: Optional[Task] = tasklist.get_now()
    if ctx.obj['json']:
        click.echo(json.dumps(now_task))
    elif now_task is None:
        click.echo('Nothing is planned for now.')
    else:
        click.echo(now_task.to_string(
            color=ctx.obj['color'],
            todotxt_format=ctx.obj['todotxt']
        ))


@cli.command()
@click.pass_context
def deduplicate(ctx: click.Context):
    """
    Deduplicate tasks

    This function removes duplicate tasks from the task list.
    """
    tasklist: TaskList = ctx.obj['tasklist']
    initial_count: int = len(tasklist)
    tasklist.deduplicate()
    removed_count = initial_count - len(tasklist)
    if ctx.obj['vebrose']:
        click.echo(f"Deduplicated {removed_count} tasks")
    save_tasklist(ctx)


def save_tasklist(ctx: click.Context,
                  tasklist: Optional[TaskList] = None
                  ) -> None:
    """
    Save the task list to a file

    This function saves the current task list to a file.
    If the task list is not provided, it uses the task list from the context.
    The task list is saved to the file specified in the context.
    If task list is provided use 'archive todo file', else 'todo file'

    Args:
        ctx (click.Context): The Click context object.
        tasklist (Optional[TaskList]): Only for archive.
    """
    path = pathlib.Path(ctx.obj['archive_file'])
    mode = 'a'
    if tasklist is None:
        path: pathlib.Path = pathlib.Path(ctx.obj['todo_file'])
        mode: str = 'w'
        tasklist: TaskList = ctx.obj['tasklist']

    with open(path, mode, encoding='utf-8') as f:
        f.write(tasklist.to_string())
