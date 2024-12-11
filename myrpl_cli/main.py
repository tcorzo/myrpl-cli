import logging
import argparse
from dotenv import load_dotenv
from myrpl_cli.errors import MissingCredentialsError, NotMyRPLDirectoryError
from myrpl_cli.myrpl import MyRPL
from myrpl_cli.api import API
from myrpl_cli.credential_manager import CredentialManager

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def login_command(myrpl: MyRPL):
	myrpl.login()


def fetch_command(myrpl: MyRPL, args):
	try:
		myrpl.fetch_course(args.course_id, args.token, args.force)
	except MissingCredentialsError:
		logger.error("You haven't logged in yet. Do so with `myrpl login`")


def test_command(myrpl: MyRPL, args):
	try:
		myrpl.test(args)
	except NotMyRPLDirectoryError:
		logger.error("not a myrpl directory: .myrpl")


def list_command(myrpl: MyRPL, args):
	myrpl.list(args.all)


def main():
	parser = argparse.ArgumentParser(description="CLI tool for MyRPL course activities")
	subparsers = parser.add_subparsers(dest="command", help="Available commands")

	# Login command
	subparsers.add_parser("login", help="Log in and store credentials")

	# List command
	list_parser = subparsers.add_parser("list", help="List all registered courses and their IDs")
	list_parser.add_argument("-a", "--all", action="store_true", help="List all courses, including hidden ones")

	# Fetch command
	fetch_parser = subparsers.add_parser("fetch", help="Fetch and save activities for a given course ID")
	fetch_parser.add_argument("course_id", type=int, help="ID of the course to fetch activities from")
	fetch_parser.add_argument("-t", "--token", help="Bearer token for authentication.")
	fetch_parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of existing files")

	# Test command
	subparsers.add_parser("test", help="Run the current course/category/activity tests")

	known_args, unknown_args = parser.parse_known_args()

	cred_mgr = CredentialManager()
	api = API(cred_mgr)
	myrpl = MyRPL(api, cred_mgr)

	if known_args.command == "login":
		login_command(myrpl)
	elif known_args.command == "list":
		list_command(myrpl, known_args)
	elif known_args.command == "fetch":
		fetch_command(myrpl, known_args)
	elif known_args.command == "test":
		# Pass both known and unknown args to test_command
		test_command(myrpl, unknown_args)
	else:
		parser.print_help()


if __name__ == "__main__":
	main()
