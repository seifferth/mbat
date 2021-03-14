#!/bin/bash
#
# Usage: init.sh [dir]

set -e

test "$#" -gt 0 && dir="$1" || dir="."
test -d "$dir" || mkdir "$dir"
cd "$dir"
if test "$(ls -A .|wc -l)" -gt 0; then
    echo "Error: Directory '$dir' is not empty" >&2
    exit 1
fi

if test -f "~/.config/mbat/default.template"; then
cat "~/.config/mbat/default.template" > mbat.template
else
cat <<EOF > mbat.template
From: Someone <sender@e.mail>
To: {name} <{email}>
Cc:
Bcc:
Subject:
Reply-To:
In-Reply-To:

The email body goes here. You can add variables like {id} or {name}
anywhere in the body. You can also use them in attachments. Attachments
are specified as follows:

![filename_the_recipient_sees.pdf](file_on_disk.pdf)

To use a variable in an attachment, simply specify it:

![file_for_{id}.pdf](file_on_disk.pdf)

If the attached file is a pdf document, mbat allows you to specify
a page range by appending a colon to the filename. The specific page
range can optionally be passed in using a variable in mbat.content:

![pages_{pages}.pdf](file_on_disk.pdf:{pages})

The page specification must be of the following form:

1. A single page as a literal. E. g. 10
2. A page range. E. g. 5-8
3. Multiple single pages or page ranges separated by commas.
   E. g. 5-8,10,12-15
4. The special keyword 'all' or the special keyword 'none'. These
   keywords cannot be combined with anything. Note that, instead of
   specifying 'all', you can also simply omit the page specification
   all together. Including only a trailing colon after the filename
   is equivalent to specifying 'none'.
EOF
fi

if test -f "~/.config/mbat/default.content"; then
cat "~/.config/mbat/default.content" > mbat.content
else
cat <<EOF > mbat.content
# The content is written in yaml format. You can include comments
# by prefixing lines with an octothorp (like these). To add more
# recipients, simply add another dashed line below like the one
# you see between recipients one and two.
#
# Note that the 'id' field is mandatory and should not contain any
# whitespace characters. It must also be unique. All other fields
# are optional and can contain whitespace without issues.
#
id: recipient_one
name: Recipient One
email: recipi@ent.one
---
id: recipient_two
name: Recipient Two
email: second@recipi.ent
EOF
fi
