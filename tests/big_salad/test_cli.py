from click.testing import CliRunner

from big_salad.cli import cli


def test_cli():
    cli_runner = CliRunner()
    result = cli_runner.invoke(cli)
    assert result.exit_code == 0
