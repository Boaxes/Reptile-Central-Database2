import streamlit as st
from frontend.ui.ui_framework.browse import render_browse_tab
from frontend.ui.ui_framework.common import page_setup
from frontend.ui.ui_framework.create_tab import render_create_tab
from frontend.ui.ui_framework.delete_tab import render_delete_tab
from frontend.ui.ui_framework.update_tab import render_update_tab

page_setup(title="Employees", icon="👨‍💼", page_heading="Employees")

tab_browse, tab_create, tab_update, tab_delete = st.tabs(
    ["Browse Employees", "Create Employee", "Update Employee", "Delete Employee"]
)

#Browse Employees Tab
render_browse_tab(
    tab=tab_browse,
    name="Browse Employees",
    view="v_browse_employees_page",
)

#Create Employee Tab
EMPLOYEE_CREATE_SPECS = [
    {"label": "First Name", "type": "text"},
    {"label": "Last Name",  "type": "text"},
    {"label": "Job Title",  "type": "text"},
]

render_create_tab(
    tab=tab_create,
    name="Create Employee",
    create_id="Employee",
    specs=EMPLOYEE_CREATE_SPECS,
    form_key="create_employee_form",
    submit_label="Create Employee",
)

#Update Employee Tab
EMPLOYEE_UPDATE_SPECS = [
    {"label": "First Name", "type": "text", "source": "First Name"},
    {"label": "Last Name",  "type": "text", "source": "Last Name"},
    {"label": "Job Title",  "type": "text", "source": "Job Title"},
]

render_update_tab(
    tab=tab_update,
    name="Update Employee",
    view="v_browse_employees_page",
    update_id="Employee",
    target_id="Employee ID",
    label_field_1="First Name",
    label_field_2="Last Name",
    specs=EMPLOYEE_UPDATE_SPECS,
    form_key="update_employee_form",
    submit_label="Update Employee",
)

#Delete Employee Tab
render_delete_tab(
    tab=tab_delete,
    name="Delete Employee",
    view="v_browse_employees_page",
    delete_id="Employee ID",
    label_field_1="First Name",
    label_field_2="Last Name",
)
