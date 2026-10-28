import json
import math
from copy import deepcopy
from datetime import date, time

import pandas as pd
import streamlit as st

from pages.platform.tenant_demo_data import DEFAULT_SETTINGS, get_demo_tenants


STATUS_LABELS = {
    "ACTIVE": "Activo",
    "SUSPENDED": "Suspendido",
    "INACTIVE": "Inactivo",
}
PLAN_OPTIONS = ["FREE", "BASIC", "PRO", "ENTERPRISE"]
WEEKDAYS = [
    ("1", "Lunes"),
    ("2", "Martes"),
    ("3", "Miércoles"),
    ("4", "Jueves"),
    ("5", "Viernes"),
    ("6", "Sábado"),
    ("7", "Domingo"),
]


def schedule_state_key(name):
    return f"{st.session_state.business_schedule_scope}_{name}"


def extra_config_state_key(name):
    return f"{st.session_state.extra_config_scope}_{name}"


def extra_config_value_type(value):
    if isinstance(value, bool):
        return "Booleano"
    if isinstance(value, (int, float)):
        return "Número"
    if isinstance(value, str):
        return "Texto"
    return "JSON"


def extra_config_value_text(value, value_type):
    if value_type == "Texto":
        return value
    if value_type == "Número":
        return str(value)
    if value_type == "Booleano":
        return "true" if value else "false"
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def add_extra_config_pair():
    count_key = extra_config_state_key("count")
    index = st.session_state[count_key]
    st.session_state[count_key] += 1
    st.session_state[extra_config_state_key(f"key_{index}")] = ""
    st.session_state[extra_config_state_key(f"type_{index}")] = "Texto"
    st.session_state[extra_config_state_key(f"value_{index}")] = ""
    st.session_state[extra_config_state_key(f"boolean_{index}")] = "true"


def remove_extra_config_pair(index):
    count_key = extra_config_state_key("count")
    count = st.session_state[count_key]
    for current in range(index, count - 1):
        next_index = current + 1
        for field in ("key", "type", "value", "boolean"):
            key = extra_config_state_key(f"{field}_{current}")
            next_key = extra_config_state_key(f"{field}_{next_index}")
            st.session_state[key] = st.session_state[next_key]

    last_index = count - 1
    for field in ("key", "type", "value", "boolean"):
        st.session_state.pop(
            extra_config_state_key(f"{field}_{last_index}"),
            None,
        )
    st.session_state[count_key] -= 1


def collect_extra_config():
    result = {}
    count = st.session_state[extra_config_state_key("count")]
    for index in range(count):
        config_key = st.session_state[
            extra_config_state_key(f"key_{index}")
        ].strip()
        if not config_key:
            raise ValueError("Cada opción adicional debe tener una clave.")
        if config_key in result:
            raise ValueError(f"La clave “{config_key}” está repetida.")

        value_type = st.session_state[
            extra_config_state_key(f"type_{index}")
        ]
        raw_value = st.session_state[
            extra_config_state_key(f"value_{index}")
        ]
        if value_type == "Texto":
            value = raw_value
        elif value_type == "Número":
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"El valor de “{config_key}” debe ser un número válido."
                ) from error
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"El valor de “{config_key}” debe ser un número válido."
                )
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(
                    f"El valor de “{config_key}” debe ser un número finito."
                )
        elif value_type == "Booleano":
            value = (
                st.session_state[
                    extra_config_state_key(f"boolean_{index}")
                ]
                == "true"
            )
        else:
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"El valor JSON de “{config_key}” no es válido "
                    f"({error.msg})."
                ) from error
        result[config_key] = value
    return result


