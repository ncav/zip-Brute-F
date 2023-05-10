#!/usr/bin/env python3

import sys
import itertools
import zipfile
import zlib
import argparse
from zipfile import BadZipFile

class Cracker:
    def __init__(self, zip_file, charset=None, min_length=None, max_length=None, wordlist=None, verbose=False):
        self.zip_file = zip_file
        self.charset = charset
        self.min_length = min_length
        self.max_length = max_length
        self.wordlist = wordlist
        self.verbose = verbose
        self.found = False

    def try_password(self, password):
        try:
            self.zip_file.extractall(pwd=bytes(password, 'utf-8'))
            print(f"Password found: {password}")
            self.found = True
        except (RuntimeError, zlib.error, zipfile.BadZipFile):
            if self.verbose:
                print(f"Trying password: {password}")

    def crack_bruteforce(self):
        for length in range(self.min_length, self.max_length + 1):
            for attempt in itertools.product(self.charset, repeat=length):
                if self.found:
                    return
                password = ''.join(attempt)
                self.try_password(password)

    def crack_wordlist(self):
        with open(self.wordlist, 'r') as wordlist_file:
            for line in wordlist_file:
                if self.found:
                    return
                password = line.strip()
                self.try_password(password)

    def crack(self):
        if self.charset:
            self.crack_bruteforce()
        elif self.wordlist:
            self.crack_wordlist()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="ZIP file to crack", required=True)
    parser.add_argument("-c", "--charset", help="Set of characters to try")
    parser.add_argument("-m", "--min_length", help="Minimum password length", type=int)
    parser.add_argument("-M", "--max_length", help="Maximum password length", type=int)
    parser.add_argument("-w", "--wordlist", help="Path to the wordlist file")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")

    args = parser.parse_args()

    if (args.charset is None) == (args.wordlist is None):
        parser.error("Either --charset or --wordlist must be provided, but not both")

    if args.charset and (args.min_length is None or args.max_length is None):
        parser.error("When using --charset, both --min_length and --max_length are required")

    with zipfile.ZipFile(args.file) as zip_file:
        cracker = Cracker(zip_file, args.charset, args.min_length, args.max_length, args.wordlist, args.verbose)
        cracker.crack()

if __name__ == '__main__':
    main()
