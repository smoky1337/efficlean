import os
import webbrowser

import matplotlib.backends.backend_pdf

from clean_app.frontend.layout import get_layout

matplotlib.use('Agg')

import datetime
from datetime import datetime, timedelta
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
load_figure_template("vapor")


# region Graphics
def create_figure(start, end, all_appointments, cleaning_schedule, subset):
    k = all_appointments
    if subset:
        k = k[k["apartment"].isin(subset)]
    fig = px.timeline(
        data_frame= k,
        x_start="arrival",
        x_end="departure",
        y="apartment",
        color="Number of Apartments",
        color_discrete_map={
            "": "gray",
            "1": "orange",
            "2": "yellow",
            "3": "green",
        },
        category_orders={
            "Number of Apartments": [str(x) for x in range(0,len(k["apartment"].unique()))],},
        hover_name="type",
        hover_data={}
    )
    for _, r in k.iterrows():
        if r["type"] == "booking":
            x_pos = datetime.fromisoformat(r["arrival"]) + (
                    datetime.fromisoformat(r["departure"]) - datetime.fromisoformat(r["arrival"])) / 2

            text = str(int(float(r["adults"]))) + " P"
            if float(r["children"]) != 0:
                text += " +<br>" + str(int(float(r["children"]))) + " K"
            fig.add_annotation(
                x=x_pos,
                y=r["apartment"],
                text=text,
                font=dict(color="white"),
                showarrow=False
            )

    for _, date in cleaning_schedule.drop_duplicates(subset=["arrival"]).iterrows():

        if date["Number of Apartments"] == "1":
            color = "orange"
        elif date["Number of Apartments"] == "2":
            color = "yellow"
        else:
            color = "green"
        fig.add_vrect(x0=date["arrival"] - timedelta(hours=9), x1=date["arrival"] + timedelta(hours=8), fillcolor=color,
                      opacity=0.2, line_width=0)

    start_i = ".".join(start.split("-")[::-1])
    end_i = ".".join(end.split("-")[::-1])
    fig.update_layout(

        yaxis=dict(color="white",rangemode="tozero", tickmode='array', autorange="min", title="Apartment", ticklabelstandoff=5,
                   tickvals=["Schanzenblick (Suite)", "Pastorensuite (Suite)", "Heidewitzka (Loft)"],
                   ticktext=["Schanzenblick<br>(Suite)", "Pastorensuite<br>(Suite)", "Heidewitzka<br>(Loft)"]),
        xaxis=dict(color="white",title="Datum", ticklabelposition="outside right", tickformat="%e\n%B", dtick="1d", ticks="inside",
                   ticklabelshift=15, ticklabelstandoff=2, tickwidth=0.5,tickangle=0, range = (start,end)),
        title=f"Reinigungsplan von {start_i} bis {end_i}",
    )
    fig.update_legends(
        title_text="Gleichzeitig zu reinigende Apartments",
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1
    )
    return fig


# endregion

# region UIUX
def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')










def get_app_layout(app):
    layout = get_layout(app)
    return layout

# endregion