def load_business_schedule(value):
    if not value:
        return {
            "version": 1,
            "weekly": {day: [] for day, _ in WEEKDAYS},
            "exceptions": {},
        }

    if (
        not isinstance(value, dict)
        or value.get("version") != 1
        or not isinstance(value.get("weekly"), dict)
        or not isinstance(value.get("exceptions", {}), dict)
    ):
        raise ValueError(
            "El horario guardado tiene un formato no compatible. "
            "No se modificó para evitar perder datos."
        )

    weekly = value["weekly"]
    valid_days = {day for day, _ in WEEKDAYS}
    if not set(weekly).issubset(valid_days):
        raise ValueError("El horario guardado contiene días no reconocidos.")
    exceptions = value.get("exceptions", {})
    normalized_weekly = {}
    for day, day_label in WEEKDAYS:
        intervals = weekly.get(day, [])
        validate_saved_intervals(intervals, f"Horario de {day_label}")
        normalized_weekly[day] = deepcopy(intervals)

    normalized_exceptions = {}
    for exception_date, intervals in exceptions.items():
        try:
            parsed_date = date.fromisoformat(exception_date)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"La fecha de excepción guardada no es válida: "
                f"{exception_date}."
            ) from error
        if parsed_date.isoformat() != exception_date:
            raise ValueError(
                f"La fecha de excepción guardada no es válida: "
                f"{exception_date}."
            )
        validate_saved_intervals(
            intervals,
            f"Excepción del {exception_date}",
        )
        normalized_exceptions[exception_date] = deepcopy(intervals)

    return {
        "version": 1,
        "weekly": normalized_weekly,
        "exceptions": normalized_exceptions,
    }


def interval_values(interval):
    if interval.get("all_day"):
        return True, time(0, 0), time(23, 45)
    return (
        False,
        time.fromisoformat(interval.get("start", "09:00")),
        time.fromisoformat(interval.get("end", "17:00")),
    )


def add_day_interval(day):
    count_key = schedule_state_key(f"interval_count_{day}")
    new_index = st.session_state[count_key]
    st.session_state[count_key] += 1
    st.session_state[
        schedule_state_key(f"all_day_{day}_{new_index}")
    ] = False
    st.session_state[
        schedule_state_key(f"start_{day}_{new_index}")
    ] = time(9, 0)
    st.session_state[
        schedule_state_key(f"end_{day}_{new_index}")
    ] = time(17, 0)


def remove_day_interval(day, index):
    count_key = schedule_state_key(f"interval_count_{day}")
    count = st.session_state[count_key]
    for current in range(index, count - 1):
        next_index = current + 1
        for field in ("all_day", "start", "end"):
            key = schedule_state_key(f"{field}_{day}_{current}")
            next_key = schedule_state_key(f"{field}_{day}_{next_index}")
            st.session_state[key] = st.session_state[next_key]

    last_index = count - 1
    for field in ("all_day", "start", "end"):
        st.session_state.pop(
            schedule_state_key(f"{field}_{day}_{last_index}"),
            None,
        )
    st.session_state[count_key] -= 1


def remove_schedule_exception(exception_date):
    st.session_state[
        schedule_state_key("exceptions")
    ].pop(exception_date, None)


def remove_schedule_exception_from_table(exception_dates):
    click = st.session_state[schedule_state_key("exception_table_action")]
    exception_date = exception_dates[click.row]
    remove_schedule_exception(exception_date)


def describe_exception_intervals(intervals):
    if not intervals:
        return "Cerrado"
    return ", ".join(
        "Todo el día"
        if interval.get("all_day")
        else f'{interval["start"]}–{interval["end"]}'
        for interval in intervals
    )


def collect_day_intervals(day):
    if not st.session_state[schedule_state_key(f"open_{day}")]:
        return []

    intervals = []
    count = st.session_state[schedule_state_key(f"interval_count_{day}")]
    for index in range(count):
        if st.session_state[
            schedule_state_key(f"all_day_{day}_{index}")
        ]:
            intervals.append({"all_day": True})
        else:
            start_time = st.session_state[
                schedule_state_key(f"start_{day}_{index}")
            ]
            end_time = st.session_state[
                schedule_state_key(f"end_{day}_{index}")
            ]
            intervals.append(
                {
                    "start": start_time.strftime("%H:%M"),
                    "end": end_time.strftime("%H:%M"),
                }
            )
    return intervals


