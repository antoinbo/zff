#!/usr/bin/env python3

import re

# https://www.datocms-assets.com/152459/1788949025-zff26_filmplanung.pdf
# | Film | Datum | Beginn | Ende | Film Länge | Location | Sektion | Sprache | Untertitel |
RE_PROGRAM_LINE = re.compile(r"^(?P<film>.+) (?P<date>\d{2}\.\d{2}\.\d{4}) (?P<begin>\d{2}:\d{2}) (?P<end>\d{2}:\d{2}) (?P<minutes>\d+|-) (?P<location>Arena \d|Arthouse (?:Le Paris|Piccadilly)|Corso \d|Filmpodium|KINOKONI \d|Kongresssaal) ?(?P<section>Hashtag #artificialintelligence|Gala Premieren|NOW/FUTURE|Retrospektive: Richard Linklater|Signatures|Special Screenings|Sounds|(?:Dokumentar|Spiel)film-Wettbewerb|ZFF (?:für (?:Kinder|Schulen)|Genuss Film)|) ?(?P<language>\w+(?:, \w+)*(?: live eingesprochen| \(Synchronfassung\)?)?|) ?(?P<subtitles>\w{2}(?:, \w{2})*|)$")

films = set()
playtimes = list()
matched, unmatched = [], []
matched_count, unmatched_count = 0, 0

with open("zff-2026_program.txt", encoding="utf8") as fp:
    for line in fp.readlines():
        line = line.strip()

        if line.startswith("#"):
            continue

        result = RE_PROGRAM_LINE.match(line)

        if result:
            matched.append(line)
            matched_count = matched_count + 1

            playtime = {
                "film": result.group("film"),
                "date": result.group("date"),
                "begin": result.group("begin"),
                "end": result.group("end"),
                "minutes": result.group("minutes"),
                "location": result.group("location"),
                "section": result.group("section"),
                "language": [language.strip() for language in result.group("language").split(",")],
                "subtitles": [subtitle.strip() for subtitle in result.group("subtitles").split(",")]
            }

            films.add(playtime.get("film"))
            playtimes.append(playtime)
        else:
            unmatched.append(line)
            unmatched_count = unmatched_count + 1

print("# Program")
print(f"Script result: {matched_count:d} playtimes parsed and {unmatched_count:d} failed.")

print("## Films")
for film in sorted(films):
    print("* " + film)

print("## Playtimes")
print("| Film | Date | Begin | End | Duration | Location | Section | Language | Subtitles |")
print("| ---- | ---- | ----- | --- | -------- | -------- | ------- | -------- | --------- |")
for playtime in playtimes:
    print(f"| {playtime.get("film")} | {playtime.get("date")} | {playtime.get("begin")} | {playtime.get("end")} | {playtime.get("minutes")}' | {playtime.get("location")} | {playtime.get("section")} | {", ".join(playtime.get("language"))} | {", ".join(playtime.get("subtitles"))} |")

print("## Failed to parse")
if len(line):
    print("```")
    for line in unmatched:
        print(line)
    print("```")
else:
    print("All playtimes parsed successfully!")
