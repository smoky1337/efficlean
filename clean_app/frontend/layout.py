from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
from dash import dcc, html

from clean_app.backend.backend import get_config, get_texts


def get_layout(app):
    config = get_config()
    texts = get_texts()

    # region header
    header = dbc.Row([
        dbc.Col([
        ],
            width="3",
            className="allign-self-start",
        ),
        dbc.Col([
            html.H2(texts["headline"], id="headerText", className="text-center"),

        ],
            width="6",
            className="allign-self-center",
        ),
        dbc.Col([

        ],
            width="3",
            className="allign-self-end",
        ),
    ],
        className="align-items-center",
        style={"padding-top": "0.5%"}
    )
    # endregion

    # region controls
    controls = dbc.Row([
        dbc.Col([
            html.Span(texts["date_selector_text"], style={"padding-right": "5%"}),
            dcc.DatePickerRange(
                id="date_picker",
                display_format="DD.MM.YYYY",
                with_portal=True,
                initial_visible_month=datetime.today(),
                min_date_allowed=datetime.today(),
                start_date=datetime.today(),
                end_date=datetime.today() + timedelta(days=config["DAYS_OFFSET"])
            )
        ],
            width="8"
        ),
        dbc.Col([
            dbc.Button(texts["download_pdf"], id="btn_download"),
            dcc.Download(id="down"),
            dbc.Button(texts["send_mail"], id="btn_mail", disabled=False),
        ],
            width="3"
        ),
        dbc.Col([
            dbc.Button(texts["settings"], id="open-sm"),
        ],
            width="1"
        )
    ],
        className="align-items-center text-center justify-content-between",
        id="controls"
    )

    apartment_selector = dbc.Row([
        dbc.Col([
            dcc.Dropdown([], searchable=False, multi=True, placeholder=texts["apartment_filter_placeholder"],
                         id="apartment_selector"),

        ], width="7", className="dash-bootstrap"),

        dbc.Col(width="1"),
        dbc.Col([
            html.Span(texts["max_days_label"]),
            dbc.Input(value=config["MAX_DAYS"], id="max_days_picker", placeholder=texts["max_days_placeholder"], min=0, type="number")
        ], width="2"),
        dbc.Col([
            dbc.Button(texts["apply_filters"], id="apartment_selector_confirm"),

        ], width="1", className="dash-bootstrap"),
        dbc.Col(width="1"),

    ],
        className="align-items-center text-center justify-content-between"
    )
    # endregion

    # region config_popup
    app_settings = html.Div([
        dbc.FormFloating(
            [
                dbc.Input(type="number", id="default_max_days"),
                dbc.Label(texts["app_default_max_days"]),
            ]
        ),
        dbc.Form([
            dbc.Label(texts["app_language_selector"]),
            dbc.Select(["deutsch", "english"],id="language_selector"),
            ]
        ),
        dbc.FormFloating(
            [
                dbc.Input(type="number", id="default_date_offset"),
                dbc.Label(texts["app_initial_date_offset"]),
            ]
        ),

        ]
    )

    api_input = dbc.FormFloating(
        [
            dbc.Input(type="text", id="api_input"),
            dbc.Label(texts["smoodu_api"]),
        ]
    )
    email_input = html.Div([
        dbc.FormFloating(
            [
                dbc.Input(type="email", id="email_from_input"),
                dbc.Label(texts["mail_from"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_to_input"),
                dbc.Label(texts["mail_from"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_cc_input"),
                dbc.Label(texts["mail_to"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_subject_input"),
                dbc.Label(texts["mail_subject"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Textarea(id="email_message_input"),
                dbc.Label(texts["mail_message"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Textarea(id="email_template_input"),
                dbc.Label(texts["mail_template"]),
            ]),
    ]
    )

    server_input = html.Div([
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_server_input"),
                dbc.Label(texts["mail_server_adress"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="number", id="email_port_input"),
                dbc.Label(texts["mail_server-port"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_username_input"),
                dbc.Label(texts["mail_server-username"]),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="password", id="email_password_input"),
                dbc.Label(texts["mail_server-password"]),
            ])
    ]
    )

    accordion = dbc.Accordion(
        [
            dbc.AccordionItem(app_settings,
                              title=texts["settings_app"]),
            dbc.AccordionItem(api_input,
                              title=texts["settings_integrations"]),
            dbc.AccordionItem(email_input,
                              title=texts["settings_sharing"]),
            dbc.AccordionItem(server_input,
                              title=texts["settings_mail-server"])
        ],
        className="accordion_settings"
    )

    form = dbc.FormFloating([accordion])
    # endregion

    # region pop-ups
    toast = dbc.Toast(
        "This toast is placed in the top right",
        id="alert",
        header="Problem erkannt:",
        is_open=False,
        duration=5000,
        icon="danger"
    )
    modal = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(texts["settings"])),
        dbc.ModalBody(
            form
        ),
        dbc.ModalFooter([
            dbc.Button(texts["settings_save"], id="btn-config-close-save"),
            dbc.Button(texts["settings_dismiss"], id="btn-config-close-dismiss"),
        ]),
    ],
        id="config-modal",
        size="lg",
        keyboard=False,
        backdrop="static",
        is_open=False
    )
    # endregion

    # region content
    content_fig = dbc.Row([
        dbc.Col([
            dbc.Spinner(
                delay_hide=300,
                id="figcontainer",
            )
        ], width="12")
    ])

    content_table = dbc.Row([
        dbc.Col([
            dbc.Spinner(
                delay_hide=500,
                id="table_loader"
            )
        ], width="12")
    ])
    #endregion
    #region footer

    footer = dbc.Row([
        dbc.Col([],width = 2),
        dbc.Col([texts["version"], ], className="text-center",width = 4),
        dbc.Col([html.A(texts["github"], href="https://github.com/smoky1337/efficlean")], className="text-center",width = 4),
        dbc.Col([], width = 2),
    ],
    style={"position" :"absolute", "bottom" : "0px", "height" : "3%","width" : "100%"},
        className="align-items-center text-center justify-content-between")
    # endregion
    layout = [
        dbc.Container([
            header,
            controls,
            toast,
            modal,
            apartment_selector,
            content_fig,
            html.Br(),
            content_table,
            footer
        ], className="dbc"
        )
    ]
    return layout
