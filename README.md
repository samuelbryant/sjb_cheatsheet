# Overview
A simple CRUD command-line program for working with 'cheat sheets'

sjb-cheatsheet is a simple command-line program to add entries to a cheat sheet and display them in an organized manner. 
Similar to 'git' this program has subcommands to interact with the cheatsheet. The basic subcommands are 'add', 'show', 'remove', and 'update'

Each cheatsheet entry has four components:
1. Clue - this is a short description of the cheat sheet entry. For example 'markdown italics' would be a valid clue.
2. Answer - this is the long explanation of the clue. In the above example, the answer could be 'Italics are done with asterisks like *this*'
3. Primary - this is the primary tag classifying this entry. In the above example, this could be 'markdown'
4. Tags - These are any other tags which might apply to the entry. In the above example this could be 'formatting'

The basic idea is to centralize all 'cheat sheet' like notes into a single file. Then to see all notes concerning a single topic you can filter them by the primary tag or secondary tags.

# Usage
See `sjb-cheatsheet -h` for more information. The most basic usage of this program could consist of just the 'add' and 'show' commands. 

## Example
~~~~
$ sjb-cheatsheet add bash echo 'echo is a simple program that prints its argument to stdout' bash,unix,posix
$ sjb-cheatsheet add python 'get user input' 'In python2, raw_input() is a simple way to get user input. In python3, input(msg) is preferred.' python,code
$ sjb-cheatsheet show
1  bash             bash, unix, posix
   echo             echo is a simple program that prints its argument to
                    stdout
2  python           python,code
   get user input   In python2, raw_input() is a simple way to get user
                    input. In python3, input(msg) is preferred.
$ sjb-cheatsheet show --tags python
2  get user input   In python2, raw_input() is a simple way to get user
                    input. In python3, input(msg) is preferred.
~~~~

# Installation
This program is in pre-alpha and is not using any deployment tools so I make zero guarantees about installation.

However, I have written a crude script that should more or less work provided the user has `python3.6` installed in a linux environment and has all of the required python dependencies. Since these dependencies are subject to change, and this is my first time writing a deployed python app, I have not bothered to record them or incorporate them into the install script. In the future I hope to fix this.

## Instructions

1. cd into the directory containing this file. 

2. run `./install.sh` as a regular user

3. create the data directory using `mkdir -p ~/.local/share/sjb/cheatsheet`
