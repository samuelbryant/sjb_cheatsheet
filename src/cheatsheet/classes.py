"""Module containing all core class definitions for this program."""
import time


## Global constants which determine search method.
SEARCH_AND = 0
SEARCH_OR = 1


def _default_if_none(value, default):
  """Returns value if it is not None, otherwise default."""
  return value if value is not None else default


class Entry:
  """Class representing an entry in a cheat sheet"""

  def __init__(self, clue, answer, primary, tags, oid=None):
    # Values that should be set at construction time
    self.clue = clue
    self.answer = answer
    self.primary = primary
    self.tags = _default_if_none(tags, set())

    # Values that should only be set when reading from file.
    self.oid = oid

    # Validation
    self.validate()


  def matches(self, andor, tags=None):
    """Checks if this entry matches the tag arguments.

    Arguments:
      andor: Determines if ALL conditions must be met or ANY condition must be
        met. Should be SEARCH_AND or SEARCH_OR
      tags: Set of tags to match (can be primary or secondary.)

    Returns:
      bool: True if it matches, false otherwise.
    """
    if not tags:
      return True

    if andor is SEARCH_AND:
      for tag in tags:
        if tag != self.primary and tag not in self.tags:
          return False
      return True

    elif andor is SEARCH_OR:
      for tag in tags:
        if tag == self.primary or tag in self.tags:
          return True
      return False
    else:
      raise ProgrammingError(
        'Entry.matches', 'invalid andor argument '+str(andor))

  def validate(self):
    """Validates that the values of this item are sensible.

    This method should be called twice: The first time at the end of the
    initialization code to make sure the user is not misusing the constructor.
    The second time should be before saving to a database to make sure that
    manipulations made to this item after initialization were valid.

    Raises:
      InvalidEntryError: If validation fails
    """
    if not self.clue or not isinstance(self.clue, str):
      raise InvalidEntryError('Bad entry clue: '+str(self.clue))
    if not self.primary or not isinstance(self.primary, str):
      raise InvalidEntryError('Bad primary: '+str(self.primary))
    if not self.answer or not isinstance(self.answer, str):
      raise InvalidEntryError('Bad answer: '+str(self.answer))
    if not isinstance(self.tags, set):
      raise InvalidEntryError('Bad tags: '+str(self.tags))

    if self.oid is not None and not isinstance(self.oid, int):
      raise InvalidEntryError('Bad oid: '+str(self.oid))


