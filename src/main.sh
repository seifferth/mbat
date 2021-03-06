#!/bin/bash
set -e

init() {
#include init.sh $@
echo "It looks like you're running a non-compiled version " \
     "of mbat that doesn't include init.sh." | fmt >&2
exit 120
#endinclude
}

prepare() {
#include prepare.py $@
echo "It looks like you're running a non-compiled version " \
     "of mbat that doesn't include prepare.py." | fmt >&2
exit 120
#endinclude
}

send() {
ls *.mail|sed 's,\.mail$,,g'|while read -r f; do
printf "Sending $f.mail ..."
#include send.py "$f" send store
echo "It looks like you're running a non-compiled version " \
     "of mbat that doesn't include send.py." | fmt >&2
exit 120
#endinclude
test -d "$f" && rm -r "$f"
rm "$f.mail"
printf " OK\n"
done
}

clean() {
prepare --clean
}

help() {
cat <<EOF
Usage: mbat <command> [directory]

Commands:
    init    Initialize a new batch by copying example 'mbat.template' and
            'mbat.content' files into the specified directory.
    prep    Prepare mails by expanding the template into mutliple '*.mail'
            files and attachment directories.
    send    Send out expanded emails. 'mbat prep' needs to be executed
            first. Once sent, the prepared '*.mail' files and attachment
            directories will be deleted.
    clean   Remove expanded mails and attachment directories.
    help    Print this help message and exit.

EOF
}

if test "$#" -lt 1 || test "$#" -gt 2; then
    help >&2
    exit 1
fi

try_cd() {
test "$1" && dir="$1" || dir="."
if test -d "$dir"; then
    cd "$dir"
else
    echo "No such directory: '$dir'" >&2
    exit 1
fi
}

# Parse main argument
case "$1" in
    "init")
        init "$2"
        ;;
    "prep")
        try_cd "$2"
        prepare
        ;;
    "send")
        try_cd "$2"
        send
        ;;
    "clean")
        try_cd "$2"
        clean
        ;;
    "help"|"--help"|"-h")
        help >&1
        ;;
    *)
        help >&2
        exit 1
        ;;
esac
