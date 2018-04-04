import os,textwrap,sys
import cheatsheet.classes

## Global constants that determine the format of the display output
FORMAT_STYLE_1 = 1
FORMAT_STYLE_2 = 2
FORMAT_STYLE_3 = 3
FORMAT_STYLE_SIMPLE = FORMAT_STYLE_3
FORMAT_STYLE_DEFAULT = FORMAT_STYLE_1
FORMAT_CHOICES = [FORMAT_STYLE_1, FORMAT_STYLE_2, FORMAT_STYLE_3]



def wrn(msg):
  print("WARNING: "+msg)  


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

def get_num_cols():
  return int(os.popen('stty size', 'r').read().split()[1])

def indent_paragraph(paragraph, indent_size):
  text = textwrap.wrap(paragraph, width = get_num_cols() - indent_size)
  prefix = '\n' + (' ' * indent_size)
  return prefix.join(text)

def display_entry(entry, format_style=None):
  print(entry_repr(entry,format_style))

def display_entries(entries, format_style=None):
  print(entry_repr_heading(format_style))
  for entry in entries:
    print(entry_repr(entry, format_style))

def entry_repr_heading(format_style=None):
  if format_style is None:
    format_style = FORMAT_STYLE_DEFAULT
  if format_style is FORMAT_STYLE_1:
    return entry_repr_style1.heading
  elif format_style is FORMAT_STYLE_2:
    return entry_repr_style2.heading
  elif format_style is FORMAT_STYLE_3:
    return entry_repr_style3.heading
  else:
    raise cheatsheet.classes.ProgrammingError(
      'display.entry_repr_heading', 'SHOULDNT HAPPEN')

def entry_repr(entry, format_style=None):
  if format_style is None:
    format_style = FORMAT_STYLE_DEFAULT
  if format_style is FORMAT_STYLE_1:
    return entry_repr_style1(entry)
  elif format_style is FORMAT_STYLE_2:
    return entry_repr_style2(entry)
  elif format_style is FORMAT_STYLE_3:
    return entry_repr_style3(entry)
  else:
    raise cheatsheet.classes.ProgrammingError(
      'display.entry_repr', 'SHOULDNT HAPPEN')

def entry_repr_style1(entry):
  """Gets the string representation of the entry."""
  line1='%-3d %-10s %-20s %s' % (entry.id,entry.primary,entry.clue,', '.join(entry.tags))
  line2 = ' '*15 + indent_paragraph(entry.answer, 15)

  return line1 + '\n' + line2
entry_repr_style1.heading = '%-3s %-10s %-20s %s' % ('ID', 'Primary', 'Clues', 'Tags')

def entry_repr_style2(entry):
  """Another option for how to represent entries.

  This one formats like:
  ID  primary   secondary1,secondary2,...
      clue      answer line 1
                answer line 2

  To get a header string for this style, try entry_repr_style2.heading

  Returns:
    str: a string representation of this entry.
  """
  line1 = '%-3d %-15s %s' % (entry.id, entry.primary, ', '.join(entry.tags))
  line2 = '    %-15s %s' % (entry.clue, indent_paragraph(entry.answer, 20))
  return line1 + '\n' + line2
entry_repr_style2.heading = '%-3s %-15s %s' % ('ID', 'Primary', 'Tags')

def entry_repr_style3(entry):
  """Gets the string representation of the entry without tags or primary.

  Returns:
    str: a string representing an entry.
  """
  line2 = '%-3d %-15s %s' % (
    entry.id, entry.clue, indent_paragraph(entry.answer, 20))
  return line2
entry_repr_style3.heading = '%-3s %-15s %s' % ('ID', 'Clue', 'Answer')