class CheatSheet:
  """Class that represents an entire cheat sheet.

  It is typically read from a file at the start of a session and written to a
  file at the end of a session. It has methods for querying a subset of the
  full entries.
  """

  def __init__(self, version=None, modified_date=None, src_fname=None):
    self.version = version
    self.src_fname = src_fname
    self.modified = False
    self.modified_date = modified_date
    self.last_entry_oid = 0

    # Maps holding cheat sheet meta data.
    self.entries = []
    self.primary_to_entries = {}
    self.tag_set = set()

    # Set of all entry oid's to avoid duplicate oid's
    self.oid_set = set()

  def _set_next_entry_oid(self):
    """Returns a suitable oid for a new entry and increments oid state."""
    self.last_entry_oid += 1
    return self.last_entry_oid

  def get_entries(self, andor=SEARCH_OR, tags=None):
    """Returns a list of entries which match the given conditions.

    Arguments:
      andor: Determines if ALL conditions must be met or ANY condition must be
        met. Should be SEARCH_AND or SEARCH_OR
      tags: Set of tags to match (can be primary or secondary.)

    Returns:
      list: A list of Entry objects matching the criteria.
    """
    return [e for e in self.entries if e.matches(andor, tags)]

  def get_entry(self, oid):
    """Returns entry with the given oid.

    Returns:
      Entry: the entry with the matching oid.

    Raises:
      InvalidIDError: If no entry has a matching oid.
    """
    for entry in self.entries:
      if oid is entry.oid:
        return entry
    raise InvalidIDError(
      'CheatSheet.get_entry', 'non-existent entry oid '+str(oid))

  def update_entry(self, oid, clue=None, answer=None, primary=None, tags=None):
    """Updates entry given by oid and returns the result.

    Only arguments that are not None will be updated. If no entry is found at
    that oid, an Error is raised. The meta objects are updated to reflect the
    new contents of the entry.

    Returns:
      Entry: The newly updated entry object.

    Raises:
      InvalidIDError: If no entry has a matching oid.
    """
    entry = self.get_entry(oid)

    # TODO: clean this up.
    if (primary is not None or clue is not None or answer is not None or
        tags is not None):
      entry.primary = _default_if_none(primary, entry.primary)
      entry.clue = _default_if_none(clue, entry.clue)
      entry.answer = _default_if_none(answer, entry.answer)
      entry.tags = _default_if_none(tags, entry.tags)
      self._mark_modified()
      self._recompute_object_maps()

    return entry

  def remove_entry(self, oid):
    """Removes the entry with the specified oid and updates meta data.

    Returns:
      Entry: The removed entry object.

    Raises:
      InvalidIDError: If no entry has a matching oid.
    """
    for i in range(len(self.entries)):
      if oid is self.entries[i].oid:
        deleted = self.entries.pop(i)
        # Mark as modified and recompute meta maps.
        self._mark_modified()
        self._recompute_object_maps()

        return deleted
    raise InvalidIDError(
      'CheatSheet.remove_entry', 'non-existent entry oid '+str(oid))

  def add_entry(self, entry, initial_load=False):
    """Adds an entry to this cheatsheet.

    Args:
      entry: The Entry object to add. It should only have an oid set if it was
        loaded from cheat sheet file.
      initial_load: Indicates that this entry object is from the cheat sheet
        file and is not a new addition to the cheat sheet.

    Raises:
      ProgrammingError: If not initial_load but the entry object already has
        an oid.
      ProgrammingError: If initial_load but the entry object has no oid.
        is false.
    """

    # Make sure any 'init load' entry already has an oid
    if initial_load and not entry.oid:
      raise ProgrammingError('CheatSheet.add_entry', 'Old Entry missing oid!')
    # Make sure any new entry does not have an oid
    if not initial_load and entry.oid:
      raise ProgrammingError('CheatSheet.add_entry', 'New Entry has oid!')

    if not initial_load:
      # Set the oid correctly
      entry.oid = self._set_next_entry_oid()

      # Mark cheatsheet as modified
      self._mark_modified()

    # Actually add the element.
    self.entries.append(entry)
    self._update_object_maps(entry)

  def _update_object_maps(self, entry):
    """Updates meta object maps like tag_set to reflect contents of entry.

    Raises:
      IllegalStateError: If a duplicate oid is encountered.
    """

    # Sanity check: Make sure there are no duplicate oids.
    if entry.oid in self.oid_set:
      raise IllegalStateError(
        'CheatSheet._update_object_maps', 'duplicate oid found.')
    self.oid_set.add(entry.oid)

    if entry.primary not in self.primary_to_entries.keys():
      self.primary_to_entries[entry.primary] = []
    self.primary_to_entries[entry.primary].append(entry)

    for tag in entry.tags:
      self.tag_set.add(tag)
    self.tag_set.add(entry.primary)

    # Set last_oid to the highest oid.
    if entry.oid > self.last_entry_oid:
      self.last_entry_oid = entry.oid

  def _recompute_object_maps(self):
    """Recomputes all meta object maps like tag_set, primary_to_entries, etc.

    This should be used after making a non-trivial change to the list like
    modifying an elements tags or removing an element.
    """
    self.primary_to_entries = {}
    self.tag_set = set()
    self.oid_set = set()
    self.last_entry_oid = 0

    for entry in self.entries:
      self._update_object_maps(entry)

  def _mark_modified(self, timestamp=None):
    """Marks the CheatSheet as modified at the given time.

    This uses the current time if no timestamp is specified.
    """
    self.modified = True
    self.modified_date = timestamp or time.time()


class Error(Exception):
  """Base class for exceptions for this program."""
  pass


class InvalidIDError(Error):
  """Exception raised when a specified entry oid does not exist."""

  def __init__(self, method, msg):
    super(InvalidIDError, Error).__init__()
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('InvalidIDError', method, msg)


class InvalidEntryError(Error):
  """Exception raised when entry validation fails.

  This most likely indicates an issue with either encoding, decoding, or
  reading a list made by a prior version.
  """
  def __init__(self, msg):
    super(InvalidEntryError, Error).__init__()
    self.message = '%s: %s' % ('InvalidEntryError', msg)


class ProgrammingError(Error):
  """Exception used to signal something that should never happen.

  This indicates that there is an error in my code somewhere."""
  def __init__(self, method, msg):
    super(ProgrammingError, Error).__init__()
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('ProgrammingError', method, msg)


class IllegalStateError(Error):
  """Exception used to signal something is wrong, but its not clear why."""
  def __init__(self, method, msg):
    super(IllegalStateError, Error).__init__()
    self.message = '%s in method %s\n\tMSG: %s' % \
      ('IllegalStateError', method, msg)
