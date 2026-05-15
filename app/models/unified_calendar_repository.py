from __future__ import annotations

from datetime import date

from app.models.appointment import Appointment
from app.models.calendar_repository import CalendarConnectionError, CalendarRepository
from app.models.windows_calendar_repository import WindowsCalendarRepository

ENTRY_SEP = "|"


class UnifiedCalendarRepository:
    """
    Usa Outlook (conta Microsoft) para sincronizar com o app Calendário do Windows.
    Fallback WinRT apenas se o Outlook não estiver disponível.
    """

    def __init__(self) -> None:
        self._backend: str | None = None
        self._outlook: CalendarRepository | None = None
        self._winrt: WindowsCalendarRepository | None = None

    @property
    def backend_name(self) -> str:
        if self._backend == "outlook":
            return "Outlook / Conta Microsoft"
        if self._backend == "winrt":
            return "Calendário local (WinRT)"
        return ""

    def connect(self) -> None:
        errors: list[str] = []

        try:
            self._outlook = CalendarRepository()
            self._outlook.connect()
            self._backend = "outlook"
            return
        except CalendarConnectionError as exc:
            errors.append(f"Outlook: {exc}")

        try:
            self._winrt = WindowsCalendarRepository()
            self._winrt.connect()
            self._backend = "winrt"
            return
        except CalendarConnectionError as exc:
            errors.append(f"WinRT: {exc}")

        raise CalendarConnectionError(
            "Não foi possível conectar ao calendário.\n"
            + "\n".join(errors)
        )

    def list_appointments(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> list[Appointment]:
        return self._repo().list_appointments(start_date, end_date)

    def create(self, appointment: Appointment) -> Appointment:
        return self._repo().create(appointment)

    def update(self, appointment: Appointment) -> Appointment:
        return self._repo().update(appointment)

    def delete(self, entry_id: str) -> None:
        return self._repo().delete(entry_id)

    def get_by_id(self, entry_id: str) -> Appointment:
        return self._repo().get_by_id(entry_id)

    def _repo(self):
        self._ensure_connected()
        if self._backend == "outlook" and self._outlook:
            return self._outlook
        if self._backend == "winrt" and self._winrt:
            return self._winrt
        raise CalendarConnectionError("Nenhum backend de calendário ativo.")

    def _ensure_connected(self) -> None:
        if self._backend is None:
            self.connect()
