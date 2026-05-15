"""
Script de diagnóstico: testa acesso WinRT aos calendários do Windows.

Não faz parte da interface gráfica. Execute no terminal para depurar permissões
e listar calendários disponíveis via API WinRT.
"""

import asyncio
from datetime import datetime, timedelta
from winrt.windows.applicationmodel.appointments import (
    Appointment,
    AppointmentManager,
    AppointmentStoreAccessType,
)


async def main():
    """
    Para cada tipo de permissão, lista calendários e tenta criar um evento de teste.
    """
    for access_name in ("ALL_CALENDARS_READ_WRITE", "APP_CALENDARS_READ_WRITE"):
        access = getattr(AppointmentStoreAccessType, access_name)
        print(f"\n=== {access_name} ===")
        store = await AppointmentManager.request_store_async(access)
        cals = list(await store.find_appointment_calendars_async())
        print(f"Calendars: {len(cals)}")
        for c in cals:
            attrs = [
                "display_name", "local_id", "can_create_or_update_appointments",
                "is_primary_calendar", "source_display_name", "user_data_account_id",
            ]
            print(f"  Calendar: {c.display_name!r}")
            for a in attrs:
                if hasattr(c, a):
                    print(f"    {a}={getattr(c, a)!r}")

        if cals:
            cal = cals[0]
            appt = Appointment()
            appt.subject = "DEBUG visibilidade Agenda"
            appt.start_time = datetime.now() + timedelta(days=1)
            appt.duration = timedelta(hours=1)
            appt.location = "Teste"
            await cal.save_appointment_async(appt)
            print(f"  Saved to {cal.display_name!r} id={appt.local_id}")

            found = list(await store.find_appointments_async(
                datetime.now(), timedelta(days=7)
            ))
            print(f"  find_appointments: {len(found)} items")
            for f in found:
                if "DEBUG" in (f.subject or ""):
                    print(f"    FOUND: {f.subject} cal={f.calendar_id}")


asyncio.run(main())
