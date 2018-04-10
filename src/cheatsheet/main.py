#!/usr/bin/python3
"""Module responsible for implementing the command line front end."""
import sys
import argparse
import operator
import cheatsheet.classes
import cheatsheet.display
import cheatsheet.fileio


PROGRAM = 'sjb_cheatsheet'
USAGE = '''\
sjb_cheatsheet command [<args>]

Where command can be:
  add     Add a new entry to the cheatsheet
  info    Shows meta info about cheatsheet
  remove  Removes an entry from the cheatsheet
  show    Shows the entries in a cheatsheet
  update  Updates an entry in the cheatsheet
'''


def _set_arg(string):
  return set(string.split(','))


def _tags_arg(string):
  """Pulls out primary tag (first tag) from the others"""
  tags = string.split(',')
  return (tags[0], set(tags[1:]))


def _add_arguments_generic(parser):
  """Adds argparse arguments that apply universally to all commands."""
  parser.add_argument(
    '--style', type=int,
    choices=cheatsheet.display.FORMAT_CHOICES,
    help='Specifies which format style is used when displaying entries.')
  parser.add_argument(
    '--file', type=str,
    help='Manually specify a cheatsheet to work with')


class Program(object):
  """Class responsible for implementing command line front end."""

  def __init__(self):
    parser = argparse.ArgumentParser(
      description='CheatSheet program', usage=USAGE)
    parser.add_argument('command', type=str, help='Command to run')
    args = parser.parse_args(sys.argv[1:2])

    if not hasattr(self, args.command):
      print('Unrecognized command: '+str(args.command))
      parser.print_help()
      exit(1)

    # use dispatch pattern to invoke method with same name
    getattr(self, args.command)()

  def add(self):
    """Implements the 'add' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' add',
      description='Add an entry to your cheat sheet')

    ## Core required arguments
    parser.add_argument(
      'tags', type=_tags_arg,
      help='Comma separated list of tags. The first tag is the "primary" tag')
    parser.add_argument(
      'clue', type=str,
      help='The short string by which to identify this cheatsheet entry')
    parser.add_argument(
      'answer', type=str,
      help='The full explanation of this entry. Can be as long as required')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    # Load cheatsheet, add an entry, then save the results
    cs = cheatsheet.fileio.load_cheatsheet(fname=args.file)
    entry = cheatsheet.classes.Entry(
      args.clue, args.answer, primary=args.tags[0], tags=args.tags[1])
    cs.add_entry(entry)
    cheatsheet.fileio.save_cheatsheet(cs, fname=args.file)

    # Print the results.
    cheatsheet.display.display_entry(entry, format_style=args.style)

  def info(self):
    """Implements the 'info' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' info',
      description='Shows meta-information about the cheat sheet')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    cs = cheatsheet.fileio.load_cheatsheet(fname=args.file)

    primary_map = cs.primary_to_entries
    tag_set = cs.tag_set
    entries = cs.entries
    primary_count = {key: len(primary_map[key]) for key in primary_map}
    sorted_primary = sorted(
      primary_count.items(), key=operator.itemgetter(1), reverse=True)

    print('Cheat sheet information:')
    print('  %-25s %s' % ('Number of entries', len(entries)))
    print('  %-25s %s' % ('Number primary tags', len(primary_map.keys())))
    print('  %-25s %s' % ('Number of tags', len(tag_set)))
    print('  %-25s %s' % ('Tag list', ', '.join(tag_set)))
    print('%-27s %s' % ('Primary key', 'Count'))
    for key, count in sorted_primary:
      print('  %-25s %d' % (key, count))

  def show(self):
    """Implements the 'show' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' show',
      description='Show the cheatsheet or a subsection of it')

    ## Optional arguments
    parser.add_argument(
      '--tags', type=_set_arg,
      help='Only show entries which match this comma separated list of tags')
    parser.add_argument(
      '--or', dest='andor', action='store_const',
      const=cheatsheet.classes.SEARCH_OR,
      default=cheatsheet.classes.SEARCH_OR,
      help='Show entries which match ANY of the given conditions')
    parser.add_argument(
      '--and', dest='andor', action='store_const',
      const=cheatsheet.classes.SEARCH_AND,
      default=cheatsheet.classes.SEARCH_OR,
      help='Only show entries which match ALL of the given conditions')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    # Special handling. If no format style is given and the user gave some
    # filter, then we display the simple style. e.g. if I type show 'bash', I
    # dont want to see 'bash' in every entry.
    if not args.style and args.tags:
      args.style = cheatsheet.display.FORMAT_STYLE_SIMPLE

    # Load cheat sheet, find matching entries, and print
    cs = cheatsheet.fileio.load_cheatsheet(fname=args.file)
    entries = cs.get_entries(args.andor, tags=args.tags)
    if entries:
      cheatsheet.display.display_entries(entries, format_style=args.style)
    else:
      print('No entries found')

  def remove(self):
    """Implements the 'remove' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' remove',
      description='Remove an entry from the cheatsheet')
    parser.add_argument(
      'oid', type=int, help='ID of the entry you wish to delete')
    parser.add_argument(
      '--f', dest='force', action='store_const', const=1, default=0,
      help='Force: dont ask before completing the removal')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    # Load cheat sheet
    cs = cheatsheet.fileio.load_cheatsheet(fname=args.file)

    # If not in force mode, ask user before proceeding.
    entry = cs.get_entry(args.oid)
    if not args.force:
      question = (
        'The entry given by oid '+str(args.oid)+' is:\n' + \
        cheatsheet.display.entry_repr(entry, format_style=args.style) + \
        '\nAre you sure you want to delete it? ')
      cont = cheatsheet.display.prompt_yes_no(question, default=False)
      if not cont:
        exit(0)

    removed = cs.remove_entry(args.oid)
    cheatsheet.fileio.save_cheatsheet(cs, fname=args.file)

    # Print the results only on force mode (otherwise user just saw item).
    if args.force:
      print('Removed entry:')
      cheatsheet.display.display_entry(removed, format_style=args.style)

  def update(self):
    """Implements the 'update' command."""
    parser = argparse.ArgumentParser(
      prog=PROGRAM + ' update',
      description='Update an entry by changing its contents')
    parser.add_argument(
      'oid', type=int,
      help='ID of the entry you wish to update')
    parser.add_argument(
      '--tags', type=_tags_arg,
      help='Comma separated list of tags. The first tag is the "primary" tag')
    parser.add_argument(
      '--clue', type=str,
      help='The short string by which to identify this cheatsheet entry')
    parser.add_argument(
      '--answer', type=str,
      help='The full explanation of this entry. Can be as long as required')
    _add_arguments_generic(parser)
    args = parser.parse_args(sys.argv[2:])

    # Load cheat sheet
    cs = cheatsheet.fileio.load_cheatsheet(fname=args.file)
    # Update entry in local CheatSheet object.
    updated = cs.update_entry(
      args.oid, clue=args.clue, answer=args.answer,
      primary=args.tags[0] if args.tags else None,
      tags=args.tags[1] if args.tags else None)
    # Save CheatSheet object to file.
    cheatsheet.fileio.save_cheatsheet(cs, fname=args.file)

    # Print the results.
    cheatsheet.display.display_entry(updated, format_style=args.style)

if __name__ == '__main__':
  Program()
