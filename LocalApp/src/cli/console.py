from typing import Callable, List, Union
import logging

class Command:
    def __init__(self):
        pass

    command_name: str
    command_description: str
    command_args_list: List[str]
    command_func: Callable

class Console:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.commands = {"Uncategorized": []}

    def print(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def add_command(self, command: Command, category: Union[str, None] = None):
        if category is None:
            category = "Uncategorized"
        if (category not in self.commands.keys()):
            self.logger.info(f"Adding command '{category}' to command list")
            self.commands[category] = []
        if (command not in self.commands[category]):
            self.commands[category].append(command)
            self.logger.info(f"Registered command '{command.command_name}' under category '{category}'")
        else:
            self.logger.error("Command already exists")

    def create_command(self, name: str, description: str, command_args_list: List[str], func: Callable, category: Union[str, None] = None):
        command = Command()
        command.command_name = name
        command.command_description = description
        command.command_args_list = command_args_list
        command.command_func = func
        self.add_command(command, category)

    def run(self):
        exit = False

        print(">>> Welcome to the Nyapix API CLI!")
        print(">>> Type 'help' for more information")
        print(">>> Type 'exit' to exit the console\n\n")

        while not exit:
            cmd = input("> ")
            cmd = cmd.strip()
            cmd = cmd.split(" ")

            cmd_tmp = []
            for i in cmd:
                if i != "":
                    cmd_tmp.append(i)
            cmd = cmd_tmp

            if len(cmd) == 0:
                continue
            has_run = False
            for category in self.commands:
                for i in self.commands[category]:
                    if i.command_name == cmd[0]:
                        try:
                            i.command_func(cmd[1:])
                        except Exception as e:
                            self.logger.error(f"Error occurred while executing command '{i.command_name}': {e}")
                        has_run = True
                        break
            if not has_run and cmd[0] != "help" and cmd[0] != "exit":
                self.logger.error(f"Command '{cmd[0]}' not recognized")

            if cmd[0] == "exit":
                break

            if cmd[0] == "help":
                print("Available commands:")
                for category in self.commands:
                    print(f"\n{category}:")
                    for i in self.commands[category]:
                        args_str = ""
                        if len(i.command_args_list) > 0:
                            args_str = " ".join([f"<{arg}>" for arg in i.command_args_list])
                        print(f"  {i.command_name} {args_str}: {i.command_description}" if args_str != "" else f"  {i.command_name}: {i.command_description}")