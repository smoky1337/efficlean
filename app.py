import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
import dash
from dash import Dash, dcc, callback, Output, Input, no_update, State, set_props, html,clientside_callback
from clean_app.backend.backend import get_bookings_in_interval, create_dfs, create_pdf, set_or_load_config, \
    get_config, set_config, set_or_load_app_config
import clean_app.backend.mail as mail
from clean_app.frontend.frontend import create_figure, get_app_layout
import dash_bootstrap_components as dbc


PreviousFigure = None
PreviousTable = None

@callback(
    Output(component_id='figcontainer', component_property='children'),
     Output(component_id='table_loader', component_property='children'),
     Output(component_id="alert", component_property='is_open'),
     Output(component_id="alert",component_property='children'),
    Input(component_id='date_picker', component_property='end_date'),
    Input(component_id="apartment_selector_confirm", component_property='n_clicks'),
    State(component_id='date_picker', component_property='start_date'),
    State(component_id='max_days_picker', component_property='value'),
    State(component_id="apartment_selector", component_property='value'),
)
def update_graph(end, n_clicks, start,max_days_uncleaned,subset):

    try:
        c = get_config()
        if c["SMOODU-API-KEY"]:
          pass
    except KeyError:
        return no_update, no_update, True, str("Kein API-KEY gefunden. Bitte in den Einstellungen setzen.")
    global PreviousFigure
    global PreviousTable
    start = start.split("T")[0]
    end = end.split("T")[0]
    df = get_bookings_in_interval(start, end)
    if type(df) is AssertionError:
        return no_update, no_update,True, str(df)
    all_appointments, best_days_with_numbers, cleaning_schedule = create_dfs(df, max_days_uncleaned, start, end)
    set_props("apartment_selector",{"options":all_appointments["apartment"].unique()})
    fig = create_figure(start, end, all_appointments, cleaning_schedule, subset)

    PreviousFigure = fig
    if subset:
        subset.insert(0,"Datum")
        best_days_with_numbers = best_days_with_numbers[subset]

    PreviousTable = best_days_with_numbers.to_dict(orient='records')
    return dcc.Graph(figure=fig),dbc.Table.from_dataframe(best_days_with_numbers, id="table_days",striped=True), no_update, no_update


@callback(
    [Output("config-modal", "is_open",allow_duplicate=True),
    Output(component_id="api_input", component_property='value'),
    Output(component_id="email_from_input", component_property='value'),
    Output(component_id="email_to_input", component_property='value'),
    Output(component_id="email_cc_input", component_property='value'),
    Output(component_id="email_subject_input", component_property='value'),
    Output(component_id="email_template_input", component_property='value'),
    Output(component_id="email_message_input", component_property='value'),
    Output(component_id="email_server_input", component_property='value'),
    Output(component_id="email_port_input", component_property='value'),
    Output(component_id="email_username_input", component_property='value'),
    Output(component_id="email_password_input", component_property='value')],
    Input("open-sm", "n_clicks"),
    prevent_initial_callbacks=True,
    prevent_initial_call=True
)
def toggle_modal(n_clicks):
    try:
        if n_clicks:
            cfg = get_config()
            rt = [True, cfg["SMOODU-API-KEY"]]
            for k in cfg["EMAIL"].keys():
                rt.append(cfg["EMAIL"][k])
            return (*rt,)
        else:
            return [dash.no_update] * 12
    except KeyError:
        rt = [dash.no_update] * 12
        rt[0] = True
        return rt


@callback(
    Output("down", "data"),
    Input("btn_download", "n_clicks"),

    prevent_initial_callbacks=True
)
def download_pdf(n_clicks):
    if n_clicks:
        create_pdf(PreviousFigure, PreviousTable)
        return dcc.send_file(
            os.path.join("tmp", "putzplan.pdf")
        )
    else:
        return dash.no_update


@callback(
    Output(component_id="alert", component_property='is_open', allow_duplicate=True),
    Output(component_id="alert", component_property='children', allow_duplicate=True),
    Input("btn_mail", "n_clicks"),
    State(component_id='date_picker', component_property='start_date'),
    State(component_id='date_picker', component_property='end_date'),
    prevent_initial_callbacks=True,
    prevent_initial_call=True
)
def send_mail(n_clicks,start,end):
    return True, "Bitte Mailclient beachten und Putzplan PDF anhängen!"

    if n_clicks:
        if os.path.exists(os.path.join("tmp", "putzplan.pdf")):
            mail.send_default_mail()
        else:
            create_pdf(PreviousFigure, PreviousTable)
            mail.send_default_mail()

        return True, "Mail erfolgreich versendet!"
    else:
        return True, "Mail konnte nicht versendet werden!"


@callback(
    Output(component_id="config-modal", component_property='is_open', allow_duplicate=True),
    Input(component_id="btn-config-close-save", component_property='n_clicks'),
    Input(component_id="btn-config-close-dismiss", component_property='n_clicks'),

    State(component_id="api_input", component_property='value'),
    State(component_id="email_from_input", component_property='value'),
    State(component_id="email_to_input", component_property='value'),
    State(component_id="email_cc_input", component_property='value'),
    State(component_id="email_subject_input", component_property='value'),
    State(component_id="email_message_input", component_property='value'),
    State(component_id="email_template_input", component_property='value'),
    State(component_id="email_server_input", component_property='value'),
    State(component_id="email_port_input", component_property='value'),
    State(component_id="email_username_input", component_property='value'),
    State(component_id="email_password_input", component_property='value'),

    prevent_initial_callbacks=True,
    prevent_initial_call=True
)
def save_config_to_file(click_save,click_dismiss, api, email_from_input, email_to_input, email_cc_input,
                        email_subject_input, email_message_input,email_template_input, email_server_input,
                        email_port_input, email_username, email_password):
    if click_save:
        config = dict()
        config["EMAIL"] = dict()
        config["SMOODU-API-KEY"] = api
        config["EMAIL"]["FROM"] = email_from_input
        config["EMAIL"]["TO"] = email_to_input
        config["EMAIL"]["CC"] = email_cc_input
        config["EMAIL"]["SUBJECT"] = email_subject_input
        config["EMAIL"]["MESSAGE"] = email_message_input
        config["EMAIL"]["TEMPLATE"] = email_template_input
        config["EMAIL"]["SERVER"] = email_server_input
        config["EMAIL"]["PORT"] = email_port_input
        config["EMAIL"]["USERNAME"] = email_username
        config["EMAIL"]["PASSWORD"] = email_password
        set_config(config)

    return False






def create_app():
    application = Dash(__name__, title="EffiClean")
    set_or_load_config()
    set_or_load_app_config()
    application.layout = get_app_layout(application)
    return application


if __name__ == "__main__":
    app = create_app()
    server = app.server
    app.run(debug=True)
