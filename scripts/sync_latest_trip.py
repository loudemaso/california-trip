from pathlib import Path
import re

index = Path("index.html")
text = index.read_text()

# Add a single consistent green style for every completed booking.
if ".pill.confirmed{" not in text:
    text = text.replace(
        ".pill.reservation{background:#fff0e4;color:#8d512e;border-color:#f1d2bc}",
        ".pill.reservation{background:#fff0e4;color:#8d512e;border-color:#f1d2bc}.pill.confirmed{background:#e8f4eb;color:#237a43;border-color:#c9e4d2}",
        1,
    )

# New confirmations since the previous HTML sync.
cave_old = '<a class="pill reservation" href="https://oakmountainwinery.com/cave-restaurant/" target="_blank" rel="noopener">Reservation required · 12:30 PM lunch target · reserve an indoor Cave Restaurant table for two · Thursday 12:00–8:00 PM · 951-699-9102</a>'
cave_new = '<a class="pill confirmed" href="https://oakmountainwinery.com/cave-restaurant/" target="_blank" rel="noopener">✅ Reservation confirmed · Thu Sep 17 · 12:30 PM · 2 guests · standard seating · 951-699-9102</a>'
if cave_old in text:
    text = text.replace(cave_old, cave_new, 1)
elif cave_new not in text:
    raise SystemExit("Could not locate Cave Restaurant status")

noches_old = '<a class="pill ticket" href="https://altisimawinery.com/events/noches-latin-jazz/" target="_blank" rel="noopener">Tickets required · Thu Sep 17 · 6:30–9:30 PM · $25/person published admission · limited seating · non-refundable · 951-422-2525</a>'
noches_new = '<a class="pill confirmed" href="https://altisimawinery.com/events/noches-latin-jazz/" target="_blank" rel="noopener">✅ TICKETS PURCHASED · Thu Sep 17 · 6:30–9:30 PM · 2 guests · 951-422-2525</a>'
if noches_old in text:
    text = text.replace(noches_old, noches_new, 1)
elif noches_new not in text:
    raise SystemExit("Could not locate Noches de Altísima status")

# Normalize all existing completed reservation / booking pills.
confirmed = re.compile(r'<a class="pill reservation"([^>]*)>(?:✅\s*)?(Reservation confirmed|BOOKED)([^<]*)</a>')
text = confirmed.sub(lambda m: f'<a class="pill confirmed"{m.group(1)}>✅ {m.group(2)}{m.group(3)}</a>', text)

required = [
    "✅ Reservation confirmed · Tue Sep 15 · 8:30 PM · 2 guests · outdoor seating",
    "✅ Reservation confirmed · Wed Sep 16 · 6:30 PM · 2 guests · standard dining-room seating",
    "✅ Reservation confirmed · Wed Sep 16 · 8:30 PM · 2 guests · outdoor heated-patio seating",
    "✅ Reservation confirmed · Thu Sep 17 · 12:30 PM · 2 guests · standard seating",
    "✅ TICKETS PURCHASED · Thu Sep 17 · 6:30–9:30 PM · 2 guests",
    "✅ BOOKED · Fri Sep 18 · 2:35 PM pickup · 2 Cruiser Bikes",
    "✅ Reservation confirmed · Fri Sep 18 · 7:15 PM · 2 guests · standard seating",
    "✅ Reservation confirmed · Sat Sep 19 · 12:30 PM · 2 guests · standard seating",
    "✅ Reservation confirmed · Sat Sep 19 · 9:00 PM · 2 guests · table seating",
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"Missing expected completed booking: {marker}")

index.write_text(text)

# Keep the existing Notion-sync workflow from restoring stale Tue/Wed/Thu HTML.
source = Path(".github/workflows/update-thursday.yml")
s = source.read_text()

def extract_day(html, date_label, next_date_label):
    start_marker = f'<section class="day"><div class="dayhead"><div><div class="date">{date_label}</div>'
    next_marker = f'<section class="day"><div class="dayhead"><div><div class="date">{next_date_label}</div>'
    start = html.find(start_marker)
    end = html.find(next_marker, start)
    if start == -1 or end == -1:
        raise SystemExit(f"Could not extract {date_label}")
    return html[start:end]

for var, date_label, next_label in [
    ("tuesday", "Tuesday · September 15", "Wednesday · September 16"),
    ("wednesday", "Wednesday · September 16", "Thursday · September 17"),
    ("thursday", "Thursday · September 17", "Friday · September 18"),
]:
    section = extract_day(text, date_label, next_label)
    marker = f"          {var} = '''"
    start = s.find(marker)
    if start == -1:
        raise SystemExit(f"Could not find {var} source assignment")
    body_start = start + len(marker)
    end = s.find("'''", body_start)
    if end == -1:
        raise SystemExit(f"Could not find end of {var} source assignment")
    s = s[:body_start] + section + s[end:]

audit_start = s.find("          must_have = [")
audit_end = s.find("          must_not_have = [", audit_start)
if audit_start == -1 or audit_end == -1:
    raise SystemExit("Could not find reservation audit block")

current_audit = '''          must_have = [
              'Scenic Highway 101 drive to Carlsbad + hotel check-in',
              'Balboa Park golden-hour wander',
              'Little Italy wander',
              'Allegro — Amalfi Lemon Sorbet',
              'Night Hawk — open-air Greek date night',
              '✅ Reservation confirmed · Tue Sep 15 · 8:30 PM · 2 guests · outdoor seating',
              'Wildland — rustic Italian date night',
              '✅ Reservation confirmed · Wed Sep 16 · 6:30 PM · 2 guests · standard dining-room seating',
              'Campfire — nightcap drinks + dessert',
              '✅ Reservation confirmed · Wed Sep 16 · 8:30 PM · 2 guests · outdoor heated-patio seating',
              'The Cave Restaurant at Oak Mountain — wine-country lunch',
              '✅ Reservation confirmed · Thu Sep 17 · 12:30 PM · 2 guests · standard seating',
              'Oak Mountain Cave Wine Tasting Tour',
              'Reservation required · 2:00 PM tour target',
              'Oak Mountain vineyard decompression',
              '✅ TICKETS PURCHASED · Thu Sep 17 · 6:30–9:30 PM · 2 guests',
              '✅ BOOKED · Fri Sep 18 · 2:35 PM pickup · 2 Cruiser Bikes',
              '✅ Reservation confirmed · Fri Sep 18 · 7:15 PM · 2 guests · standard seating',
              '✅ Reservation confirmed · Sat Sep 19 · 12:30 PM · 2 guests · standard seating',
              '✅ Reservation confirmed · Sat Sep 19 · 9:00 PM · 2 guests · table seating',
              'Ticket required · buy General Admission, not RSVP-only',
              'Reservation required · 2:15 PM target',
          ]
'''
s = s[:audit_start] + current_audit + s[audit_end:]
source.write_text(s)
