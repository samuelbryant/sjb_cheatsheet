## cheatsheet.read module
## This file contains logic for reading from and writing to the cheatshset file.
import time


## Global constants which determine search method.
SEARCH_AND = 0
SEARCH_OR = 1


class Entry:
  """Class representing an entry in a cheat sheet"""

  def __init__(self, primary, clue, answer, tags, id=None):
    self.id = id
    self.clue = clue
    self.primary = primary
    self.answer = answer
    self.tags = set(tags)

  def matches(self, andor, primary=None, tags={}):
    """Checks if this entry matches the primary and tag arguments. 

    Arguments:
      andor: Determines if ALL conditions must be met or ANY condition must be
        met. Should be SEARCH_AND or SEARCH_OR
      primary: String primary tag to match.
      tags: Set of secondary tags to match.  

    Returns:
      bool: True if it matches, false otherwise.
    """
    # If andor is SEARCH_AND, we must match all of the conditions:
    if andor is SEARCH_AND:
      return \
        (not primary or primary == self.primary) and \
        (not tags or tags.issubset(self.tags))
    elif andor is SEARCH_OR:
      return \
        (not primary and not tags) or \
        (primary and primary == self.primary) or \
        (tags and bool((tags.intersection(self.tags))))
    else:
      raise ProgrammingError(
        'Entry.matches', 'invalid andor argument '+str(andor))


class CheatSheet:
  """Class that represents an entire cheat sheet. It is typically read from a file at the start of a session and written to a file at the end of a session. It has methods for querying a subset of the full entries."""

  def __init__(self, version=None, modified_date=None, src_fname=None):
    self.version = version
    self.src_fname = src_fname
    self.modified = False
    self.modified_date = modified_date
    self.last_entry_id = 0
    
    # Maps holding cheat sheet meta data.
    self.entries = []
    self.primary_to_entries = {}
    self.tag_set = set()

    # Set of all entry ID's to avoid duplicate ID's
    self.id_set = set()

  def _set_next_entry_id(self):
    """Returns a suitable ID for a new entry and increments ID state."""
    self.last_entry_id += 1
    return(self.last_entry_id)

  def get_entries(self, andor=SEARCH_OR, primary=None, tags={}):
    """Returns a list of entries which match the given conditions.

    Arguments:
      andor: Determines if ALL conditions must be met or ANY condition must be
        met. Should be SEARCH_AND or SEARCH_OR
      primary: String primary tag to match.
      tags: Set of secondary tags to match.  

    Returns:
      list: A list of Entry objects matching the criteria.
    """
    return([e for e in self.entries if e.matches(andor, primary, tags)])

  def get_entry(self, id):
    """Returns entry with the given id.

    Returns:
      Entry: the entry with the matching ID.

    Raises:
      InvalidIDError: If no entry has a matching ID.
    """
    for e in self.entries:
      if id is e.id:
        return e
    raise InvalidIDError(
      'CheatSheet.get_entry', 'non-existent entry id '+str(id))

  def update_entry(self, id, primary=None, clue=None, answer=None, tags=None):
    """Updates entry given by id and returns the result.
    
    Only arguments that are truthy will be updated. If no entry is found at that id, the method returns None. The meta CheatSheet objects are updated are updating the entry.

    Returns:
      Entry: The newly updated entry object.

    Raises:
      InvalidIDError: If no entry has a matching ID.
    """
    entry = self.get_entry(id)

    if primary or clue or answer or tags:
      entry.primary = primary or entry.primary
      entry.clue = clue or entry.clue
      entry.answer = answer or entry.answer
      entry.tags = (tags and set(tags)) or entry.tags
      self._mark_modified()
      self._recompute_object_maps()

    return(entry)

  def remove_entry(self, id):
    """Removes the entry with the specified ID and updates meta data.

    Returns:
      Entry: The removed entry object.

    Raises:
      InvalidIDError: If no entry has a matching ID. 
    """
    for i in range(len(self.entries)):
      if id is self.entries[i].id:
        deleted = self.entries.pop(i)
        # Mark as modified.
        self._mark_modified()
        # Recalculate maps like id_set and tag_set since we lost an element.
        self._recompute_object_maps()

        return(deleted)
    raise InvalidIDError(
      'CheatSheet.remove_entry', 'non-existent entry id '+str(id))

  def add_entry(self, entry, initial_load=False):
    """Adds an entry to this cheatsheet.

    Args:
      entry: The Entry object to add. It should only have an ID set if it was
        loaded from cheat sheet file.
      initial_load: Indicates that this entry object is from the cheat sheet 
        file and is not a new addition to the cheat sheet.

    Raises:
      ProgrammingError: If not initial_load but the entry object already has
        an ID.
      ProgrammingError: If initial_load but the entry object has no ID.
        is false.
    """

    # Make sure any 'init load' entry already has an id
    if initial_load and not entry.id:
      raise ProgrammingError('CheatSheet.add_entry', 'Old Entry missing ID!')
    # Make sure any new entry does not have an id
    if not initial_load and entry.id:
      raise ProgrammingError('CheatSheet.add_entry', 'New Entry has ID!')
    
    if not initial_load: 
      # Set the id correctly
      entry.id = self._set_next_entry_id()
      
      # Mark cheatsheet as modified
      self._mark_modified()

    # Actually add the element.
    self.entries.append(entry)
    self._update_object_maps(entry)

  def _update_object_maps(self, entry):
    """Updates meta object maps like tag_set to reflect contents of entry.

    Raises:
      IllegalStateError: If a duplicate ID is encountered.
    """
    
    # Sanity check: Make sure there are no duplicate IDs.
    if entry.id in self.id_set:
      raise IllegalStateError(
        'CheatSheet._update_object_maps', 'duplicate ID found.')
    self.id_set.add(entry.id)

    if entry.primary not in self.primary_to_entries.keys():
      self.primary_to_entries[entry.primary] = []
    self.primary_to_entries[entry.primary].append(entry)
    
    for tag in entry.tags:
      self.tag_set.add(tag)

    # Set last_id to the highest ID.
    if entry.id > self.last_entry_id:
      self.last_entry_id = entry.id

  def _recompute_object_maps(self):
    """Recomputes all meta object maps like tag_set, primary_to_entries, etc.

    This should be used after making a non-trivial change to the list like modifying an elements tags or removing an element.
    """
    self.primary_to_entries = {}
    self.tag_set = set()
    self.id_set = set()
    self.last_entry_id = 0

    for entry in self.entries:
      self._update_object_maps(entry)
    
  def _mark_modified(self, timestamp=None):
    """Marks the CheatSheet as modified at the given time.

    This uses the current time if no timestamp is specified.
    """
    self.modified=True
    self.modified_date=timestamp or time.time()


class Error(Exception):
  """Base class for exceptions for this program."""
  pass


class InvalidIDError(Error):
  """Exception raised when a specified entry ID does not exist."""

  def __init__(self, method, msg):
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('InvalidIDError', method, msg)
    

class ProgrammingError(Error):
  """Exception used to signal something that should never happen.

  This indicates that there is an error in my code somewhere."""
  def __init__(self, method, msg):
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('ProgrammingError', method, msg)


class IllegalStateError(Error):
  """Exception used to signal something is wrong, but its not clear why."""
  def __init__(self, method, msg):
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('IllegalStateError', method, msg)


class MalformedCheatSheet(Error):
  """Exception used to signal that the cheatsheet json file has errors."""
  def __init__(self, method, msg):
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('MalformedCheatSheet', method, msg)
