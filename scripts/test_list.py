from datetime import date, datetime, timedelta

from app.models.appointment import Appointment
from app.models.calendar_repository import CalendarRepository

r = CalendarRepository()
r.connect()

start = datetime.now() + timedelta(days=1)
appt = Appointment("", "Teste parse COM", start, start + timedelta(hours=1))
created = r.create(appt)

items = r._calendar_folder.Items
items.IncludeRecurrences = True
items.Sort("[Start]")

start_date = date.today()
end_date = start_date + timedelta(days=30)
restriction = (
    f"[Start] >= '{start_date.strftime('%m/%d/%Y')}' "
    f"AND [Start] < '{(end_date + timedelta(days=1)).strftime('%m/%d/%Y')}'"
)
print("Restriction:", restriction)

try:
    filtered = items.Restrict(restriction)
    print("Restrict count:", filtered.Count)
except Exception as e:
    print("Restrict error:", e)
    filtered = items

errors = 0
found_test = False
for item in filtered:
    try:
        a = r._to_appointment(item)
        if "Teste parse" in a.subject:
            found_test = True
            print("OK:", a.subject, a.start, "raw Start type:", type(item.Start))
    except Exception as e:
        errors += 1
        print("Parse error:", getattr(item, "Subject", None), e)

print("found_test:", found_test, "parse_errors:", errors)

listed = r.list_appointments(start_date, end_date)
print("list_appointments count:", len(listed))
print("test in list:", any("Teste parse" in a.subject for a in listed))

r.delete(created.entry_id)
