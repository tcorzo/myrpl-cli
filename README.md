# MyRPL CLI

<p align="center">
    <a href="https://github.com/tcorzo/myrpl-cli/actions/workflows/python-ci.yml" alt="Build Status">
        <img src="https://img.shields.io/github/actions/workflow/status/tcorzo/myrpl-cli/python-ci.yml?branch=main" />
    </a>
    <a href="https://github.com/tcorzo/myrpl-cli/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/tcorzo/myrpl-cli" />
    </a>
</p>

MyRPL CLI is a command-line interface tool for fetching and saving course activities from `myrpl.ar`.

## What does it do?

-   🪨 Tired of copying and pasting your code between your IDE and RPL like a caveman?

    > Well I've got the answer for you! Fetch your activities with `myrpl fetch`, solve them and upload them **once** with `myrpl submit` when you're done

-   ⌛ Exhausted of waiting **whole** seconds for running tests that should take **milli**seconds?

    > Well I've got the answer for you! Run your tests **locally** with `myrpl test`

-   💦 Got a thing for slick CLI tools?

    > While `myrpl` can't help you with your fantasies, it can certainly make your workflow smoother and more enjoyable. 😏

## Installation 🛠️

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
pip install dist/myrpl_cli-0.2.0-py3-none-any.whl
```

Now you can use the myrpl command! 🎉

## Usage 📚

To use MyRPL CLI, you need a bearer token for authentication. You can provide this token either as an environment variable (even within a .env file) or as a command-line argument.

### Logging In 🔑

Before fetching course activities, you need to log in and store your credentials securely. Use the login command:

```bash
myrpl login
```

This will prompt you for your username/email and password and store your credentials securely in an encrypted file. You'll also be asked for a passphrase to encrypt said file.🔒 NOTE: Each time you use `myrpl` you'll be prompted for the passphrase.

You can always overwrite the stored credentials by running the `login` command again

### (Optional) Setting up the bearer token 🛡️

Option 1: Set an environment variable

```bash
export MYRPL_BEARER_TOKEN=your_bearer_token_here
```

Option 2: Provide the token as a command-line argument (see examples below)

### Fetching course activities 🎓

First, `cd` into the directory where you want your courses and activities stored

To fetch activities for a specific course:

```bash
myrpl fetch <course_id>
```

This will create a file structure in the current working directory like follows:

```bash
./
└── courses/
    └── {course 1}/
        ├── {category 1}/
        │   ├── description.txt
        │   ├── {activity 1}/
        │   │   ├── description.md
        │   │   ├── unit_test.py
        │   │   └── main.py
        │   ├── {activity 2}/
        ┊   ┊
```

### Getting some actual work done 🧑‍💻

-   `cd` into any activity
-   Launch your IDE of choice. eg.: `code .` for VS Code
-   You can see the activity's description, initial code and unit tests
-   Write your code and run the tests using `pytest`

### Getting help ❓

For general help:

```bash
myrpl --help
```

For help with the a specific command:

```bash
myrpl {command} --help
```

## Project Structure 🏗️

```bash
myrpl-cli/
├── pyproject.toml
├── README.md
└── myrpl_cli/
    ├── __init__.py
    ├── api.py
    ├── credential_manager.py
    ├── main.py
    └── myrpl.py
```

## Development 👩‍💻👨‍💻

To set up the development environment:

1. Install all dependencies

```bash
poetry install
```

2. Activate the virtual environment:

```bash
poetry shell
```

3. Off you go! 🚀

### Tests 🧪

Use `pytest` to run the project tests

Use [act](https://github.com/nektos/act) for running the github workflow locally

### Linting 📝✅

I chose [flake8](https://pypi.org/project/flake8/) for linting

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📜

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors 👥

-   tcorzo 🧑🏾‍🦲
