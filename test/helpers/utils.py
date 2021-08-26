import json
from pathlib import Path
from typing import Any, List, Mapping, Text, Union


def list_examples(path: Union[Path, Text], name: Text) -> List[Path]:
    """Lists the example JSON folders in the directory `path` that start
    with the name `name`

    Args:
        path (Union[Path, Text]): Path to a directory with JSON examples
        name (Text): The prefix of the example files

    Returns:
        List[Path]: The example JSON files
    """
    if not isinstance(path, Path):
        path = Path(path)

    return [_file for _file in path.iterdir() if _file.match(f"{name}*.json")]


def load_example(path: Path) -> Mapping[Text, Any]:
    """Load a JSON example from `path`

    Args:
        path (Path): Path to a a JSON example file

    Returns:
        Mapping[Text, Any]: The loaded JSON file
    """
    with open(path) as f_in:
        loaded_example = json.load(f_in)

        # do this so that mypy knows we loaded a dict (since the JSON
        # format is flexible enough to be just a string or int, etc)
        if not isinstance(loaded_example, dict):
            raise ValueError(
                "Expected JSON example to be of type dict"
            )

        return loaded_example
