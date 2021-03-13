#!/bin/bash
set -e

init() {
#include init.sh $@
echo "It looks like you're running a non-compiled version " \
     "of mailbatch that doesn't include init.sh." | fmt >&2
exit 120
#endinclude
}

prepare() {
#include prepare.py $@
echo "It looks like you're running a non-compiled version " \
     "of mailbatch that doesn't include prepare.py." | fmt >&2
exit 120
#endinclude
}

send() {
echo "Send not implemented yet" >&2
exit 1
}

clean() {
prepare --clean
}

help() {
cat <<EOF
Usage: mailbatch <command> [directory]

Commands:
  init      Initialize a new batch by copying example
            'mailbatch.template' and 'mailbatch.config'
            files into the specified directory.
  prepare   Expand template into mutliple mails and attachment
            directories.
  send      Send out expanded emails. 'mailbatch prepare' needs
            to be run first.
  clean     Remove expanded mails and attachment directories.
  help      Print this help message and exit.

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
    "prepare")
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
