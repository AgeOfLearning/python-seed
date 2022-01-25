"""python_seed.scripts.cli."""

import os
import shutil

import click

from .. import __version__

try:
    from importlib.resources import files as resources_files  # type: ignore
except ImportError:
    # Try backported to PY<39 `importlib_resources`.
    from importlib_resources import files as resources_files  # type: ignore


@click.group(short_help="python-seed CLI")
@click.version_option(version=__version__, message="%(version)s")
def pyseed():
    """python-seed subcommands."""
    pass


CI_CHOICES = ["circleci", "github", "gitlab"]

@pyseed.command(short_help="Create new python seed skeleton")
@click.argument("name", type=str, nargs=1)
@click.option(
    "--ci", type=click.Choice(CI_CHOICES), help="Add CI configuration"
)
def create(name, ci):
    """Create new python seed skeleton."""
    template_dir = str(resources_files("python_seed") / "template" / "module")
    shutil.rmtree(f"{name}/{name}", ignore_errors=True)
    shutil.rmtree(f"{name}/docs", ignore_errors=True)
    shutil.copytree(template_dir, name, dirs_exist_ok=True)

    if ci:
        # acommodate gitlab's single file ci config
        if ci == 'gitlab':
            template_file = str(
                resources_files("python_seed") / "template" / "ci" / ".gitlab-ci.yml"
            )
            shutil.copy2(template_file, f"{name}/.gitlab-ci.yml")
        else:
            template_dir = str(
                resources_files("python_seed") / "template" / "ci" / f".{ci}"
            )
            shutil.copytree(template_dir, f"{name}/.{ci}", dirs_exist_ok=True)

        covconfig = str(
            resources_files("python_seed") / "template" / "cov" / "codecov.yml"
        )
        shutil.copy2(covconfig, f"{name}/codecov.yml")

        gitignore = str(resources_files("python_seed") /  "template" / ".gitignore")
        shutil.copy2(gitignore, f"{name}/.gitignore")



    new_dir = name
    name = name.replace("-", "_")
    for root, _, files in os.walk(new_dir):
        if root.endswith("pyseed"):
            shutil.move(root, root.replace("pyseed", name))

    for root, _, files in os.walk(new_dir):
        for filename in files:
            if filename.endswith(".pyc"):
                continue
            if filename.endswith(".pyc"):
                continue
            try:
                with open(f"{root}/{filename}", "r", encoding="utf-8") as f:
                    s = f.read().replace("pyseed", name)

                with open(f"{root}/{filename}", "w", encoding="utf-8") as f:
                    f.write(s)
            except UnicodeDecodeError:
                pass

    if ci == 'gitlab':
        stream = os.popen(f'sphinx-quickstart {name}/docs -p {name} -a aofl-data -v 0.0.1 -l en --no-sep -q --ext-autodoc --ext-doctest')
        print(stream.read())