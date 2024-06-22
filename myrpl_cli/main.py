# main.py

import argparse
from dotenv import load_dotenv

from myrpl_cli.myrpl import MyRPL

load_dotenv()

def login_command():
    myrpl = MyRPL()
    myrpl.login()

def fetch_command(args):
    myrpl = MyRPL()
    myrpl.fetch_course(args.course_id, args.token, args.force)

def main():
    parser = argparse.ArgumentParser(description="CLI tool for MyRPL course activities")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Log in and store credentials")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch and save activities for a given course ID")
    fetch_parser.add_argument("course_id", type=int, help="ID of the course to fetch activities from")
    fetch_parser.add_argument("-t", "--token", help="Bearer token for authentication. If not provided, uses MYRPL_BEARER_TOKEN from environment or stored credentials")
    fetch_parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of existing files")

    args = parser.parse_args()

    if args.command == "login":
        login_command()
    elif args.command == "fetch":
        fetch_command(args)
    elif args.command is None:
        parser.print_help()

if __name__ == "__main__":
    main()
