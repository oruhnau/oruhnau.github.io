#!/usr/bin/env python3
"""Rewrite the "Recent publications:" block of classic-Outlook signature files.

Usage:
    python update_signature.py entries.json SIGNATURE_BASE [SIGNATURE_BASE ...]

SIGNATURE_BASE is a path without extension, e.g.
    ".../Signatures/Uni Köln (ruhnau@wiso.uni-koeln.de)"
and <base>.htm, <base>.rtf and <base>.txt are rewritten in place.

entries.json: list (newest first) of objects with
    authors  - list of "Surname, X." strings, full list
    year     - e.g. "2026"
    title
    url
    venue    - journal or series, e.g. "Energy Policy", "EWI Working Paper"

Formatting: "Authors, year. Title. Venue." Title bold and linked, venue italic,
own name NOT bold. More than 7 authors -> first max(3, own position) + "et al."
Everything between the "Recent publications:" heading and the trailing empty
paragraph is replaced; the rest of each file is left byte-for-byte unchanged.
"""

import html
import json
import re
import sys

OWN_NAME = "Ruhnau, O."
MAX_AUTHORS = 7


def author_string(names):
    names = list(names)
    et_al = False
    if len(names) > MAX_AUTHORS:
        keep = max(3, names.index(OWN_NAME) + 1 if OWN_NAME in names else 3)
        if keep < len(names):
            names, et_al = names[:keep], True
    return ", ".join(names) + (", et al." if et_al else "")


def title_punct(title):
    return "" if title.rstrip()[-1:] in "?!." else "."


# ---------------------------------------------------------------- HTML
def html_text(s):
    out = []
    for ch in html.escape(s, quote=False):
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            out.append(f"&#{ord(ch)};")
    return "".join(out)


def html_entry(e):
    return (
        "<p class=xmsonormal style='margin-top:3.0pt;margin-right:0cm;margin-bottom:\r\n"
        "6.0pt;margin-left:21.3pt'><span style='font-size:9.0pt;font-family:\"Calibri Light\",sans-serif'>"
        f"{html_text(author_string(e['authors']))}, {html_text(e['year'])}. </span><span style='font-size:9.0pt'><a\r\n"
        f"href=\"{html.escape(e['url'])}\"><b><span lang=EN-US\r\n"
        f"style='mso-ansi-language:EN-US'>{html_text(e['title'])}</span></b></a></span><span\r\n"
        "lang=EN-US style='font-size:9.0pt;font-family:\"Calibri Light\",sans-serif;mso-ansi-language:\r\n"
        f"EN-US'>{title_punct(e['title'])} <i>{html_text(e['venue'])}</i>.</span><span\r\n"
        "style='font-size:9.0pt'><o:p></o:p></span></p>\r\n\r\n"
    )


def update_html(path, entries):
    data = open(path, "rb").read().decode("cp1252")
    head = data.index("Recent publications:")
    start = data.index("</p>", head) + len("</p>")
    # skip blank lines after the heading paragraph
    while data[start] in "\r\n":
        start += 1
    tail_marker = "<o:p>&nbsp;</o:p></span></p>"
    end = data.rindex("<p class=", start, data.index(tail_marker, start) + 1)
    new = data[:start] + "".join(html_entry(e) for e in entries) + data[end:]
    open(path, "wb").write(new.encode("cp1252"))


# ---------------------------------------------------------------- RTF
def rtf_text(s):
    out = []
    for ch in s:
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ord(ch) < 128:
            out.append(ch)
        else:
            try:
                out.append("\\'%02x" % ch.encode("cp1252")[0])
            except UnicodeEncodeError:
                out.append("\\u%d?" % (ord(ch) if ord(ch) < 32768 else ord(ch) - 65536))
    return "".join(out)


RTF_PARA = r"\pard \ltrpar\s18\ql \li426\ri0\sb60\sa120\widctlpar\wrapdefault\aspalpha\aspnum\faauto\adjustright\rin0\lin426\itap0 "
RTF_LIGHT = r"{\rtlch\fcs1 \af38\afs18 \ltrch\fcs0 \f38\fs18\lang1033\langfe1031\langnp1033 \hich\af38\dbch\af31505\loch\f38 "
RTF_ITALIC = r"{\rtlch\fcs1 \ai\af38\afs18 \ltrch\fcs0 \i\f38\fs18\lang1033\langfe1031\langnp1033 \hich\af38\dbch\af31505\loch\f38 "
RTF_PAR_END = "{\\rtlch\\fcs1 \\af37\\afs18 \\ltrch\\fcs0 \\fs18 \r\n\\par }"


def rtf_entry(e):
    return (
        RTF_LIGHT + rtf_text(f"{author_string(e['authors'])}, {e['year']}. ") + "}"
        + r"{\field{\*\fldinst {\rtlch\fcs1 \af37\afs18 \ltrch\fcs0 \fs18 HYPERLINK \"" + rtf_text(e["url"]) + r"\" }}"
        + r"{\fldrslt {\rtlch\fcs1 \ab\af37\afs18 \ltrch\fcs0 \cs17\b\fs18\ul\cf19\lang1033\langfe1031\langnp1033 \hich\af37\dbch\af31505\loch\f37 "
        + rtf_text(e["title"]) + "}}}\r\n"
        + RTF_LIGHT + rtf_text(title_punct(e["title"]) + " ") + "}"
        + RTF_ITALIC + rtf_text(e["venue"]) + "}"
        + RTF_LIGHT + ".}"
        + RTF_PAR_END
    )


def update_rtf(path, entries):
    data = open(path, "rb").read().decode("latin-1")
    head = data.index("Recent publications:")
    start = data.index("\\par }", head) + len("\\par }")
    theme = data.index("{\\*\\themedata", start)
    # the trailing empty paragraph is the last group before \themedata
    end = data.rindex("{\\rtlch", start, data.rindex("\\par }", start, theme))
    new = data[:start] + RTF_PARA + "".join(rtf_entry(e) for e in entries) + data[end:]
    open(path, "wb").write(new.encode("latin-1"))


# ---------------------------------------------------------------- TXT
def update_txt(path, entries):
    data = open(path, "rb").read().decode("utf-16")
    head = data.index("Recent publications:")
    start = data.index("\r\n", head) + 2
    lines = [
        f"{author_string(e['authors'])}, {e['year']}. {e['title']}{title_punct(e['title'])} {e['venue']}.\r\n"
        for e in entries
    ]
    new = data[:start] + "".join(lines) + "\r\n"
    open(path, "wb").write(new.encode("utf-16"))  # little-endian with BOM on Windows/Linux x86


def main():
    entries = json.load(open(sys.argv[1], encoding="utf-8"))
    assert 1 <= len(entries) <= 3, "signature holds at most 3 entries"
    for base in sys.argv[2:]:
        update_html(base + ".htm", entries)
        update_rtf(base + ".rtf", entries)
        update_txt(base + ".txt", entries)
        print("updated", base)


if __name__ == "__main__":
    main()
