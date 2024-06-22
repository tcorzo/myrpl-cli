import argparse
from dotenv import load_dotenv
import logging

from myrpl_cli.myrpl import MyRPL
from myrpl_cli.api import API
from myrpl_cli.credential_manager import CredentialManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_command(myrpl):
    myrpl.login()

def fetch_command(myrpl, args):
    myrpl.fetch_course(args.course_id, args.token, args.force)

def main():
    parser = argparse.ArgumentParser(description="CLI tool for MyRPL course activities")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    login_parser = subparsers.add_parser("login", help="Log in and store credentials")
    fetch_parser = subparsers.add_parser("fetch", help="Fetch and save activities for a given course ID")
    fetch_parser.add_argument("course_id", type=int, help="ID of the course to fetch activities from")
    fetch_parser.add_argument("-t", "--token", help="Bearer token for authentication.")
    fetch_parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of existing files")

    args = parser.parse_args()

    api = API()
    cred_mgr = CredentialManager()
    myrpl = MyRPL(api, cred_mgr)

    if args.command == "login":
        login_command(myrpl)
    elif args.command == "fetch":
        fetch_command(myrpl, args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
