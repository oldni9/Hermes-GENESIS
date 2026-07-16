from hermes.commands.base import BaseCommandHandler
from hermes.commands.command import Command
from hermes.commands.executor import CommandExecutor
from hermes.commands.registry import CommandRegistry
from hermes.commands.result import CommandResult


class Demo(BaseCommandHandler):

    @property
    def name(self):
        return "demo"

    def execute(self, command):
        return CommandResult(
            success=True,
            message=f"Executed {command.text}",
        )


registry = CommandRegistry()

registry.register(
    "demo",
    Demo(),
)

command = Command(
    text="Hello",
    subsystem="demo",
)

result = CommandExecutor(
    registry,
).execute(
    command,
)

print(result)