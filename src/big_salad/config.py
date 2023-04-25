"""
This module has some configuration functions etc to support running locally or in docker
"""
from os import getenv
from pathlib import Path

IN_DOCKER = getenv("IN_DOCKER", "false").lower() in ("true", "1")
DOCKER_CONTEXT_PATH = Path("/opt/context")
DOCKER_USER_HOME_PATH = Path("/opt/usr/home")
DOCKER_BS_DIR = Path("/opt/big_salad")
LOCAL_BS_DIR = Path("~/.local/share/big-salad")


def _mutate_path(path: Path, docker_path: Path) -> Path:
    """
    Mutates the given file path to be relative to a specified Docker path, if running inside a Docker container.

    Parameters:
    path (Path): The original file path.
    docker_path (Path): The base path inside the Docker container.

    Returns:
    Path: The mutated path if running inside Docker; otherwise, returns the original path.
    """
    if not IN_DOCKER:
        return path
    return Path(docker_path, path)


def context_mutate(path: Path) -> Path:
    """
    Mutates the given path within the context of a Docker build.

    This function modifies the input path in conjunction with the Docker context path.

    Parameters:
    path (Path): The original file or directory path to be mutated.

    Returns:
    Path: The mutated path.
    """
    return _mutate_path(path, DOCKER_CONTEXT_PATH)


def mutant_home(path: Path) -> Path:
    """
    Returns the appropriate path based on the environment.

    In a standard environment, it returns the given path as-is.
    If running inside a Docker container, it adjusts and returns the path
    relative to the Docker user's home directory.

    Parameters:
    path (Path): The input path to be processed.

    Returns:
    Path: The processed path, relative to the environment.
    """
    if not IN_DOCKER:
        return path
    return Path(DOCKER_USER_HOME_PATH, path)


def mutant_bs_dir(path: Path) -> Path:
    """
    Resolves the correct directory path for a given path based on whether the application is running inside a Docker container.

    Parameters:
    path (Path): The original file or directory path.

    Returns:
    Path: The resolved directory path. If the application is running inside a Docker container, it prepends the Docker base directory; otherwise, it returns the original path unchanged.
    """
    if not IN_DOCKER:
        return path
    return Path(DOCKER_BS_DIR, path)


LOCAL_BIN = _mutate_path(Path(".local/bin"), DOCKER_USER_HOME_PATH)
CONTEXT_PATH = _mutate_path(Path("."), DOCKER_CONTEXT_PATH)
BS_DIR = DOCKER_BS_DIR if IN_DOCKER else LOCAL_BS_DIR
