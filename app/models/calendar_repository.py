from __future__ import annotations

from datetime import date, datetime, time, timedelta
from app.models.appointment import Appointment

OL_FOLDER_CALENDAR = 9
OL_APPOINTMENT_ITEM = 1


class CalendarConnectionError(Exception):
    """Outlook não disponível ou calendário inacessível."""


class CalendarRepository:
    """Acesso ao calendário padrão do Windows via Outlook COM."""

    def __init__(self) -> None:
        self._outlook = None
        self._namespace = None
        self._calendar_folder = None

    def connect(self) -> None:
        try:
            import win32com.client
        except ImportError as exc:
            raise CalendarConnectionError(
                "Instale pywin32: pip install pywin32"
            ) from exc

        try:
            self._outlook = win32com.client.Dispatch("Outlook.Application")
            self._namespace = self._outlook.GetNamespace("MAPI")
            self._calendar_folder = self._namespace.GetDefaultFolder(OL_FOLDER_CALENDAR)
        except Exception as exc:
            raise CalendarConnectionError(
                "Não foi possível conectar ao Outlook. "
                "Verifique se o Microsoft Outlook ou o app Calendário "
                "está configurado com uma conta."
            ) from exc

    def list_appointments(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Appointment]:
        self._ensure_connected()

        start_date = start_date or date.today()
        end_date = end_date or (start_date + timedelta(days=30))
        range_start = datetime.combine(start_date, time.min)
        range_end = datetime.combine(end_date + timedelta(days=1), time.min)

        items = self._calendar_folder.Items
        items.IncludeRecurrences = True
        items.Sort("[Start]")

        appointments: list[Appointment] = []
        self._collect_in_range(items, range_start, range_end, appointments)
        appointments.sort(key=lambda a: a.start)
        return appointments

    def _collect_in_range(
        self,
        items,
        range_start: datetime,
        range_end: datetime,
        appointments: list[Appointment],
        max_scan: int = 10_000,
    ) -> None:
        try:
            total = int(items.Count)
        except Exception:
            total = -1

        if total <= 0 or total >= 2_000_000_000:
            total = max_scan

        for index in range(1, total + 1):
            try:
                item = items.Item(index)
            except Exception:
                break
            try:
                start = self._parse_com_datetime(item.Start)
                if start >= range_end:
                    break
                end = self._parse_com_datetime(item.End)
                if end < range_start:
                    continue
                appointments.append(self._to_appointment(item))
            except Exception:
                continue

    def create(self, appointment: Appointment) -> Appointment:
        self._ensure_connected()
        item = self._calendar_folder.Items.Add(OL_APPOINTMENT_ITEM)
        self._apply_to_item(item, appointment)
        item.Save()
        return self._to_appointment(item)

    def update(self, appointment: Appointment) -> Appointment:
        self._ensure_connected()
        item = self._namespace.GetItemFromID(appointment.entry_id)
        self._apply_to_item(item, appointment)
        item.Save()
        return self._to_appointment(item)

    def delete(self, entry_id: str) -> None:
        self._ensure_connected()
        item = self._namespace.GetItemFromID(entry_id)
        item.Delete()

    def get_by_id(self, entry_id: str) -> Appointment:
        self._ensure_connected()
        item = self._namespace.GetItemFromID(entry_id)
        return self._to_appointment(item)

    def _ensure_connected(self) -> None:
        if self._calendar_folder is None:
            self.connect()

    def _apply_to_item(self, item, appointment: Appointment) -> None:
        item.Subject = appointment.subject or "(Sem título)"
        item.Location = appointment.location or ""
        item.Body = appointment.body or ""
        item.AllDayEvent = appointment.all_day

        if appointment.all_day:
            item.Start = self._com_datetime(appointment.start.date(), time.min)
            item.End = self._com_datetime(
                appointment.end.date() + timedelta(days=1), time.min
            )
        else:
            item.Start = self._com_datetime(appointment.start)
            item.End = self._com_datetime(appointment.end)

    def _com_datetime(
        self, value: date | datetime, hour: time | None = None
    ) -> datetime:
        if isinstance(value, datetime):
            return value.replace(second=0, microsecond=0)
        if hour is not None:
            return datetime.combine(value, hour).replace(second=0, microsecond=0)
        return datetime.combine(value, time.min).replace(second=0, microsecond=0)

    def _to_appointment(self, item) -> Appointment:
        start = self._parse_com_datetime(item.Start)
        end = self._parse_com_datetime(item.End)
        all_day = bool(getattr(item, "AllDayEvent", False))

        if all_day and end.date() > start.date():
            end = datetime.combine(end.date() - timedelta(days=1), time(23, 59))

        return Appointment(
            entry_id=str(item.EntryID),
            subject=str(item.Subject or ""),
            start=start,
            end=end,
            location=str(item.Location or ""),
            body=str(item.Body or ""),
            all_day=all_day,
        )

    @staticmethod
    def _parse_com_datetime(value) -> datetime:
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        if hasattr(value, "year"):
            return datetime(
                value.year,
                value.month,
                value.day,
                getattr(value, "hour", 0),
                getattr(value, "minute", 0),
                getattr(value, "second", 0),
            )
        return datetime.fromisoformat(str(value)).replace(tzinfo=None)
