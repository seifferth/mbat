#!/usr/bin/env python3
#
# Usage send.py <name> [store|send|dump]
#
# Where <name>.mail is a plain-text email-like file and <name>/ is an
# optional directory containing attachments (if desired)
#
# Options:
#   store   Call the command specified as post_sendmail in
#           ~/.config/mbat/mbat.conf
#   send    Call the command specified as sendmail in
#           ~/.config/mbat/mbat.conf
#   dump    Dump resulting email to stdout (useful for debugging)
#
# Multiple options can be specified at the same time

import sys, os, subprocess, mimetypes
from pathlib import Path
from configparser import ConfigParser
from email.parser import Parser
from email.message import EmailMessage
from email.utils import parseaddr, formatdate

def bundle_mail(name: str) -> (EmailMessage, str):
    with open(f"{name}.mail") as f:
        user_input = Parser().parse(f)
    mail = EmailMessage()
    for key in user_input.keys():
        if user_input.get(key):
            mail.add_header(key, user_input.get(key))
    if "Date" not in user_input:
        mail.add_header("Date", formatdate(localtime=True))
    plain_body = user_input.get_payload()
    mail.set_content(plain_body)
    if os.path.isdir(name):
        for a in os.listdir(name):
            with open(os.path.join(name, a), "rb") as f:
                data = f.read()
            mime, _ = mimetypes.guess_type(a)
            if not mime: mime = "application/octet-stream"
            maintype, subtype = mime.split("/", 1)
            mail.add_attachment(
                data, filename=a,
                maintype=maintype, subtype=subtype,
            )
    return (mail, plain_body)

def run_command(command: str, stdin: bytes) -> None:
    subprocess.run(command, input=stdin, shell=True, check=True)

def run_filter(command: str, stdin: str) -> str:
    return subprocess.check_output(
        command, input=stdin, shell=True, text=True
    )

def read_config(conf_file: str, sender: str) -> dict:
    config = ConfigParser()
    config.read(conf_file)
    for sec in config.sections():
        if parseaddr(config[sec].get("from_address"))[1] == sender:
            section = config[sec]
            break
    else:
        raise Exception(
            f"Unable to find a section in {conf_file} which contains " + \
            f"'from_address = {sender}' "
        )
    return {
        "sendmail":
            section.get("sendmail", "sendmail -t"),
        "post_sendmail":
            section.get(
                "post_sendmail",
                "notmuch insert --folder=Sent -inbox -unread +sent"
            ),
        "use_alt_html_filter":
            section.getboolean("use_alt_html_filter", False),
        "alt_html_filter":
            section.get("alt_html_filter", "pandoc -f markdown -t html"),
    }

if __name__ == "__main__":
    try:
        name = sys.argv[1]
        mail, plain_body = bundle_mail(name)
        sender = mail.get("From").addresses[0].addr_spec

        conf_file = os.path.join(Path.home(), ".config", "mbat", "mbat.conf")
        if "send" in sys.argv or "store" in sys.argv \
        or os.path.isfile(conf_file):
            config = read_config(conf_file, sender)
        else:
            config = dict()

        if config.get("use_alt_html_filter"):
            html = run_filter(
                config.get("alt_html_filter"),
                plain_body,
            )
            if html.strip():
                mail.get_body().add_alternative(html, subtype="html")

        if "dump" in sys.argv:
            run_command("cat", mail.as_bytes())
        if "send" in sys.argv:
            run_command(config["sendmail"], mail.as_bytes())
        if "store" in sys.argv:
            run_command(config["post_sendmail"], mail.as_bytes())
    except Exception as e:
        raise e     #!DEBUG-ONLY
        print(e, file=sys.stderr)
        exit(1)
