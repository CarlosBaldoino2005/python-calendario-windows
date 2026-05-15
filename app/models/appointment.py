"""
Modelo de um compromisso (appointment).

Representa um evento do calendário de forma independente do Outlook ou WinRT.
O restante do código converte objetos do Windows para esta classe e vice-versa.
"""

from dataclasses import dataclass  # Gera __init__ e atributos automaticamente
from datetime import datetime  # Data e hora (início/fim do compromisso)


@dataclass
class Appointment:
    """
    Dados de um compromisso na memória do programa.

    entry_id: identificador único no calendário (usado para editar/excluir)
    subject: título do evento
    start / end: data e hora de início e fim
    location: local (opcional)
    body: descrição ou notas (opcional)
    all_day: True se for evento de dia inteiro (sem horário específico)
    """

    entry_id: str
    subject: str
    start: datetime
    end: datetime
    location: str = ""
    body: str = ""
    all_day: bool = False

    @property
    def duration_minutes(self) -> int:
        """
        Duração em minutos (propriedade calculada, não armazenada).

        Subtrai fim - início e converte segundos em minutos.
        max(..., 0) evita valor negativo se as datas estiverem invertidas.
        """
        delta = self.end - self.start
        return max(int(delta.total_seconds() // 60), 0)

    @property
    def display_date(self) -> str:
        """Data formatada para exibir na interface (ex.: 15/05/2026)."""
        return self.start.strftime("%d/%m/%Y")

    @property
    def display_time_range(self) -> str:
        """
        Texto do horário para a lista na tela.

        Eventos de dia inteiro mostram "Dia inteiro";
        os demais mostram intervalo HH:MM – HH:MM.
        """
        if self.all_day:
            return "Dia inteiro"
        return f"{self.start.strftime('%H:%M')} – {self.end.strftime('%H:%M')}"