def validate_intervals(intervals, label):
    if any(interval.get("all_day") for interval in intervals):
        if len(intervals) != 1 or not intervals[0].get("all_day"):
            raise ValueError(
                f"{label}: un horario de 24 horas no puede combinarse "
                "con otros intervalos."
            )
        return

    sorted_intervals = sorted(intervals, key=lambda item: item["start"])
    previous_end = None
    for interval in sorted_intervals:
        start_time = time.fromisoformat(interval["start"])
        end_time = time.fromisoformat(interval["end"])
        if start_time >= end_time:
            raise ValueError(
                f"{label}: la hora de apertura debe ser anterior al cierre. "
                "Divide los horarios nocturnos entre dos días."
            )
        if previous_end is not None and start_time < previous_end:
            raise ValueError(f"{label}: los intervalos no pueden solaparse.")
        previous_end = end_time


def validate_saved_intervals(intervals, label):
    if not isinstance(intervals, list):
        raise ValueError(f"{label}: se esperaba una lista de intervalos.")

    for interval in intervals:
        if not isinstance(interval, dict):
            raise ValueError(f"{label}: el intervalo guardado no es válido.")
        if interval == {"all_day": True}:
            continue
        if (
            set(interval) != {"start", "end"}
            or not isinstance(interval["start"], str)
            or not isinstance(interval["end"], str)
        ):
            raise ValueError(f"{label}: el intervalo guardado no es válido.")
        try:
            start_time = time.fromisoformat(interval["start"])
            end_time = time.fromisoformat(interval["end"])
        except ValueError as error:
            raise ValueError(
                f"{label}: el formato de hora debe ser HH:MM."
            ) from error
        if (
            start_time.strftime("%H:%M") != interval["start"]
            or end_time.strftime("%H:%M") != interval["end"]
        ):
            raise ValueError(
                f"{label}: el formato de hora debe ser HH:MM."
            )

    validate_intervals(intervals, label)


tenants = get_demo_tenants()
tenant_code = st.query_params.get("code")
tenant = next(
    (item for item in tenants if item["code"] == tenant_code),
    None,
) if tenant_code else None

if tenant_code and tenant is None:
    st.error("No se encontró el cliente solicitado en esta sesión de demostración.")
    if st.button("Volver al listado"):
        st.switch_page("pages/platform/tenants.py", query_params={})
    st.stop()

is_edit = tenant is not None
st.session_state.business_schedule_scope = (
    f"business_schedule_{tenant_code or 'new'}"
)
st.session_state.extra_config_scope = (
    f"extra_config_{tenant_code or 'new'}"
)
page_title = "Editar cliente" if is_edit else "Crear cliente"
st.title(page_title)
st.caption(
    "Configura los datos de la organización y los ajustes de su asistente."
)
if st.button(":material/arrow_left_alt: Volver a clientes"):
    st.switch_page("pages/platform/tenants.py", query_params={})

current_settings = (
    {**DEFAULT_SETTINGS, **tenant["settings"]} if is_edit else DEFAULT_SETTINGS
)
current_extra_config = current_settings.get("extra_config", {})
if not isinstance(current_extra_config, dict):
    st.error("La configuración adicional guardada debe ser un objeto JSON.")
    st.stop()

extra_config_items = list(current_extra_config.items())
st.session_state.setdefault(
    extra_config_state_key("count"),
    len(extra_config_items),
)
for index, (config_key, value) in enumerate(extra_config_items):
    value_type = extra_config_value_type(value)
    st.session_state.setdefault(
        extra_config_state_key(f"key_{index}"),
        config_key,
    )
    st.session_state.setdefault(
        extra_config_state_key(f"type_{index}"),
        value_type,
    )
    st.session_state.setdefault(
        extra_config_state_key(f"value_{index}"),
        extra_config_value_text(value, value_type),
    )
    st.session_state.setdefault(
        extra_config_state_key(f"boolean_{index}"),
        "true" if value else "false",
    )

try:
    business_schedule = load_business_schedule(
        current_settings.get("business_hours", {})
    )
except ValueError as error:
    st.error(str(error))
    st.stop()

