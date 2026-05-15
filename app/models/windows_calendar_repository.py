from __future__ import annotations

import asyncio
from datetime import date, datetime, time, timedelta

from app.models.appointment import Appointment

ENTRY_SEP = "|"


class CalendarConnectionError(Exception):
    """Calendário do Windows indisponível."""


class WindowsCalendarRepository:
    """CRUD no app Calendário do Windows via WinRT."""

    def __init__(self) -> None:
        self._store = None
        self._calendars: dict[str, object] = {}
        self._default_calendar = None

    def connect(self) -> None:
        try:
            self._run(self._connect_async())
        except ImportError as exc:
            raise CalendarConnectionError(
                "Instale as dependências: pip install -r requirements.txt"
            ) from exc
        except Exception as exc:
            raise CalendarConnectionError(
                "Não foi possível acessar o Calendário do Windows. "
                "Verifique se o app Calendário está configurado."
            ) from exc

    def list_appointments(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Appointment]:
        self._ensure_connected()
        start_date = start_date or date.today()
        end_date = end_date or (start_date + timedelta(days=30))
        span = (end_date - start_date).days + 1
        start_dt = datetime.combine(start_date, time.min)
        return self._run(self._list_async(start_dt, timedelta(days=max(span, 1))))

    def create(self, appointment: Appointment) -> Appointment:
        self._ensure_connected()
        return self._run(self._create_async(appointment))

    def update(self, appointment: Appointment) -> Appointment:
        self._ensure_connected()
        return self._run(self._update_async(appointment))

    def delete(self, entry_id: str) -> None:
        self._ensure_connected()
        self._run(self._delete_async(entry_id))

    def get_by_id(self, entry_id: str) -> Appointment:
        self._ensure_connected()
        return self._run(self._get_async(entry_id))

    async def _connect_async(self) -> None:
        from winrt.windows.applicationmodel.appointments import (
            AppointmentManager,
            AppointmentStoreAccessType,
        )

        self._store = await AppointmentManager.request_store_async(
            AppointmentStoreAccessType.ALL_CALENDARS_READ_WRITE
        )
        calendars = await self._store.find_appointment_calendars_async()
        self._calendars.clear()
        for cal in calendars:
            self._calendars[cal.local_id] = cal

        if not self._calendars:
            raise CalendarConnectionError("Nenhum calendário encontrado no Windows.")

        self._default_calendar = next(iter(self._calendars.values()))
        for cal in self._calendars.values():
            if cal.can_create_or_update_appointments:
                self._default_calendar = cal
                break

    async def _list_async(
        self, start_dt: datetime, span: timedelta
    ) -> list[Appointment]:
        items = await self._store.find_appointments_async(start_dt, span)
        appointments = [self._to_appointment(a) for a in items]
        appointments.sort(key=lambda a: a.start)
        return appointments

    async def _create_async(self, appointment: Appointment) -> Appointment:
        from winrt.windows.applicationmodel.appointments import Appointment as WinAppt

        cal = self._default_calendar
        win_appt = WinAppt()
        self._apply_to_win_appt(win_appt, appointment)
        await cal.save_appointment_async(win_appt)
        return self._to_appointment(win_appt, cal.local_id)

    async def _update_async(self, appointment: Appointment) -> Appointment:
        cal_id, appt_id = self._parse_entry_id(appointment.entry_id)
        cal = self._get_calendar(cal_id)
        win_appt = await cal.get_appointment_async(appt_id)
        self._apply_to_win_appt(win_appt, appointment)
        await cal.save_appointment_async(win_appt)
        return self._to_appointment(win_appt, cal_id)

    async def _delete_async(self, entry_id: str) -> None:
        cal_id, appt_id = self._parse_entry_id(entry_id)
        cal = self._get_calendar(cal_id)
        await cal.delete_appointment_async(appt_id)

    async def _get_async(self, entry_id: str) -> Appointment:
        cal_id, appt_id = self._parse_entry_id(entry_id)
        cal = self._get_calendar(cal_id)
        win_appt = await cal.get_appointment_async(appt_id)
        return self._to_appointment(win_appt, cal_id)

    def _get_calendar(self, cal_id: str):
        cal = self._calendars.get(cal_id)
        if cal is None:
            raise CalendarConnectionError(f"Calendário não encontrado: {cal_id}")
        return cal

    def _apply_to_win_appt(self, win_appt, appointment: Appointment) -> None:
        win_appt.subject = appointment.subject or "(Sem título)"
        win_appt.location = appointment.location or ""
        win_appt.details = appointment.body or ""
        win_appt.all_day = appointment.all_day

        if appointment.all_day:
            start = datetime.combine(appointment.start.date(), time.min)
            days = (appointment.end.date() - appointment.start.date()).days + 1
            win_appt.start_time = start
            win_appt.duration = timedelta(days=max(days, 1))
        else:
            win_appt.start_time = appointment.start.replace(tzinfo=None)
            delta = appointment.end - appointment.start
            win_appt.duration = delta if delta.total_seconds() > 0 else timedelta(hours=1)

    def _to_appointment(self, win_appt, calendar_id: str | None = None) -> Appointment:
        cal_id = calendar_id or win_appt.calendar_id or self._default_calendar.local_id
        start = self._from_win_datetime(win_appt.start_time)
        duration = win_appt.duration or timedelta(hours=1)
        end = start + duration
        all_day = bool(win_appt.all_day)

        if all_day and duration.days >= 1:
            end = datetime.combine(
                (start + duration - timedelta(days=1)).date(),
                time(23, 59),
            )

        entry_id = self._make_entry_id(cal_id, win_appt.local_id)
        return Appointment(
            entry_id=entry_id,
            subject=str(win_appt.subject or ""),
            start=start,
            end=end,
            location=str(win_appt.location or ""),
            body=str(win_appt.details or ""),
            all_day=all_day,
        )

    @staticmethod
    def _from_win_datetime(value) -> datetime:
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        return datetime.fromisoformat(str(value)).replace(tzinfo=None)

    @staticmethod
    def _make_entry_id(calendar_id: str, appointment_id: str) -> str:
        return f"{calendar_id}{ENTRY_SEP}{appointment_id}"

    @staticmethod
    def _parse_entry_id(entry_id: str) -> tuple[str, str]:
        if ENTRY_SEP in entry_id:
            cal_id, appt_id = entry_id.split(ENTRY_SEP, 1)
            return cal_id, appt_id
        raise CalendarConnectionError("Identificador de compromisso inválido.")

    def _ensure_connected(self) -> None:
        if self._store is None:
            self.connect()

    @staticmethod
    def _run(coro):
        return asyncio.run(coro)
