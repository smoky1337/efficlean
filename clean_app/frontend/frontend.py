import os
import webbrowser

import matplotlib.backends.backend_pdf

from clean_app.frontend.layout import get_layout

matplotlib.use('Agg')

import datetime
from datetime import datetime, timedelta
import plotly.express as px
from clean_app.backend.backend import get_app_config, get_config, get_texts, set_or_load_app_config
import pandas as pd
from dash_bootstrap_templates import load_figure_template
load_figure_template("vapor")



# region Graphics
def create_figure(start, end, all_appointments, cleaning_schedule, subset):
    texts = get_texts()
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
        if r["type"] == "booking" or r["type"] == "blocker":
            x_pos = datetime.fromisoformat(r["arrival"]) + (
                    datetime.fromisoformat(r["departure"]) - datetime.fromisoformat(r["arrival"])) / 2
            if r["type"] == "blocker":
                text = texts["g_data_label_blocker"]
            else:
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

        yaxis=dict(color="white",rangemode="tozero", tickmode='array', autorange="min", title=texts["g_y_label"], ticklabelstandoff=20,
                   ),
        xaxis=dict(color="white",title=texts["g_x_label"], ticklabelposition="outside right", tickformat="%e\n%B", dtick="1d", ticks="inside",
                   ticklabelshift=15, ticklabelstandoff=2, tickwidth=0.5,tickangle=0, range = (start,end)),
        title=texts["g_title"].replace("[START]",start_i).replace("[END]",end_i),
    )
    fig.update_legends(
        title_text=texts["g_legend"],
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1
    )
    return fig

# endregion

# region Table


# endregion

# region UIUX
def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')

def reload_layout(app):
    app.layout = get_layout(app)









def get_app_layout(app):
    layout = get_layout(app)
    return layout

# endregion