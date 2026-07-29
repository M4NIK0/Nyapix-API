from typing import Callable, List
import logging

class Command:
    def __init__(self):
        pass

    command_name: str
    command_description: str
    command_func: Callable

class Console:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.commands = []

    def print(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def add_command(self, command: Command):
        if (command not in self.commands):
            self.commands.append(command)
        else:
            self.logger.error("Command already exists")

    def create_command(self, name: str, description: str, func: Callable):
        command = Command()
        command.command_name = name
        command.command_description = description
        command.command_func = func
        self.add_command(command)

    def run(self):
        exit = False

        while not exit:
            cmd = input("> ")
            cmd = cmd.strip()
            cmd = cmd.split(" ")

            cmd_tmp = []
            for i in cmd:
                if i != "":
                    cmd_tmp.append(i)
            cmd = cmd_tmp

            has_run = False
            for i in self.commands:
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
                for i in self.commands:
                    print(f"{i.command_name}: {i.command_description}")