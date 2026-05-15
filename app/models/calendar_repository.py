"""
Repositório do calendário via Microsoft Outlook (COM).

COM é a tecnologia do Windows para programas conversarem com o Outlook instalado.
Este módulo é o backend preferido: sincroniza com contas Microsoft no app Calendário.
"""

from __future__ import annotations  # Permite usar tipos como date | None em versões antigas

from datetime import date, datetime, time, timedelta
from app.models.appointment import Appointment

# Constantes do Outlook: tipo de pasta "Calendário" e tipo de item "Compromisso"
OL_FOLDER_CALENDAR = 9
OL_APPOINTMENT_ITEM = 1


class CalendarConnectionError(Exception):
    """Erro lançado quando o Outlook não está instalado ou o calendário não abre."""


class CalendarRepository:
    """
    Acesso CRUD ao calendário padrão do Outlook.

    CRUD = Create, Read, Update, Delete (criar, ler, atualizar, excluir).
    Mantém referências internas à aplicação Outlook após connect().
    """

    def __init__(self) -> None:
        """Inicializa com conexão vazia; connect() preenche os atributos."""
        self._outlook = None  # Aplicação Outlook
        self._namespace = None  # Namespace MAPI (pastas e contas)
        self._calendar_folder = None  # Pasta do calendário

    def connect(self) -> None:
        """
        Abre o Outlook em segundo plano e obtém a pasta do calendário.

        Levanta CalendarConnectionError se pywin32 não estiver instalado
        ou se o Outlook/Calendário não estiver configurado.
        """
        try:
            import win32com.client  # Biblioteca para falar com programas Windows (COM)
        except ImportError as exc:
            raise CalendarConnectionError(
                "Instale pywin32: pip install pywin32"
            ) from exc

        try:
            # Dispatch abre ou conecta à instância do Outlook
            self._outlook = win32com.client.Dispatch("Outlook.Application")
            self._namespace = self._outlook.GetNamespace("MAPI")
            # Pasta padrão de calendário do usuário
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
        """
        Lista compromissos entre start_date e end_date (inclusive).

        Se as datas forem omitidas: de hoje até 30 dias à frente.
        Percorre itens da pasta, filtra por intervalo e ordena por início.
        """
        self._ensure_connected()

        start_date = start_date or date.today()
        end_date = end_date or (start_date + timedelta(days=30))
        # Início do primeiro dia; fim = meia-noite do dia seguinte ao end_date
        range_start = datetime.combine(start_date, time.min)
        range_end = datetime.combine(end_date + timedelta(days=1), time.min)

        items = self._calendar_folder.Items
        items.IncludeRecurrences = True  # Inclui ocorrências de eventos recorrentes
        items.Sort("[Start]")  # Ordena por data de início (importante para o loop)

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
        """
        Varre itens do Outlook e adiciona os que caem no intervalo.

        Como a lista está ordenada por Start, pode parar quando start >= range_end.
        Ignora itens com erro de leitura e limita varredura a max_scan por segurança.
        """
        try:
            total = int(items.Count)
        except Exception:
            total = -1

        # Alguns cenários COM retornam Count inválido; usa limite fixo
        if total <= 0 or total >= 2_000_000_000:
            total = max_scan

        for index in range(1, total + 1):  # Índices COM do Outlook começam em 1
            try:
                item = items.Item(index)
            except Exception:
                break  # Fim da lista ou erro: para a varredura
            try:
                start = self._parse_com_datetime(item.Start)
                if start >= range_end:
                    break  # Já passou do fim do intervalo (lista ordenada)
                end = self._parse_com_datetime(item.End)
                if end < range_start:
                    continue  # Terminou antes do intervalo: pula
                appointments.append(self._to_appointment(item))
            except Exception:
                continue  # Item corrompido ou tipo inesperado: ignora

    def create(self, appointment: Appointment) -> Appointment:
        """Cria novo compromisso na pasta do calendário e retorna com entry_id preenchido."""
        self._ensure_connected()
        item = self._calendar_folder.Items.Add(OL_APPOINTMENT_ITEM)
        self._apply_to_item(item, appointment)
        item.Save()
        return self._to_appointment(item)

    def update(self, appointment: Appointment) -> Appointment:
        """Atualiza compromisso existente usando entry_id."""
        self._ensure_connected()
        item = self._namespace.GetItemFromID(appointment.entry_id)
        self._apply_to_item(item, appointment)
        item.Save()
        return self._to_appointment(item)

    def delete(self, entry_id: str) -> None:
        """Remove compromisso pelo identificador único do Outlook."""
        self._ensure_connected()
        item = self._namespace.GetItemFromID(entry_id)
        item.Delete()

    def get_by_id(self, entry_id: str) -> Appointment:
        """Busca um compromisso para abrir o diálogo de edição."""
        self._ensure_connected()
        item = self._namespace.GetItemFromID(entry_id)
        return self._to_appointment(item)

    def _ensure_connected(self) -> None:
        """Garante conexão antes de qualquer operação; reconecta se necessário."""
        if self._calendar_folder is None:
            self.connect()

    def _apply_to_item(self, item, appointment: Appointment) -> None:
        """Copia campos do objeto Appointment para o item COM do Outlook."""
        item.Subject = appointment.subject or "(Sem título)"
        item.Location = appointment.location or ""
        item.Body = appointment.body or ""
        item.AllDayEvent = appointment.all_day

        if appointment.all_day:
            # Dia inteiro: Outlook usa início à meia-noite e fim no dia seguinte
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
        """Normaliza date/datetime para o formato que o COM aceita (sem microssegundos)."""
        if isinstance(value, datetime):
            return value.replace(second=0, microsecond=0)
        if hour is not None:
            return datetime.combine(value, hour).replace(second=0, microsecond=0)
        return datetime.combine(value, time.min).replace(second=0, microsecond=0)

    def _to_appointment(self, item) -> Appointment:
        """Converte um item COM do Outlook para a classe Appointment."""
        start = self._parse_com_datetime(item.Start)
        end = self._parse_com_datetime(item.End)
        all_day = bool(getattr(item, "AllDayEvent", False))

        # Outlook guarda fim de dia inteiro como meia-noite do dia seguinte
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
        """
        Converte data/hora vinda do COM para datetime Python.

        O COM pode devolver datetime, objeto com .year/.month ou string ISO.
        """
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
