#!/usr/bin/env python3
#
# Usage: prepare.py [--clean]

import yaml
import re
import sys
import os
import shutil

def read_content(content: str) -> list:
    content = list(yaml.safe_load_all(content))
    return content

def get_vars(template: str):
    return re.findall("{(.*?)}", template, re.DOTALL)

def validate_content(content: list, template_vars: list) -> None:
    err = list()
    def mkerr(item: int, key: str):
        return f"Error in mbat.content, item {item}: " + \
               f"'{key}' is not defined"
    for i, item in enumerate(content, 1):
        if "id" not in item:
            err.append(mkerr(i, "id"))
        for key in template_vars:
            if key not in item.keys():
                err.append(i, key)
    if err:
        raise Exception("\n".join(err))

def get_atts(template: str) -> tuple:
    def extract_pages(pages: str) -> list:
        ranges = re.split(",", pages)
        pages = list()
        for r in ranges:
            if re.fullmatch("[0-9]+-[0-9]+", r):
                f, t = re.fullmatch("([0-9]+)-([0-9]+)", r).groups()
                f, t = int(f), int(t)
                if f <= t:
                    pages.extend(range(f, t+1))
                else:
                    pages.extend(range(f, t-1))
            else:
                pages.append(int(i))
        return pages
    def match_with_pages(line: str):
        match = re.fullmatch(r"!\[(.+?)\]\((.+?):([0-9,-]*)\)\s*", line)
        if match:
            return {
                "newname": match.groups()[0],
                "oldname": match.groups()[1],
                "pages": extract_pages(match.groups()[2]),
            }
    def match_no_pages(line: str):
        match = re.fullmatch(r"!\[(.+?)\]\((.+?)\)\s*", line)
        if match:
            return {
                "newname": match.groups()[0],
                "oldname": match.groups()[1],
                "pages": list(),
            }
    atts = list()
    content = list()
    for line in template.splitlines():
        if match_with_pages(line):
            atts.append(match_with_pages(line))
        elif match_no_pages(line):
            atts.append(match_no_pages(line))
        else:
            content.append(line)
    content = "\n".join(content)
    content = re.sub("(\s*\n)*$", "", content) + "\n"
    return (content, atts)

def clean_up():
    try:
        oldids = map(
            lambda filename: re.sub(r"\.mail$", "", filename),
            filter(
                lambda filename: filename.endswith(".mail"),
                os.listdir()
            )
        )
        for i in oldids:
            if os.path.isdir(i): shutil.rmtree(i)
            os.remove(f"{i}.mail")
    except Exception as e:
        raise Exception(f"Failed to remove old files: {e}") from e

if __name__ == "__main__":
    try:
        clean_up()
        if "--clean" in sys.argv:
            exit(0)
        with open("mbat.template") as f:
            template = f.read()
        vs = get_vars(template)
        with open("mbat.content") as f:
            content = read_content(f.read())
        if not content:
            raise Exception("No entries in 'mbat.content'")
        validate_content(content, vs)
        for i, item in enumerate(content, 1):
            with open(f"{item['id']}.mail", "w") as f:
                content = template.format(**item)
                content, atts = get_atts(template.format(**item))
                f.write(content)
                if atts: os.makedirs(item["id"], exist_ok=True)
                for a in atts:
                    newname = os.path.join(item["id"], a["newname"])
                    if not a["pages"]:
                        shutil.copy(a["oldname"], newname)
                    else:
                        raise Exception(
                            "Error: Page extraction not implemented yet"
                        )
    except Exception as e:
        raise e     #!DEBUG-ONLY
        print(e, file=sys.stdout)
        exit(1)
