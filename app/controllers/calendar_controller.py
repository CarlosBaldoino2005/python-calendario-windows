"""
Controlador do calendário (camada Controller do MVC).

Recebe eventos da interface (cliques, atualizar) e chama o repositório.
A view não acessa o calendário diretamente — tudo passa por aqui.
"""

from __future__ import annotations

from datetime import date

import customtkinter as ctk
from tkinter import messagebox  # Caixas de diálogo nativas (erro, confirmar)

from app.models.appointment import Appointment
from app.models.calendar_repository import CalendarConnectionError
from app.models.unified_calendar_repository import UnifiedCalendarRepository
from app.views.appointment_dialog import AppointmentDialog
from app.views.main_view import MainView


class CalendarController:
    """
    Liga MainView ↔ UnifiedCalendarRepository.

    Handlers registrados em bind_handlers:
      refresh, create, edit, delete
    """

    def __init__(self, repository: UnifiedCalendarRepository, view: MainView) -> None:
        self._repository = repository
        self._view = view
        # Conecta métodos desta classe aos botões da janela
        self._view.bind_handlers(
            on_refresh=self.refresh,
            on_create=self.create_appointment,
            on_edit=self.edit_appointment,
            on_delete=self.delete_appointment,
        )

    def start(self) -> None:
        """
        Inicialização ao abrir o app: conecta e carrega a lista.

        Mostra mensagem de sucesso ou erro na barra de status.
        """
        try:
            self._repository.connect()
            backend = getattr(self._repository, "backend_name", "")
            msg = f"Conectado — {backend}" if backend else "Conectado ao calendário"
            self._view.show_info(msg)
            start, end = self._view.get_date_range()
            self.refresh(start, end)
        except CalendarConnectionError as exc:
            self._view.show_error(str(exc))
            messagebox.showerror("Conexão", str(exc))

    def refresh(self, start: date, end: date) -> None:
        """
        Recarrega compromissos do período e atualiza a lista na tela.

        Chamado ao mudar 7/30/90 dias, clicar Atualizar ou após criar/editar/excluir.
        """
        try:
            appointments = self._repository.list_appointments(start, end)
            self._view.show_appointments(appointments)
            self._view.show_info(f"{len(appointments)} compromisso(s) carregado(s)")
        except CalendarConnectionError as exc:
            self._view.show_error(str(exc))
            messagebox.showerror("Erro", str(exc))
        except Exception as exc:
            self._view.show_error(str(exc))
            messagebox.showerror("Erro", f"Falha ao listar: {exc}")

    def create_appointment(self) -> None:
        """Abre diálogo vazio; ao salvar, chama _save_new."""
        AppointmentDialog(
            self._view,
            title="Novo compromisso",
            on_save=self._save_new,
        )

    def edit_appointment(self, entry_id: str) -> None:
        """Carrega compromisso pelo id e abre diálogo preenchido."""
        try:
            appointment = self._repository.get_by_id(entry_id)
            AppointmentDialog(
                self._view,
                title="Editar compromisso",
                appointment=appointment,
                on_save=self._save_edit,
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível abrir: {exc}")

    def delete_appointment(self, entry_id: str) -> None:
        """Pede confirmação, exclui no calendário e atualiza a lista."""
        if not messagebox.askyesno("Confirmar", "Excluir este compromisso?"):
            return
        try:
            self._repository.delete(entry_id)
            start, end = self._view.get_date_range()
            self.refresh(start, end)
            self._view.show_info("Compromisso excluído")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao excluir: {exc}")

    def _save_new(self, appointment: Appointment) -> None:
        """Callback do diálogo ao criar: grava, atualiza lista e seleciona o novo item."""
        try:
            created = self._repository.create(appointment)
            start, end = self._view.get_date_range()
            self.refresh(start, end)
            self._view.select_appointment(created.entry_id)
            self._view.show_info("Compromisso criado")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao criar: {exc}")

    def _save_edit(self, appointment: Appointment) -> None:
        """Callback do diálogo ao editar: atualiza e recarrega a lista."""
        try:
            self._repository.update(appointment)
            start, end = self._view.get_date_range()
            self.refresh(start, end)
            self._view.show_info("Compromisso atualizado")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao atualizar: {exc}")
