# MyRPL CLI

MyRPL CLI is a command-line interface tool for fetching and saving course activities from myrpl.ar.

## Installation

This project uses Poetry for dependency management. To install, follow these steps:

1. Ensure you have Poetry installed. If not, install it from [Poetry's official website](https://python-poetry.org/docs/#installation).

2. Clone this repository:

```bash
git clone https://github.com/tcorzo/myrpl-cli.git
cd myrpl-cli
```

3. Build the package:

```bash
poetry build
```

4. Install the package globally:

```bash
pip install dist/myrpl_cli-0.1.0-py3-none-any.whl
```

Now you can use the `myrpl` command!

## Usage

To use MyRPL CLI, you need a bearer token for authentication. You can provide this token either as an environment variable (even within a .env file) or as a command-line argument.

### Setting up the bearer token

Option 1: Set an environment variable
```bash
export MYRPL_BEARER_TOKEN=your_bearer_token_here
```

Option 2: Provide the token as a command-line argument (see examples below)

### Fetching course activities

To fetch activities for a specific course:

```bash
poetry run myrpl fetch <course_id> [--token YOUR_BEARER_TOKEN]
```

Example:

```bash
poetry run myrpl fetch 57
```
Or with explicit token:

```bash
poetry run myrpl fetch 57 --token your_bearer_token_here
```

### Getting help

For general help:
```bash
poetry run myrpl --help
```

For help with the a specific command:

```bash
poetry run myrpl {command} --help
```

## Project Structure

```bash
myrpl-cli/
├── pyproject.toml
├── README.md
└── myrpl_cli/
    ├── __init__.py
    └── main.py
    └── myrpl_api.py
```

## Development

To set up the development environment:

1. Install dependencies including development dependencies:

```bash
poetry install
```

2. Activate the virtual environment:

```bash
poetry shell
```

3. Off you go!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- tcorzo
