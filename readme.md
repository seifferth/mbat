# mbat – batch processing tool for sending emails

## Dependencies

- python3
- python-pyyaml (if not included with python3 yet)
- python3-pypdf2

## Compiling

`mbat` is compiled into a single, self-contained bash script at `out/mbat`.
Simply run `make` to compile it.

## Usage

A basic mbat session looks like this:

```
mbat init   # Initialize the current working directory for mbat.
            # Note that the current working directory must be
            # empty for mbat to initialize it.

# Manually adjust 'mbat.template' and 'mbat.content'

mbat prep   # Prepare '*.mail' files and optional attachment
            # directories.

# Manually confirm that '*.mail' and attachments are as desired.
# These files can still be adjusted manually at this stage. It
# is also possible to recreate all files by running 'mbat prep'
# again.

mbat send   # Send out emails as specified in the '*.mail' files.
            # Files will be removed once the email has been sent.

# Once the emails have been sent, the current working directory
# can be removed manually.
```

## Configuration

The mbat configuration is located at `~/.config/mbat/mbat.conf`. An example
configuration file could look like this:

```
# Example configuration file. Save a similar file to
# ~/.config/mbat/mbat.conf for specific configuration.

[DEFAULT]
    # Uncomment and adjust these lines to run a filter on the
    # plain text of outgoing emails. This allows convenient
    # sending of text/plain and text/html multipart messages
    # by simply writing the body in markdown.
  ; use_alt_html_filter = false
  ; alt_html_filter = pandoc -f html -t markdown

[account.myself]
    # Every account that is to be used for sending emails
    # needs to be configured in its own section. The section
    # name does not matter.  There needs to be some section
    # containing a valid from_address, however. Only the
    # address part is matched. Specifying a display name is
    # optional and doesn't change program behaviour.
    from_address = My Self <my@self.net>
    sendmail = sendmail -t
    post_sendmail = notmuch insert -inbox -unread +sent
```

There are also two optional configuration files for `mbat.template`
and `mbat.content` located at `~/.config/mbat/default.template` and
`~/.config/mbat/default.content`. If those files exist, they will
override the defaults included in `mbat init`.

## Author

Frank Seifferth <frankseifferth@posteo.net>. Feel free to contact me
with feedback or suggestions.