st.session_state.setdefault(
    schedule_state_key("exceptions"),
    deepcopy(business_schedule["exceptions"]),
)
for day, _ in WEEKDAYS:
    intervals = business_schedule["weekly"][day]
    st.session_state.setdefault(
        schedule_state_key(f"open_{day}"),
        bool(intervals),
    )
    st.session_state.setdefault(
        schedule_state_key(f"interval_count_{day}"),
        max(1, len(intervals)),
    )
    for index in range(max(1, len(intervals))):
        interval = intervals[index] if index < len(intervals) else {}
        all_day, start_time, end_time = interval_values(interval)
        st.session_state.setdefault(
            schedule_state_key(f"all_day_{day}_{index}"),
            all_day,
        )
        st.session_state.setdefault(
            schedule_state_key(f"start_{day}_{index}"),
            start_time,
        )
        st.session_state.setdefault(
            schedule_state_key(f"end_{day}_{index}"),
            end_time,
        )

chat_settings = {
    **DEFAULT_SETTINGS["chat"],
    **current_settings.get("chat", {}),
}
embedding_settings = {
    **DEFAULT_SETTINGS["embedding"],
    **current_settings.get("embedding", {}),
}

with st.container():
    st.subheader("Organización")
    name = st.text_input(
        "Nombre",
        value=tenant["name"] if is_edit else "",
        max_chars=200,
        placeholder="Nombre de la organización",
    )
    tenant_columns = st.columns(2)
    status = tenant_columns[0].selectbox(
        "Estado",
        options=list(STATUS_LABELS),
        index=(
            list(STATUS_LABELS).index(tenant["status"])
            if is_edit
            else 0
        ),
        format_func=lambda value: STATUS_LABELS[value],
    )
    plan = tenant_columns[1].text_input(
        "Plan",
        value=tenant["plan"] if is_edit else "FREE",
        max_chars=50,
        placeholder="FREE",
    )

    st.divider()
    (
        assistant_tab,
        chat_tab,
        embedding_tab,
        business_tab,
        extra_config_tab,
    ) = st.tabs(
        [
            "Asistente",
            "Configuración chat",
            "Configuración embeddings",
            "Horarios",
            "Configuración adicional",
        ]
    )

    with assistant_tab:
        st.caption("Define la identidad y las instrucciones del asistente.")
        agent_name = st.text_input(
            "Nombre del asistente",
            value=current_settings.get("agent_name", "Asistente"),
            max_chars=100,
        )
        system_prompt = st.text_area(
            "Instrucciones del sistema",
            value=current_settings.get(
                "system_prompt", "Eres un asistente útil."
            ),
            height=120,
            help="Define el propósito, tono y límites del asistente.",
        )

    with chat_tab:
        st.caption("Proveedor y parámetros para generar respuestas.")
        chat_columns = st.columns(2)
        chat_provider = chat_columns[0].text_input(
            "Proveedor",
            value=chat_settings["provider"],
            key="chat_provider",
        )
        chat_model = chat_columns[1].text_input(
            "Modelo",
            value=chat_settings["model"],
            key="chat_model",
        )
        chat_base_url = chat_columns[0].text_input(
            "URL base",
            value=chat_settings["base_url"],
            key="chat_base_url",
        )
        chat_api_key = chat_columns[1].text_input(
            "Clave API",
            value=chat_settings.get("api_key", ""),
            type="password",
            key="chat_api_key",
            help="Solo se almacena en la sesión local de demostración.",
        )
        chat_temperature = chat_columns[0].number_input(
            "Temperatura",
            min_value=0.0,
            max_value=2.0,
            value=float(chat_settings["temperature"]),
            step=0.1,
            key="chat_temperature",
        )
        chat_timeout = chat_columns[1].number_input(
            "Tiempo de espera (segundos)",
            min_value=1,
            value=int(chat_settings["timeout"]),
            step=1,
            key="chat_timeout",
        )
        chat_max_retries = chat_columns[0].number_input(
            "Reintentos máximos",
            min_value=0,
            value=int(chat_settings["max_retries"]),
            step=1,
            key="chat_max_retries",
        )

    with embedding_tab:
        st.caption("Proveedor y parámetros de búsqueda semántica.")
        embedding_columns = st.columns(2)
        embedding_provider = embedding_columns[0].text_input(
            "Proveedor",
            value=embedding_settings["provider"],
            key="embedding_provider",
        )
        embedding_model = embedding_columns[1].text_input(
            "Modelo",
            value=embedding_settings["model"],
            key="embedding_model",
        )
        embedding_base_url = embedding_columns[0].text_input(
            "URL base",
            value=embedding_settings["base_url"],
            key="embedding_base_url",
        )
        embedding_api_key = embedding_columns[1].text_input(
            "Clave API",
            value=embedding_settings.get("api_key", ""),
            type="password",
            key="embedding_api_key",
            help="Solo se almacena en la sesión local de demostración.",
        )
        embedding_dimensions = embedding_columns[0].number_input(
            "Dimensiones",
            min_value=1,
            value=int(embedding_settings["dimensions"]),
            step=1,
            key="embedding_dimensions",
        )
        embedding_threshold = embedding_columns[1].number_input(
            "Umbral de similitud",
            min_value=0.0,
            max_value=1.0,
            value=float(embedding_settings["similarity_threshold"]),
            step=0.01,
            key="embedding_threshold",
        )
        embedding_language = embedding_columns[0].text_input(
            "Idioma",
            value=embedding_settings["language"],
            key="embedding_language",
        )

    with business_tab:
        st.caption(
            "Define los horarios de atención. Puedes agregar "
            "varios intervalos por día."
        )
        for day, day_label in WEEKDAYS:
            with st.container(border=True):
                day_columns = st.columns(
                    [1, 1, 4], vertical_alignment="center")
                day_columns[0].markdown(f"**{day_label}**")
                is_open = day_columns[1].checkbox(
                    "Abierto",
                    key=schedule_state_key(f"open_{day}"),
                )
                interval_count = st.session_state[
                    schedule_state_key(f"interval_count_{day}")
                ]
                has_all_day_interval = any(
                    st.session_state[
                        schedule_state_key(f"all_day_{day}_{index}")
                    ]
                    for index in range(interval_count)
                )
                if is_open and day_columns[2].button(
                    "Agregar horario",
                    key=schedule_state_key(f"add_interval_{day}"),
                    icon=":material/add:",
                    disabled=has_all_day_interval,
                ):
                    add_day_interval(day)
                    st.rerun()

                if is_open:
                    for index in range(interval_count):
                        interval_columns = st.columns(
                            [1, 2, 2, 1],
                            vertical_alignment="bottom",
                        )
                        interval_columns[0].checkbox(
                            "Todo el día",
                            key=schedule_state_key(
                                f"all_day_{day}_{index}"
                            ),
                            disabled=interval_count > 1,
                        )
                        is_all_day = st.session_state[
                            schedule_state_key(f"all_day_{day}_{index}")
                        ]
                        interval_columns[1].time_input(
                            "Apertura",
                            key=schedule_state_key(
                                f"start_{day}_{index}"
                            ),
                            disabled=is_all_day,
                            step=900,
                            format="24h",
                        )
                        interval_columns[2].time_input(
                            "Cierre",
                            key=schedule_state_key(f"end_{day}_{index}"),
                            disabled=is_all_day,
                            step=900,
                            format="24h",
                        )
                        interval_columns[3].button(
                            "Quitar",
                            key=schedule_state_key(
                                f"remove_interval_{day}_{index}"
                            ),
                            icon=":material/delete:",
                            disabled=interval_count <= 1,
                            on_click=remove_day_interval,
                            args=(day, index),
                        )

        st.subheader("Excepciones y festivos")
        st.caption(
            "Una excepción sustituye el horario semanal de esa fecha. "
            "Deja desactivado “Abierto” para marcar un cierre."
        )
        exception_columns = st.columns(
            [2, 1, 1, 2, 2, 1],
            vertical_alignment="bottom",
        )
        exception_date = exception_columns[0].date_input(
            "Fecha",
            value=date.today(),
            key=schedule_state_key("exception_date"),
        )
        exception_open = exception_columns[1].checkbox(
            "Abierto",
            key=schedule_state_key("exception_open"),
        )
        exception_all_day = exception_columns[2].checkbox(
            "Todo el día",
            key=schedule_state_key("exception_all_day"),
            disabled=not exception_open,
        )
        exception_start = exception_columns[3].time_input(
            "Apertura",
            value=time(9, 0),
            key=schedule_state_key("exception_start"),
            disabled=not exception_open or exception_all_day,
            step=900,
            format="24h",
        )
        exception_end = exception_columns[4].time_input(
            "Cierre",
            value=time(17, 0),
            key=schedule_state_key("exception_end"),
            disabled=not exception_open or exception_all_day,
            step=900,
            format="24h",
        )
        if exception_columns[5].button(
            "Agregar",
            key=schedule_state_key("add_exception"),
            icon=":material/add:",
            help="Agrega o reemplaza la excepción para esta fecha.",
        ):
            exception_key = exception_date.isoformat()
            exception_intervals = (
                [{"all_day": True}]
                if exception_open and exception_all_day
                else [
                    {
                        "start": exception_start.strftime("%H:%M"),
                        "end": exception_end.strftime("%H:%M"),
                    }
                ]
                if exception_open and not exception_all_day
                else []
            )
            try:
                validate_intervals(
                    exception_intervals,
                    f"Excepción del {exception_key}",
                )
            except ValueError as error:
                st.error(str(error))
            else:
                st.session_state[
                    schedule_state_key("exceptions")
                ][exception_key] = exception_intervals
                st.rerun()

        schedule_exceptions = st.session_state[
            schedule_state_key("exceptions")
        ]
        if schedule_exceptions:
            exception_dates = sorted(schedule_exceptions)
            exception_table = pd.DataFrame(
                [
                    {
                        "Fecha": date.fromisoformat(exception_key).strftime(
                            "%d/%m/%Y"
                        ),
                        "Horario": describe_exception_intervals(
                            schedule_exceptions[exception_key]
                        ),
                        "Acción": ":material/delete: Quitar",
                    }
                    for exception_key in exception_dates
                ]
            )
            st.dataframe(
                exception_table,
                width="stretch",
                hide_index=True,
                column_config={
                    "Fecha": st.column_config.TextColumn(
                        width="small",
                    ),
                    "Horario": st.column_config.TextColumn(
                        width="stretch",
                    ),
                    "Acción": st.column_config.ButtonColumn(
                        "",
                        type="tertiary",
                        width="small",
                        key=schedule_state_key("exception_table_action"),
                        on_click=remove_schedule_exception_from_table,
                        args=(exception_dates,),
                    ),
                },
                key=schedule_state_key("exception_table"),
            )

        weekly_summary = []
        for day, day_label in WEEKDAYS:
            day_intervals = collect_day_intervals(day)
            if day_intervals:
                description = ", ".join(
                    "24 horas"
                    if interval.get("all_day")
                    else f'{interval["start"]}–{interval["end"]}'
                    for interval in day_intervals
                )
                weekly_summary.append(f"{day_label}: {description}")
        if weekly_summary:
            st.info("Resumen semanal · " + " · ".join(weekly_summary))

    with extra_config_tab:
        st.caption(
            "Agrega opciones adicionales usando pares de clave y valor."
        )
        extra_config_count = st.session_state[
            extra_config_state_key("count")
        ]
        if extra_config_count == 0:
            st.info("Aún no hay opciones adicionales configuradas.")
        for index in range(extra_config_count):
            with st.container(border=True):
                config_columns = st.columns([2, 1, 3, 1])
                config_columns[0].text_input(
                    "Clave",
                    key=extra_config_state_key(f"key_{index}"),
                    placeholder="ej. max_results",
                )
                config_value_type = config_columns[1].selectbox(
                    "Tipo",
                    options=["Texto", "Número", "Booleano", "JSON"],
                    key=extra_config_state_key(f"type_{index}"),
                )
                if config_value_type == "Booleano":
                    config_columns[2].selectbox(
                        "Valor",
                        options=["true", "false"],
                        format_func=lambda value: (
                            "Verdadero" if value == "true" else "Falso"
                        ),
                        key=extra_config_state_key(f"boolean_{index}"),
                    )
                else:
                    config_columns[2].text_input(
                        "Valor",
                        key=extra_config_state_key(f"value_{index}"),
                        placeholder=(
                            "JSON válido"
                            if config_value_type == "JSON"
                            else "Valor"
                        ),
                        help=(
                            "Ingresa un valor JSON, como un objeto, una "
                            "lista, una cadena, un número, true, false o null."
                            if config_value_type == "JSON"
                            else None
                        ),
                    )
                config_columns[3].button(
                    "Quitar",
                    key=extra_config_state_key(f"remove_{index}"),
                    icon=":material/delete:",
                    on_click=remove_extra_config_pair,
                    args=(index,),
                )
        st.button(
            "Agregar opción",
            key=extra_config_state_key("add"),
            icon=":material/add:",
            on_click=add_extra_config_pair,
        )

    submitted = st.button(
        "Guardar cambios" if is_edit else "Crear cliente",
        type="primary",
        width="stretch",
    )

