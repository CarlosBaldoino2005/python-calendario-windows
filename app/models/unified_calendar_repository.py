"""
Repositório unificado: escolhe automaticamente o melhor backend de calendário.

Ordem de tentativa:
  1. Outlook (COM) — preferido, sincroniza com conta Microsoft
  2. WinRT — app Calendário nativo do Windows, se Outlook falhar
"""

from __future__ import annotations

from datetime import date

from app.models.appointment import Appointment
from app.models.calendar_repository import CalendarConnectionError, CalendarRepository
from app.models.windows_calendar_repository import WindowsCalendarRepository

# Separador usado no WinRT para juntar id do calendário + id do compromisso
ENTRY_SEP = "|"


class UnifiedCalendarRepository:
    """
    Fachada (padrão Facade): uma única interface para o controlador.

    O controlador não precisa saber se está usando Outlook ou WinRT;
    este módulo delega para o backend que conectou com sucesso.
    """

    def __init__(self) -> None:
        self._backend: str | None = None  # "outlook" ou "winrt"
        self._outlook: CalendarRepository | None = None
        self._winrt: WindowsCalendarRepository | None = None

    @property
    def backend_name(self) -> str:
        """Nome amigável do backend para exibir na barra de status."""
        if self._backend == "outlook":
            return "Outlook / Conta Microsoft"
        if self._backend == "winrt":
            return "Calendário local (WinRT)"
        return ""

    def connect(self) -> None:
        """
        Tenta conectar ao Outlook; se falhar, tenta WinRT.

        Acumula mensagens de erro e lança CalendarConnectionError
        só se ambos os métodos falharem.
        """
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
        """Delega listagem ao repositório ativo."""
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
        """Retorna o repositório concreto (Outlook ou WinRT) já conectado."""
        self._ensure_connected()
        if self._backend == "outlook" and self._outlook:
            return self._outlook
        if self._backend == "winrt" and self._winrt:
            return self._winrt
        raise CalendarConnectionError("Nenhum backend de calendário ativo.")

    def _ensure_connected(self) -> None:
        if self._backend is None:
            self.connect()
