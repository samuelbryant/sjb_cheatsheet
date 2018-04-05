import os,json
import cheatsheet.classes
import cheatsheet.display


def _encode_entry(entry):
  return {
    'id': entry.id,
    'primary': entry.primary,
    'tags': list(entry.tags),
    'clue': entry.clue,
    'answer': entry.answer
  }

def _decode_entry(json_object):
  return(cheatsheet.classes.Entry(
    json_object['primary'],
    json_object['clue'],
    json_object['answer'],
    set(json_object['tags']),
    id=json_object['id']))

def _get_default_cheatsheet_file():
  if 'XDG_DATA_HOME' in os.environ:
    return(os.environ['XDG_DATA_HOME']+'/'+'sjb_cheatsheet/cheatsheet.json')
  else:
    return(os.environ['HOME']+'/.local/share/sjb_cheatsheet/cheatsheet.json')

def save_cheatsheet(cs, fname=None):
  """Saves a cheatsheet object to a json file.
  This attempts to save the CheatSheet object cs as a file by first looking at:
    1) the given file name string fname
    2) the file that the CheatSheet object was originally read from
    3) the default file stored in a standard xdg linux manner."""

  entries_js = []
  for entry in cs.entries:
    entries_js.append(_encode_entry(entry))

  top_json = {
    'cheatsheet': {
      'version': cs.version,
      'modified_date': cs.modified_date,
      'entries': entries_js
    }
  }

  fname = fname or cs.src_fname or _get_default_cheatsheet_file()
  file = open(fname, "w")
  
  file.write(json.dumps(top_json, indent=2))

def load_cheatsheet(fname=None):
  fname = fname or _get_default_cheatsheet_file()

  # Attempt to open
  if not os.path.isfile(fname):
    cheatsheet.display.wrn("no cheatsheet file found")
    return(cheatsheet.classes.CheatSheet(src_fname=fname))

  file = open(fname)
  ob = json.load(file)['cheatsheet']
  modified_date = ('modified_date' in ob and ob['modified_date']) or None

  # Create new blank cs book.
  cs = cheatsheet.classes.CheatSheet(
    src_fname=fname, modified_date=modified_date)
  
  # Add entries to CheatSheet
  for entry_json in ob['entries']:
    entry = _decode_entry(entry_json)
    cs.add_entry(entry, initial_load=True)

  return(cs)