"""
Diálogo modal para criar ou editar um compromisso.

Janela secundária (CTkToplevel) com formulário: título, datas, horas, local, descrição.
Ao salvar, valida os campos e chama on_save com um objeto Appointment.
"""

from __future__ import annotations

import customtkinter as ctk
from datetime import date, datetime, time, timedelta
from typing import Callable

from app.models.appointment import Appointment
from app.views.date_picker import DatePicker
from app.views.main_view import COLORS


class AppointmentDialog(ctk.CTkToplevel):
    """
    Janela popup sobre a janela principal.

    transient + grab_set: mantém foco nesta janela até fechar (modal).
    """

    def __init__(
        self,
        parent: ctk.CTk,
        title: str,
        appointment: Appointment | None = None,
        on_save: Callable[[Appointment], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("500x580")
        self.minsize(460, 520)
        self.resizable(True, True)
        self.transient(parent)  # Fica sempre acima da janela pai
        self.grab_set()  # Bloqueia interação com a janela principal
        self.configure(fg_color=COLORS["bg"])

        self._on_save = on_save  # Função do controlador (_save_new ou _save_edit)
        self._entry_id = appointment.entry_id if appointment else ""  # Vazio = novo

        self._build_layout(appointment)
        self._center_on_parent(parent)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self._handle_save())

    def _center_on_parent(self, parent: ctk.CTk) -> None:
        """Centraliza o diálogo em relação à janela principal."""
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(px, 0)}+{max(py, 0)}")

    def _build_layout(self, appointment: Appointment | None) -> None:
        """Monta área rolável do formulário e rodapé com Cancelar/Salvar."""
        content = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            scrollbar_button_color=COLORS["border"],
        )
        content.pack(fill="both", expand=True, padx=16, pady=(16, 0))

        self._build_form_fields(content, appointment)

        footer = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=64)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self._error_label = ctk.CTkLabel(
            footer, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"],
        )
        self._error_label.pack(side="left", padx=16, pady=8)

        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(side="right", padx=16, pady=12)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=110, height=38,
            fg_color=COLORS["surface_hover"], hover_color=COLORS["border"],
            command=self.destroy,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Salvar", width=110, height=38,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._handle_save,
        ).pack(side="left")

    def _build_form_fields(
        self, form: ctk.CTkScrollableFrame, appointment: Appointment | None
    ) -> None:
        """Cria todos os campos e preenche se for edição."""
        ctk.CTkLabel(
            form, text="Título",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self._subject = ctk.CTkEntry(form, height=40, placeholder_text="Reunião, consulta...")
        self._subject.pack(fill="x", padx=16, pady=(0, 12))

        self._all_day_var = ctk.BooleanVar(value=appointment.all_day if appointment else False)
        ctk.CTkCheckBox(
            form, text="Dia inteiro", variable=self._all_day_var,
            command=self._toggle_time_fields,
        ).pack(anchor="w", padx=16, pady=(0, 8))

        dates_row = ctk.CTkFrame(form, fg_color="transparent")
        dates_row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(dates_row, text="Data início", width=100, anchor="w").pack(side="left")
        self._start_date = DatePicker(dates_row, width=12)
        self._start_date.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(dates_row, text="Data fim", width=80, anchor="w").pack(side="left")
        self._end_date = DatePicker(dates_row, width=12)
        self._end_date.pack(side="left")

        times_row = ctk.CTkFrame(form, fg_color="transparent")
        times_row.pack(fill="x", padx=16, pady=4)
        self._times_row = times_row

        ctk.CTkLabel(times_row, text="Hora início", width=100, anchor="w").pack(side="left")
        self._start_time = ctk.CTkEntry(times_row, width=80, placeholder_text="HH:MM")
        self._start_time.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(times_row, text="Hora fim", width=80, anchor="w").pack(side="left")
        self._end_time = ctk.CTkEntry(times_row, width=80, placeholder_text="HH:MM")
        self._end_time.pack(side="left")

        ctk.CTkLabel(
            form, text="Local",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self._location = ctk.CTkEntry(form, height=40, placeholder_text="Opcional")
        self._location.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            form, text="Descrição",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self._body = ctk.CTkTextbox(form, height=100, fg_color=COLORS["bg"])
        self._body.pack(fill="x", padx=16, pady=(0, 16))

        if appointment:
            self._fill_form(appointment)
        else:
            # Valores padrão para novo compromisso: hoje, próxima hora cheia
            today = date.today()
            now = datetime.now().replace(minute=0, second=0, microsecond=0)
            end = now + timedelta(hours=1)
            self._start_date.set_date(today)
            self._end_date.set_date(today)
            self._start_time.insert(0, now.strftime("%H:%M"))
            self._end_time.insert(0, end.strftime("%H:%M"))

        self._toggle_time_fields()

    def _fill_form(self, appt: Appointment) -> None:
        """Preenche campos com dados do compromisso em edição."""
        self._subject.insert(0, appt.subject)
        self._start_date.set_date(appt.start.date())
        self._end_date.set_date(appt.end.date())
        self._start_time.insert(0, appt.start.strftime("%H:%M"))
        self._end_time.insert(0, appt.end.strftime("%H:%M"))
        self._location.insert(0, appt.location)
        if appt.body:
            self._body.insert("1.0", appt.body)

    def _toggle_time_fields(self) -> None:
        """Desabilita campos de hora quando "Dia inteiro" está marcado."""
        state = "disabled" if self._all_day_var.get() else "normal"
        for widget in self._times_row.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state=state)

    def _parse_time(self, value: str) -> time:
        """Converte texto HH:MM em objeto time; lança ValueError se inválido."""
        try:
            return datetime.strptime(value.strip(), "%H:%M").time()
        except ValueError:
            raise ValueError(f"Hora inválida: {value}")

    def _handle_save(self) -> None:
        """
        Valida formulário, monta Appointment e chama on_save.

        Fecha o diálogo em caso de sucesso; mostra erro no rodapé se validação falhar.
        """
        try:
            subject = self._subject.get().strip()
            if not subject:
                raise ValueError("Informe um título.")

            start_d = self._start_date.get_date()
            end_d = self._end_date.get_date()
            all_day = self._all_day_var.get()

            if all_day:
                start_dt = datetime.combine(start_d, time.min)
                end_dt = datetime.combine(end_d, time(23, 59))
            else:
                start_dt = datetime.combine(start_d, self._parse_time(self._start_time.get()))
                end_dt = datetime.combine(end_d, self._parse_time(self._end_time.get()))

            if end_dt <= start_dt:
                raise ValueError("A data/hora de fim deve ser posterior ao início.")

            appointment = Appointment(
                entry_id=self._entry_id,
                subject=subject,
                start=start_dt,
                end=end_dt,
                location=self._location.get().strip(),
                body=self._body.get("1.0", "end").strip(),
                all_day=all_day,
            )

            if self._on_save:
                self._on_save(appointment)
            self.destroy()

        except ValueError as exc:
            self._error_label.configure(text=str(exc))
