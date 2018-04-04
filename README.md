# Overview
**This program is not designed to be usable by anyone except me, yet** - see the Installation section for more details.

sjb_cheatsheet is a simple command-line program to add entries to a cheat sheet and display them in an organized manner. 
Similar to 'git' this program has subcommands to interact with the cheatsheet. The basic subcommands are 'add', 'show', 'remove', and 'update'

Each cheatsheet entry has four components:
1. Clue - this is a short description of the cheat sheet entry. For example 'markdown italics' would be a valid clue.
2. Answer - this is the long explanation of the clue. In the above example, the answer could be 'Italics are done with asterisks like *this*'
3. Primary - this is the primary tag classifying this entry. In the above example, this could be 'markdown'
4. Tags - These are any other tags which might apply to the entry. In the above example this could be 'formatting'

The basic idea is to centralize all 'cheat sheet' like notes into a single file. Then to see all notes concerning a single topic you can filter them by the primary tag or secondary tags.

# Usage
See `sjb_cheatsheet -h` for more information. The most basic usage of this program could consist of just the 'add' and 'show' commands. 

## Example
~~~~
$ sjb_cheatsheet add bash echo 'echo is a simple program that prints its argument to stdout' bash,unix,posix
$ sjb_cheatsheet add python 'get user input' 'In python2, raw_input() is a simple way to get user input. In python3, input(msg) is preferred.' python,code

$ sjb_cheatsheet show
1  bash             bash, unix, posix
   echo             echo is a simple program that prints its argument to
                    stdout
2  python           python,code
   get user input   In python2, raw_input() is a simple way to get user
                    input. In python3, input(msg) is preferred.
$ sjb_cheatsheet show --primary python
2  get user input   In python2, raw_input() is a simple way to get user
                    input. In python3, input(msg) is preferred.
~~~~

# Installation
This program is not currently written in a way that allows for easy deployment to other systems. It's still in the super-alpha stage. However, for my own reference, and just-in-case, here is a rough explanation of how one could deploy this project:

1. The directory src/cheatsheet should be placed within some directory that is on the python classpath.
For example, in my setup, cheatsheet is located at ~/bin/code_python/cheatsheet and my .profile includes a line like:
  `PYTHONPATH="${PYTHONPATH}:/home/$USER/bin/code_python"`

2. The data directory must be setup.
By default this program reads/writes to the directory '~/.local/share/sjb_cheatsheet'. The user needs to manually create this folder.

3. Finally, add an alias to the program in .bash_aliases or whereever:
`alias sjb_cheatsheet='/path/to/directory/cheatsheet/main.py'`

It should work after this. I haven't actually tried to see what happens when there is no .json file so maybe not.
