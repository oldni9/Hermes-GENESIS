from hermes.ai.tool import Tool, ToolParameter, ParameterType
from hermes.filesystem import Filesystem

class FileTools:
    def __init__(self, filesystem: Filesystem) -> None:
        self.fs = filesystem
        self.tools = [
            Tool(name="read_file", description="Read file from workspace.", parameters=[ToolParameter(name="path", type=ParameterType.STRING, description="Relative path", required=True)], function=self.read_file),
            Tool(name="write_file", description="Write file to workspace.", parameters=[ToolParameter(name="path", type=ParameterType.STRING, description="Relative path", required=True), ToolParameter(name="content", type=ParameterType.STRING, description="Content", required=True)], function=self.write_file)
        ]
    def read_file(self, path: str) -> str: return self.fs.read(path)
    def write_file(self, path: str, content: str) -> str:
        self.fs.write(path, content)
        return f"Successfully wrote to {path}"