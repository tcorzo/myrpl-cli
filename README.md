# myrpl-cli

<p align="center">
    <a href="https://github.com/tcorzo/myrpl-cli/actions/workflows/python-ci.yml">
        <img src="https://img.shields.io/github/actions/workflow/status/tcorzo/myrpl-cli/ci.yml?branch=main" alt="Build Status"/>
    </a>
    <a href="https://github.com/tcorzo/myrpl-cli/blob/main/LICENSE" >
        <img src="https://img.shields.io/github/license/tcorzo/myrpl-cli" alt="License"/>
    </a>
</p>

myrpl-cli is a command-line interface tool for fetching and saving course activities from [myrpl.ar](https://myrpl.ar/).

## What does it do?

- 🪨 Tired of copying and pasting your code between your IDE and RPL like a caveman?

    > Well I've got the answer for you! Fetch your activities with `myrpl fetch`, solve them and upload them **once** with `myrpl submit` when you're done

- ⌛ Exhausted of waiting **whole** seconds for running tests that should take **milli**seconds?

    > Well I've got the answer for you! Run your tests **locally** with `myrpl test`

- 💦 Got a thing for slick CLI tools?

    > While `myrpl` can't help you with your fantasies, it can certainly make your workflow smoother and more enjoyable. 😏

## 🛠️ Installation

Install the package globally using [pipx](https://github.com/pypa/pipx):

```bash
pipx install myrpl-cli
```

Now you can use the myrpl command! 🎉

## 📚 Usage

To use myrpl-cli, you need a bearer token for authentication. You can provide this token either as an environment variable (even within a .env file) or as a command-line argument.

### 1. 🔑 Logging In

Before fetching course activities, you need
to log in and store your credentials
securely. Use the login command:

```bash
myrpl login
```

This will prompt you for your username/email and password and store your credentials securely in an encrypted file. You'll also be asked for a passphrase to encrypt said file.🔒 NOTE: Each time you use `myrpl` you'll be prompted for the passphrase.

You can always overwrite the stored credentials by running the `login` command again

### 2. 🎓 Fetching course activities

First, `cd` into the directory where you want your courses and activities stored

To fetch activities for a specific course:

```bash
myrpl fetch <course_id>
```

This will create a file structure in the current working directory like follows:

```bash
./
├── courses/
├── {course 1}/
├── {category 1}/
│   ├── description.txt
│   ├── {activity 1}/
│   │   ├── description.md
│   │   ├── unit_test.py
│   │   └── main.py
│   ├── {activity 2}/
┊   ┊
```

### 3. 🧑‍💻 Getting some actual work done

- `cd` into any activity
- Launch your IDE of choice. eg.: `code .` for VS Code
- You can see the activity's description, initial code and unit tests
- Write your code and run the tests using `myrpl test` or just `pytest`

### 🛡️ (Optional) Setting up the bearer token

Option 1: Set an environment variable

```bash
export MYRPL_BEARER_TOKEN=your_bearer_token_here
```

Option 2: Provide the token as a command-line argument (see examples below)

### ❓ Getting help

For general help:

```bash
myrpl --help
```

For help with the a specific command:

```bash
myrpl <command> --help
```

## 🏗️ Project Structure

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

## 👩‍💻👨‍💻 Development

To set up the development environment:

1. Activate an env

```bash
poetry env use python
```

1. Install all dependencies

```bash
poetry install
```

1. And pre-commit hooks:

```bash
pre-commit install
```

1. Activate the virtual environment:

```bash
poetry shell
```

1. Off you go! 🚀

### 🧪 Tests

Use `pytest` to run the project's tests

Use [act](https://github.com/nektos/act) for running the github workflow locally

### 📝✅ Linting & Formatting

I chose [ruff](https://github.com/astral-sh/ruff/) for linting + formatting

> PD: I use the [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) VS Code extension, but you do you

## 🗺️ Roadmap

- \[x\]
- \[x\]
- \[x\]
- \[x\]
- \[

    \]
- \[

    \]
- \[

    \]
- \[

    \]
- \[

    \]
- \[

    \]
- \[

    \]
- \[

    \]

Please note that this roadmap is subject to change and may be updated based on user feedback and my own time 😁

## How does myrpl-cli fetch hidden files and decompiles them? (incoming feature)

I ran into a problem where I couldn't run a unit_test because the "grafo" library
was missing.

So, what could I do?

I started trying to get the content of the grafo library, obviously

I ended up with this code snippet, which I ran on [myrpl.ar](https://myrpl.ar):

```python
import grafo
import base64


def vertex_cover_min(_):
	print("#startgrafocontent")
	with open(grafo.__file__, "rb") as gf:
		content = gf.read()
		encoded_content = base64.b64encode(content).decode("utf-8")
		print(encoded_content)
	print("#endgrafocontent")

	return []
```

> In the future this can be easily automated with the submission API

This ends up spitting into the submission's stdout the base64 encoded contents
of the `grafo.pyc` file.

From there I could easily import the `Grafo` class into python. **But**, .pyc files are
python version specific, so I could only run them inside Python 3.10.0. *Boooringg*

So, time to decompile 😈

I finally found [pycdc](https://github.com/zrax/pycdc), which unfortunately has to be `make` compiled (that'll make things harder when integrating with `myrpl-cli` later on)

pycdc then spat the following to stdout:

```python
# Source Generated with Decompyle++
# File: grafo.pyc (Python 3.10)


class Grafo:
	def __init__(self, es_dirigido, vertices_init=(False, [])):
		self.vertices = {}
		for v in vertices_init:
			self.vertices[v] = {}
		self.es_dirigido = es_dirigido

	def __contains__(self, v):
		return v in self.vertices


# and so on...
```

So, now comes the time to **integrate** this into `myrpl-cli`, which poses a challenge in itself.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Where does the name come from?

It's actually 'My RPL' backwards. No, wait...

## 👥 Authors

- tcorzo 🧑🏾‍🦲
