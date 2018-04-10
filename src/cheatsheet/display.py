"""Module responsible for representing todo items and writing to terminal."""
import os
import textwrap
import sys
import cheatsheet.classes

## Global constants that determine the format of the display output
FORMAT_STYLE_SIMPLE = 1
FORMAT_STYLE_FULL = 2
FORMAT_STYLE_DEFAULT = FORMAT_STYLE_FULL
FORMAT_CHOICES = [FORMAT_STYLE_SIMPLE, FORMAT_STYLE_FULL]


def prompt_yes_no(question, default=None):
  """Asks a yes/no question and returns either True or False."""
  prompt = (default is True and 'Y/n') or (default is False and 'y/N') or 'y/n'
  valid = {'yes': True, 'ye': True, 'y': True, 'no': False, 'n': False}

  while True:
    choice = input(question + prompt + ': ').lower()

    if not choice and default is not None:
      return default
    if choice in valid:
      return valid[choice]
    else:
      sys.stdout.write("Invalid reponse\n")

def _get_num_cols():
  return int(os.popen('stty size', 'r').read().split()[1])

def _indent_paragraph(paragraph, indent_size):
  width = _get_num_cols() - indent_size

  # Have to treat new lines specially
  lines = paragraph.split('\n')
  indented = [textwrap.wrap(line, width=width) for line in lines]
  indented = [y for x in indented for y in x]

  prefix = '\n' + (' ' * indent_size)
  return prefix.join(indented)

def display_entry(entry, format_style=None):
  """Prints a string representation of a cheat sheet entry to stdout."""
  print(entry_repr(entry, format_style))

def display_entries(entries, format_style=None):
  """Prints a string representation of a cheat sheet to stdout."""
  print(entry_repr_heading(format_style))
  for entry in entries:
    print(entry_repr(entry, format_style))

def entry_repr_heading(format_style=None):
  """Prints a string heading corresponding to a cheat sheet list to stdout."""
  if format_style is None:
    format_style = FORMAT_STYLE_DEFAULT
  if format_style is FORMAT_STYLE_SIMPLE:
    return _entry_repr_simple.heading
  elif format_style is FORMAT_STYLE_FULL:
    return _entry_repr_full.heading
  else:
    raise cheatsheet.classes.ProgrammingError(
      'display.entry_repr_heading', 'SHOULDNT HAPPEN')

def entry_repr(entry, format_style=None):
  """Returns a string reprentation of a cheat sheet entry.

  Arguments:
    format_style: int indicating which output format should be used.

  Returns:
    str: String representation of a cheat sheet item.
  """
  if format_style is None:
    format_style = FORMAT_STYLE_DEFAULT
  if format_style is FORMAT_STYLE_SIMPLE:
    return _entry_repr_simple(entry)
  elif format_style is FORMAT_STYLE_FULL:
    return _entry_repr_full(entry)
  else:
    raise cheatsheet.classes.ProgrammingError(
      'display.entry_repr', 'SHOULDNT HAPPEN')

def _repr_tags(tags):
  return '#' + ', #'.join(tags) if tags else ''

def _entry_repr_full(entry):
  """Gets the string representation of the entry.

  This one formats like:
  ID  primary   clue
                answer ....
                answer line 2 #tag1,#tag2

  Returns:
    str: a string representation of this entry.
  """
  rep = '%-3d %-10s %s\n%s\n%s' % (
    entry.oid, entry.primary, entry.clue, entry.answer, _repr_tags(entry.tags))
  rep = _indent_paragraph(rep, 15)
  return rep
  # return line1 + '\n' + line2
_entry_repr_full.heading = '%-3s %-10s %-20s' % (
  'ID', 'Primary', 'Clues')

def _entry_repr_simple(entry):
  """Gets the string representation of the entry without tags or primary.

  Returns:
    str: a string representing an entry.
  """
  line2 = '%-3d %-20s %s' % (
    entry.oid, entry.clue, _indent_paragraph(entry.answer, 25))
  return line2
_entry_repr_simple.heading = '%-3s %-20s %s' % ('ID', 'Clue', 'Answer')