if submitted:
    if not name.strip() or not plan.strip():
        st.error("Completa el nombre, el código y el plan.")
    elif not agent_name.strip() or not system_prompt.strip():
        st.error("Completa el nombre y las instrucciones del asistente.")
    elif not chat_provider.strip() or not chat_model.strip():
        st.error("Completa el proveedor y el modelo de chat.")
    elif not embedding_provider.strip() or not embedding_model.strip():
        st.error("Completa el proveedor y el modelo de embeddings.")
    else:
        try:
            weekly_schedule = {
                day: collect_day_intervals(day)
                for day, _ in WEEKDAYS
            }
            for day, day_label in WEEKDAYS:
                validate_intervals(
                    weekly_schedule[day],
                    day_label,
                )
            for exception_key, intervals in st.session_state[
                schedule_state_key("exceptions")
            ].items():
                validate_intervals(
                    intervals,
                    f"Excepción del {exception_key}",
                )
            extra_config = collect_extra_config()
        except ValueError as error:
            st.error(str(error))
        else:
            settings = {
                "agent_name": agent_name.strip(),
                "system_prompt": system_prompt.strip(),
                "chat": {
                    "provider": chat_provider.strip(),
                    "model": chat_model.strip(),
                    "base_url": chat_base_url.strip(),
                    "api_key": chat_api_key,
                    "temperature": chat_temperature,
                    "timeout": chat_timeout,
                    "max_retries": chat_max_retries,
                },
                "embedding": {
                    "provider": embedding_provider.strip(),
                    "model": embedding_model.strip(),
                    "base_url": embedding_base_url.strip(),
                    "api_key": embedding_api_key,
                    "dimensions": embedding_dimensions,
                    "similarity_threshold": embedding_threshold,
                    "language": embedding_language.strip(),
                },
                "business_hours": {
                    "version": 1,
                    "weekly": weekly_schedule,
                    "exceptions": deepcopy(
                        st.session_state[
                            schedule_state_key("exceptions")
                        ]
                    ),
                },
                "extra_config": extra_config,
            }

            if is_edit:
                tenant.update(
                    {
                        "code": normalized_code,
                        "name": name.strip(),
                        "status": status,
                        "plan": plan.strip(),
                        "settings": settings,
                    }
                )
                st.success("Cliente actualizado en la sesión de demostración.")
            else:
                tenants.append(
                    {
                        "code": normalized_code,
                        "name": name.strip(),
                        "status": status,
                        "plan": plan.strip(),
                        "created_at": date.today().isoformat(),
                        "settings": settings,
                    }
                )
                st.success("Cliente creado en la sesión de demostración.")

            st.switch_page("pages/platform/tenants.py", query_params={})
