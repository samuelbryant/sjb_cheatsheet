"""Module responsible for reading/writing cheat sheet json to file."""
import os
import json
import warnings
import cheatsheet.classes
import cheatsheet.display


def _encode_entry(entry):
  entry.validate()
  return {
    'oid': entry.oid,
    'primary': entry.primary,
    'tags': list(entry.tags),
    'clue': entry.clue,
    'answer': entry.answer
  }

def _decode_entry(json_object):
  return(cheatsheet.classes.Entry(
    clue=json_object['clue'],
    answer=json_object['answer'],
    primary=json_object['primary'],
    tags=set(json_object['tags']),
    oid=json_object['oid']))

def _get_default_cheatsheet_file():
  if 'XDG_DATA_HOME' in os.environ:
    return os.environ['XDG_DATA_HOME']+'/'+'sjb/cheatsheet/cheatsheet.json'
  return os.environ['HOME']+'/.local/share/sjb/cheatsheet/cheatsheet.json'

def save_cheatsheet(cs, fname=None):
  """Saves a cheatsheet object to a json file.

  This attempts to save the CheatSheet object cs as a file by first looking at:
    1) the given file name string fname
    2) the file that the CheatSheet object was originally read from
    3) the default file stored in a standard xdg linux manner.

  Arguments:
    fname: str an optional file name to read the cheat sheet from.
  """
  top_json = {
    'cheatsheet': {
      'version': cs.version,
      'modified_date': cs.modified_date,
      'entries': [_encode_entry(e) for e in cs.items]
    }
  }

  fname = fname or cs.source_filename or _get_default_cheatsheet_file()
  json_file = open(fname, "w")

  json_file.write(json.dumps(top_json, indent=2))

def load_cheatsheet(fname=None):
  """Loads a cheat sheet from a json file.

  Arguments:
    fname: str an optional file name to read the cheat sheet from.

  Returns:
    CheatSheet: object with contents given by the loaded file.
  """
  fname = fname or _get_default_cheatsheet_file()

  # If file doesn't exist, return a new blank cheat sheet.
  if not os.path.isfile(fname):
    warnings.warn('no cheatsheet file found', UserWarning)
    return cheatsheet.classes.CheatSheet(source_fname=fname)

  json_file = open(fname)
  ob = json.load(json_file)['cheatsheet']
  modified_date = ob['modified_date'] if 'modified_date' in ob else None


  cs = cheatsheet.classes.CheatSheet(
    source_fname=fname, modified_date=modified_date)
  for entry_json in ob['entries']:
    entry = _decode_entry(entry_json)
    cs.add_item(entry, initial_load=True)

  return cs
