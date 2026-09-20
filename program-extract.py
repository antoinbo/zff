#!/usr/bin/env python3

import re

from datetime import datetime
from icalendar import Calendar, Event
from uuid import UUID, uuid5

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
if len(unmatched):
    print("```")
    for line in unmatched:
        print(line)
    print("```")
else:
    print("All playtimes parsed successfully!")

# Create iCalendar file (.ics)
calendar = Calendar()
calendar.summary = "Zürich Film Festival 2026 program"

for playtime in playtimes:
    date = datetime.strptime(playtime.get("date", "00.00.0000"), "%d.%m.%Y")
    begin = datetime.strptime(playtime.get("begin", "00:00"), "%H:%M")
    end = datetime.strptime(playtime.get("end", "00:00"), "%H:%M")

    event = Event()
    event.uid = uuid5(UUID(int=0), "_".join([playtime.get("date", "00.00.0000"), playtime.get("begin", "00:00"), playtime.get("film").replace(" ", "-")]))
    event.summary = playtime.get("film")
    event.set_start(datetime.combine(date, begin.time()))
    event.set_end(datetime.combine(date, end.time()))
    event.location = playtime.get("location")

    event["description"] = f"""# {playtime.get("film")}
Section {playtime.get("section")}.
Language {", ".join(playtime.get("language"))}, subtitles {", ".join(playtime.get("subtitles"))}.
At {playtime.get("location")}.
On {playtime.get("date")} at {playtime.get("begin")}, ending at {playtime.get("end")}.
Duration {playtime.get("minutes")} minutes.
"""

    calendar.add_component(event)

with open("zff-2026_program.ics", "wb") as fp:
    fp.write(calendar.to_ical())
