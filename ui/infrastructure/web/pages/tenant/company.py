import json
from datetime import date, time
from zoneinfo import available_timezones

import streamlit as st


TIMEZONES = sorted(available_timezones())
WEEKDAYS = [
    ("1", "Lunes"),
    ("2", "Martes"),
    ("3", "Miércoles"),
    ("4", "Jueves"),
    ("5", "Viernes"),
    ("6", "Sábado"),
    ("7", "Domingo"),
]


st.title("Empresa")

current_time_zone = "America/Bogota"
st.text_input(
    "Nombre de la empresa",
    placeholder="Ingresa el nombre de la empresa",
    max_chars=200,
    required=True,
    key="company_name",
)

details_columns = st.columns([1, 1, 2], vertical_alignment="bottom")
details_columns[0].text_input(
    "Estado",
    value="Activo",
    disabled=True,
)
details_columns[1].text_input(
    "Plan",
    value="Gratis",
    disabled=True,
)
timezone = details_columns[2].selectbox(
    "Zona horaria",
    TIMEZONES,
    index=(
        TIMEZONES.index(current_time_zone)
        if current_time_zone in TIMEZONES
        else None
    ),
    placeholder="Seleccione una zona horaria",
    filter_mode=None,
)

with st.expander("Configuración del horario semanal"):
    st.caption("Activa cada día y define su horario.")
    header_columns = st.columns([1.5, 1, 1, 1])
    header_columns[0].caption("Día")
    header_columns[1].caption("Abierto")
    header_columns[2].caption("Apertura")
    header_columns[3].caption("Cierre")

    weekly_schedule = {}
    for day_code, day_label in WEEKDAYS:
        day_columns = st.columns(
            [1.5, 1, 1, 1],
            vertical_alignment="center",
        )
        day_columns[0].text(day_label)
        is_open = day_columns[1].checkbox(
            "Abierto",
            value=day_code not in ("6", "7"),
            key=f"company_open_{day_code}",
            label_visibility="collapsed",
        )
        opens_at = day_columns[2].time_input(
            "Apertura",
            value=time(9, 0),
            step=900,
            format="24h",
            key=f"company_start_{day_code}",
            disabled=not is_open,
            label_visibility="collapsed",
        )
        closes_at = day_columns[3].time_input(
            "Cierre",
            value=time(17, 0),
            step=900,
            format="24h",
            key=f"company_end_{day_code}",
            disabled=not is_open,
            label_visibility="collapsed",
        )

        if is_open and opens_at >= closes_at:
            st.error(f"{day_label}: la hora de cierre debe ser posterior.")
            weekly_schedule[day_code] = None
        elif is_open:
            weekly_schedule[day_code] = [{
                "start": opens_at.strftime("%H:%M"),
                "end": closes_at.strftime("%H:%M"),
            }]
        else:
            weekly_schedule[day_code] = []

weekly_summary = []
invalid_weekdays = []
for day_code, day_label in WEEKDAYS:
    intervals = weekly_schedule[day_code]
    if intervals is None:
        invalid_weekdays.append(day_label)
    elif intervals:
        description = ", ".join(
            f'{interval["start"]}–{interval["end"]}'
            for interval in intervals
        )
        weekly_summary.append(f"{day_label}: {description}")

if invalid_weekdays:
    st.warning(
        "Corrige los horarios de: " + ", ".join(invalid_weekdays) + "."
    )
elif weekly_summary:
    st.info("Resumen semanal · " + " · ".join(weekly_summary))
else:
    st.info("No hay horarios laborales configurados.")

with st.expander("Excepciones y festivos"):
    st.caption(
        "Una excepción sustituye el horario de esa fecha."
    )
    exception_columns = st.columns(
        [2, 1, 2, 2, 1.5],
        vertical_alignment="bottom",
    )
    exception_date = exception_columns[0].date_input(
        "Fecha",
        value=date.today(),
        key="company_exception_date",
    )
    exception_open = exception_columns[1].checkbox(
        "Abierto",
        key="company_exception_open",
    )
    exception_start = exception_columns[2].time_input(
        "Apertura",
        value=time(9, 0),
        step=900,
        format="24h",
        key="company_exception_start",
        disabled=not exception_open,
    )
    exception_end = exception_columns[3].time_input(
        "Cierre",
        value=time(17, 0),
        step=900,
        format="24h",
        key="company_exception_end",
        disabled=not exception_open,
    )
    add_exception = exception_columns[4].button(
        "Agregar",
        icon=":material/add:",
        key="company_add_exception",
        help="Agregar excepción",
        width="stretch",
    )

    st.session_state.setdefault("company_schedule_exceptions", {})
    if add_exception:
        if exception_open and exception_start >= exception_end:
            st.error("La hora de cierre debe ser posterior a la de apertura.")
        else:
            intervals = (
                [{
                    "start": exception_start.strftime("%H:%M"),
                    "end": exception_end.strftime("%H:%M"),
                }]
                if exception_open
                else []
            )
            st.session_state["company_schedule_exceptions"][
                exception_date.isoformat()
            ] = intervals
            st.rerun()

    for exception_date_key, intervals in sorted(
        st.session_state["company_schedule_exceptions"].items()
    ):
        exception_row = st.columns(
            [2, 4, 1],
            vertical_alignment="center",
        )
        exception_row[0].write(exception_date_key)
        exception_row[1].write(
            "Cerrado"
            if not intervals
            else f'{intervals[0]["start"]}–{intervals[0]["end"]}'
        )
        if exception_row[2].button(
            "Quitar",
            key=f"company_remove_exception_{exception_date_key}",
            icon=":material/delete:",
        ):
            del st.session_state["company_schedule_exceptions"][
                exception_date_key
            ]
            st.rerun()

action_columns = st.columns([1, 5, 1], vertical_alignment="center")
if action_columns[0].button(
    "Generar JSON",
    type="primary",
    width="stretch",
):
    if invalid_weekdays:
        st.error("Corrige los horarios semanales antes de generar el JSON.")
    else:
        business_hours = {
            "version": 1,
            "weekly": weekly_schedule,
            "exceptions": st.session_state["company_schedule_exceptions"],
        }
        st.session_state["company_schedule_json"] = json.dumps(
            {
                "timezone": timezone,
                "business_hours": business_hours,
            },
            ensure_ascii=False,
            indent=2,
        )

if schedule_json := st.session_state.get("company_schedule_json"):
    action_columns[1].download_button(
        "Descargar horario JSON",
        data=schedule_json,
        file_name="horario_empresa.json",
        mime="application/json",
    )
    with st.expander("Ver JSON generado"):
        st.code(schedule_json, language="json")
