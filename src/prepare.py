#!/usr/bin/env python3
#
# Usage: prepare.py [--clean]

import yaml
import re
import sys
import os
import shutil
from PyPDF2 import PdfFileMerger

def pdf_pages(pdf: str, pages: list) -> PdfFileMerger:
    merger = PdfFileMerger()
    for p in pages:
        if p < 1:
            raise Exception(
                f"Pdf page {p} is too low. Page numbering starts with 1."
            )
        merger.append(pdf, pages=(p-1,p))
    return merger

def read_content(content: str) -> list:
    content = list(filter(lambda x: x != None, yaml.safe_load_all(content)))
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

def get_atts(mail: str) -> tuple:
    def extract_pages(pages: str) -> list:
        if not pages or pages.strip().lower() in ("", "none"):
            return "none"
        elif pages.strip().lower() == "all":
            return "all"
        if not re.fullmatch("[0-9,-]+", pages):
            raise Exception(
                f"Error: Invalid page range: '{pages}'"
            )
        pages = re.sub(r"\s", "", pages)
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
                pages.append(int(r))
        return pages
    def match_with_pages(line: str):
        match = re.fullmatch(r"!\[(.+?)\]\((.+?):(.*)\)\s*", line)
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
                "pages": "all"
            }
    atts = list()
    content = mail
    refs = re.findall(r"(\s*\n)+(!\[.*\]\(.*\))(\s*\n)+", mail)
    for i, r in enumerate(refs, 1):
        if match_with_pages(r[1]):
            atts.append(match_with_pages(r[1]))
        elif match_no_pages(r[1]):
            atts.append(match_no_pages(r[1]))
        else:
            raise Exception(
                f"Error while processing attachment reference {i}."
            )
        whitespace = "\n" * max(
            len(re.findall("\n", r[0])),
            len(re.findall("\n", r[2])),
        )
        content = content.replace(r[0]+r[1]+r[2], whitespace)
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
            template = f.read() + "\n"
        vs = get_vars(template)
        with open("mbat.content") as f:
            content = read_content(f.read() + "\n")
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
                    if a["pages"] == "all":
                        shutil.copy(a["oldname"], newname)
                    elif a["pages"] == "none":
                        pass
                    else:
                        merger = pdf_pages(a["oldname"], a["pages"])
                        merger.write(newname)
                        merger.close()
    except Exception as e:
        raise e     #!DEBUG-ONLY
        print(e, file=sys.stderr)
        exit(1)
