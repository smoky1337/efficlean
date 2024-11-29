from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
from dash import dcc, dash_table, html

APP = {"app": None}






def get_layout(app):
    #region header
    header = dbc.Row([
        dbc.Col([
            html.Div(
                html.Img(src=app.get_asset_url(path="customer.png"), style={"width":"60%"}, className=".img-fluid"),
                className="text-center",
            ),
        ],
            width="3",
            className="allign-self-start",
        ),
        dbc.Col([
            html.H2("EffiClean Reinigungsplaner", id="headerText",className="text-center"),

        ],
            width="6",
            className="allign-self-center",
        ),
        dbc.Col([
            html.Div(
                html.Img(src=app.get_asset_url(path="zeitgeist.png"), style={"width":"60%"}, className=".img-fluid"),
                className="text-center",
            ),
        ],
            width="3",
            className="allign-self-end",
        ),
    ],
        className="align-items-center",
        style={"padding-top":"0.5%"}
    )
    #endregion

    # region controls
    controls = dbc.Row([
        dbc.Col([
            html.Span("Gewünschten Zeitraum auswählen:",style={"padding-right":"5%"}),
            dcc.DatePickerRange(
                id="date_picker",
                display_format="DD.MM.YYYY",
                with_portal=True,
                initial_visible_month=datetime.today(),
                min_date_allowed=datetime.today(),
                start_date=datetime.today(),
                end_date=datetime.today() + timedelta(days=9)
            )
        ],
            width="8"
        ),
        dbc.Col([
            dbc.Button("Download PDF", id="btn_download"),
            dcc.Download(id="down"),
            dbc.Button(html.A("Versand via Mail", href="mailto:?subject=KWXX%3A%20Neuer%20Putzplan&body=Guten%20Tag%2C%20%0D%0A%0D%0Awie%20besprochen%20finden%20Sie%20anbei%20den%20Putzplan%20f%C3%BCr%20die%20KW%20XX.%20Falls%20%C3%84nderungen%20anfallen%2C%20melden%20wir%20uns%20unter%20dem%20selben%20Betreff%20bei%20Ihnen.%20%0D%0AViele%20Gr%C3%BC%C3%9Fe%2C%20%0D%0AIhr%20Vitihof%20Service%20Team"
                              ,id="mailhack"), id="btn_mail", disabled=False),
        ],
            width="3"
        ),
        dbc.Col([
            dbc.Button("Einstellungen", id="open-sm"),
        ],
            width="1"
        )
    ],
        className="align-items-center text-center justify-content-between",
        id="controls"
    )

    apartment_selector = dbc.Row([
        dbc.Col([
            dcc.Dropdown([], searchable=False, multi=True, placeholder="Apartments filtern", id="apartment_selector"),

        ], width="7", className="dash-bootstrap"),

        dbc.Col(width="1"),
        dbc.Col([
            html.Span("Max Tage"),
            dbc.Input(value=99,id="max_days_picker",placeholder="Tage", min=0,type="number")
        ],width="2"),
        dbc.Col([
            dbc.Button("Aktualisieren", id="apartment_selector_confirm"),

        ], width="1", className="dash-bootstrap"),
        dbc.Col(width="1"),

    ],
        className="align-items-center text-center justify-content-between"
    )
    # endregion

    # region config_popup
    api_input = dbc.FormFloating(
        [
            dbc.Input(type="text", id="api_input"),
            dbc.Label("smoodu API Schlüssel"),
        ]
    )
    email_input = html.Div([
        dbc.FormFloating(
            [
                dbc.Input(type="email", id="email_from_input"),
                dbc.Label("Mail Absender Adresse"),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_to_input"),
                dbc.Label("Mail Empfänger Adresse(n) (durch Komma trennen)"),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_cc_input"),
                dbc.Label("Mail CC Adresse(n) (durch Komma trennen)"),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_subject_input"),
                dbc.Label("Betreff der Mail"),
            ]),
        dbc.FormFloating(
            [
                dbc.Textarea(id="email_message_input"),
                dbc.Label("(HTML / Text) Inhalt der Mail"),
            ]),
        dbc.FormFloating(
            [
                dbc.Textarea(id="email_template_input"),
                dbc.Label("(HTML / Text) Teplate der Mail. Muss [!MESSAGE!] beinhalten"),
            ]),
    ]
    )

    server_input = html.Div([
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_server_input"),
                dbc.Label("Mail Server Adresse"),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="number", id="email_port_input"),
                dbc.Label("Port des Mail Servers (587)"),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="text", id="email_username_input"),
                dbc.Label("Mail Username"),
            ]),
        dbc.FormFloating(
            [
                dbc.Input(type="password", id="email_password_input"),
                dbc.Label("Mail Passwort"),
            ])
    ]
    )

    accordion = dbc.Accordion(
        [
            dbc.AccordionItem(api_input,
                              title="Integrationen"),
            dbc.AccordionItem(email_input,
                              title="Mail"),
            dbc.AccordionItem(server_input,
                              title="Mail-Server")
        ],
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
                dbc.ModalHeader(dbc.ModalTitle("Einstellungen")),
                dbc.ModalBody(
                    form
                ),
                dbc.ModalFooter([
                    dbc.Button("Save", id="btn-config-close-save"),
                    dbc.Button("Dismiss", id="btn-config-close-dismiss"),
                ]),
                ],
                id="config-modal",
                size="lg",
                keyboard=False,
                backdrop="static",
                is_open=False
        )
    #endregion

    #region content
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
    layout = [
        dbc.Container([
            header,
            controls,
            toast,
            modal,
            apartment_selector,
            content_fig,
            html.Br(),
            content_table
        ],className="dbc"
        )
    ]
    return layout