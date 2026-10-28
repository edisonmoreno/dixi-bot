import pandas as pd
import streamlit as st

from pages.platform.tenant_demo_data import get_demo_tenants


STATUS_LABELS = {
    "ACTIVE": "Activo",
    "SUSPENDED": "Suspendido",
    "INACTIVE": "Inactivo",
}


def reset_page():
    st.session_state.tenant_page_generation += 1


def open_tenant_form(page_tenants):
    click = st.session_state.tenant_edit_button
    st.session_state.tenant_form_code = page_tenants[click.row]["code"]


st.session_state.setdefault("tenant_page_generation", 0)
tenants = get_demo_tenants()

available_plans = sorted({tenant["plan"] for tenant in tenants})

header_columns = st.columns([5, 1], vertical_alignment="center")
with header_columns[0].container(
    horizontal=True,
    vertical_alignment="center",
    gap="small",
):
    st.title("Clientes")
    st.badge(f"{len(tenants)} clientes", color="gray")
if header_columns[1].button(
    ":material/add_circle: Nuevo cliente",
    type="primary",
    width="stretch",
):
    st.switch_page(
        "pages/platform/tenants_form.py",
        query_params={},
    )

filter_columns = st.columns([5, 1, 1], vertical_alignment="bottom")
filter_columns[0].text_input(
    "Buscar",
    placeholder="Nombre o código",
    key="tenant_search",
    on_change=reset_page,
)
filter_columns[1].selectbox(
    "Estado",
    options=["Todos", *STATUS_LABELS],
    format_func=lambda status: (
        "Todos" if status == "Todos" else STATUS_LABELS[status]
    ),
    key="tenant_status_filter",
    on_change=reset_page,
)
filter_columns[2].selectbox(
    "Plan",
    options=["Todos", *available_plans],
    format_func=lambda plan: plan,
    key="tenant_plan_filter",
    on_change=reset_page,
)

search = st.session_state.tenant_search.strip().casefold()
status_filter = st.session_state.tenant_status_filter
plan_filter = st.session_state.tenant_plan_filter
visible_tenants = [
    tenant
    for tenant in tenants
    if search in f'{tenant["name"]} {tenant["code"]}'.casefold()
    and (status_filter == "Todos" or tenant["status"] == status_filter)
    and (plan_filter == "Todos" or tenant["plan"] == plan_filter)
]

page_size = st.session_state.get("tenant_page_size", 5)
page_count = max(1, (len(visible_tenants) + page_size - 1) // page_size)
pagination_key = (
    f"tenant_pagination_{st.session_state.tenant_page_generation}"
)
current_page = min(st.session_state.get(pagination_key, 1), page_count)
start = (current_page - 1) * page_size
page_tenants = visible_tenants[start: start + page_size]

if page_tenants:
    table_data = pd.DataFrame(
        [
            {
                "Organización": tenant["name"],
                "Código": tenant["code"],
                "Estado": STATUS_LABELS[tenant["status"]],
                "Plan": tenant["plan"],
                "Creado en": tenant['created_at'],
                "Editar": ":material/edit: Editar",
            }
            for tenant in page_tenants
        ]
    )
    table_key = (
        f"tenant_table_{current_page}_"
        f"{'_'.join(tenant['code'] for tenant in page_tenants)}"
    )
    st.dataframe(
        table_data,
        width="stretch",
        hide_index=True,
        column_config={
            "Editar": st.column_config.ButtonColumn(
                "Acciones",
                type="tertiary",
                key="tenant_edit_button",
                on_click=open_tenant_form,
                args=(page_tenants,),
            )
        },
        key=table_key,
    )
    tenant_code_to_edit = st.session_state.pop("tenant_form_code", None)
    if tenant_code_to_edit:
        st.switch_page(
            "pages/platform/tenants_form.py",
            query_params={"code": tenant_code_to_edit},
        )
else:
    st.info("No se encontraron clientes con esos filtros.")

range_start = start + 1 if page_tenants else 0
range_end = start + len(page_tenants)
range_text = (
    f"Mostrando {range_start}–{range_end} de "
    f"{len(visible_tenants)} resultados"
)

with st.container(
    horizontal=True,
    horizontal_alignment="right",
    vertical_alignment="center",
    gap="xxsmall",
    wrap=False,
):
    st.caption(range_text)
    st.pagination(
        num_pages=page_count,
        key=pagination_key,
        max_visible_pages=5,
        width="stretch",
    )
    st.selectbox(
        "Filas por página",
        options=[5, 10, 20],
        index=[5, 10, 20].index(page_size),
        key="tenant_page_size",
        on_change=reset_page,
        label_visibility="collapsed",
        width="stretch",
        filter_mode=None
    )
