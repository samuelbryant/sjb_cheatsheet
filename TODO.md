# Short Term

1. Fix secondary tag system. Currently they are not super useful yet they are always required. In addition, there is some ambiguity about whether or not 'primary' tags are always also 'secondary' tags. Also there should be a much simpler way to show all entries with a given tag as either the primary or secondary tag.

2. Come up with better or more flexible entry formatting system. Right now the system has a few fixed formatting options that the user can choose from.

3. Write `info` subcommand that shows meta-things like "How many entries exist with each tag?".

4. Add project linting.

5. Object handling refactor: There needs to be a simple point of object conversion and validation between json load and object initialization. This way it will be clear where changes are made. Do not do any validation or parsing in the constructors (or do all of it that way)

# Long Term

1. Make project deployable. I've never done this before so I don't even know where to start.

2. Add GUI frontend. I've never done python GUI so this would be a challenge

3. Add unit testing.
