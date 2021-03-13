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

if test -f "~/.config/mailbatch/default.template"; then
cat "~/.config/mailbatch/default.template" > mailbatch.template
else
cat <<EOF > mailbatch.template
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
EOF
fi

if test -f "~/.config/mailbatch/default.config"; then
cat "~/.config/mailbatch/default.config" > mailbatch.config
else
cat <<EOF > mailbatch.config
id: recipient_one
name: Recipient One
email: recipi@ent.one
---
id: recipient_two
name: Recipient Two
email: second@recipi.ent
# The config is written in yaml format. You can include comments
# by prefixing lines with an octothorp (like these). To add more
# recipients, simply add another dashed line below like the one
# you see between recipients one and two.
EOF
fi
