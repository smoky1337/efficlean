import json
import os

import matplotlib.backends.backend_pdf
import pandas as pd
import requests

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PyPDF2 import PdfMerger

import datetime
from datetime import datetime, timedelta
import plotly.graph_objects as go
CONFIG = {}
import plotly.io as pio
pio.kaleido.scope.mathjax = None


# region Request to Smoobu
def get(url, payload):
    """
    Sends a GET request to the specified URL with the provided payload and headers.

    Parameters:
    - url (str): The API endpoint to send the request to.
    - payload (dict): Query parameters to include in the request.

    Returns:
    - Response: The response object from the GET request.
    """
    headers = {"Api-Key": CONFIG["SMOODU-API-KEY"], "Cache-Control": "no-cache"}

    return requests.get(url=url, headers=headers, params=payload)


def get_bookings_in_interval(start, end):
    """
    Fetches bookings within a specified interval.

    Parameters:
    - start (str): The start date of the interval in "YYYY-MM-DD" format.
    - end (str): The end date of the interval in "YYYY-MM-DD" format.

    Returns:
    - DataFrame: A pandas DataFrame containing the booking data.
    """
    df = None
    try:
        data = get(
        url="https://login.smoobu.com/api/reservations",
        payload=
        {
            "departureFrom": start,
            "arrivalTo": end,
            "pageSize": 100,
            "page":1
        })
        assert data.status_code == 200 , (f"Smoobu Status Code {data.status_code}<br>"
                                          +f"Möglicherweise ist der API-Schlüssel fehlerhaft oder Smoodu's API ist offline.")

        parsed_data = dict(data.json())
        assert len(parsed_data["bookings"]) > 0, "Keine Buchungen im angegebenen Zeitraum. Versuche einen anderen Zeitraum."
        df = pd.DataFrame.from_records(data.json()["bookings"])
        for i in range(1,int(parsed_data["page_count"])+1):
            df = pd.concat([df,
                            pd.DataFrame.from_records(
                                get(url="https://login.smoobu.com/api/reservations",
                                    payload=
                                    {
                                        "arrivalFrom": start,
                                        "arrivalTo": end,
                                        "pageSize": 100,
                                        "page":i
                                    }).json()["bookings"]
                                )]
                           , ignore_index=True
            )


    except AssertionError as e:
        print(e)
        return e

    return pd.DataFrame.from_records(data.json()["bookings"])


# endregion


# region DataFrame manipulation
def prepare_df(df):
    """
    Prepares and cleans a DataFrame with booking data.

    Parameters:
    - df (DataFrame): The raw booking data.

    Returns:
    - DataFrame: A cleaned DataFrame with unique guest bookings and adjusted arrival and departure times.
    """

    relevant_columns = ["guestId", "type", "apartment", "modifiedAt", "adults", "children", "arrival", "departure"]
    rdf = df[relevant_columns]
    rdf = rdf.dropna(subset=["guestId"])
    rdf.loc[:, "apartment"] = rdf["apartment"].apply(lambda x: x["name"])
    rdf_unique = rdf.sort_values(['guestId', 'modifiedAt']).drop_duplicates(subset=['guestId'], keep='last')

    # add datetime:
    rdf_unique['arrival'] = pd.to_datetime(rdf_unique['arrival'])
    rdf_unique['departure'] = pd.to_datetime(rdf_unique['departure'])

    rdf_unique['arrival'] = rdf_unique['arrival'] + pd.to_timedelta('15:00:00')
    rdf_unique['departure'] = rdf_unique['departure'] + pd.to_timedelta('10:00:00')
    return rdf_unique


def prepare_cleaning_df(bookings, cleaning):
    """
    Prepares a DataFrame to manage the cleaning schedule based on bookings and cleaning days.

    Parameters:
    - bookings (DataFrame): DataFrame containing booking details.
    - cleaning (dict): Dictionary of cleaning days by apartment.

    Returns:
    - DataFrame: A schedule DataFrame including cleaning types and times.
    """
    cleaning_schedule = pd.DataFrame(
        pd.date_range(bookings['arrival'].min().date(), bookings['departure'].max().date()), columns=['date'])
    for apartment, days in cleaning.items():
        cleaning_schedule[apartment] = cleaning_schedule['date'].isin(days)
    cleaning_schedule["Number of Apartments"] = cleaning_schedule[cleaning.keys()].sum(axis=1)
    cleaning_schedule = cleaning_schedule[cleaning_schedule["Number of Apartments"] > 0]
    cleaning_schedule["arrival"] = cleaning_schedule["date"] + pd.to_timedelta('10:00:00')
    cleaning_schedule["departure"] = cleaning_schedule["date"] + pd.to_timedelta('15:00:00')

    new_rows = []
    possible_cols = list(cleaning.keys())
    actual_cols = list(set(cleaning_schedule.columns) & set(possible_cols))
    for _, row in cleaning_schedule.iterrows():
        for c in actual_cols:
            if row[c]:
                t = row.to_dict()
                t["apartment"] = c
                new_rows.append(t)

    best_clean_schedule = pd.DataFrame(new_rows)
    best_clean_schedule = best_clean_schedule.drop(
        columns=list(cleaning.keys()))
    best_clean_schedule["Number of Apartments"] = best_clean_schedule["Number of Apartments"].astype(str)
    best_clean_schedule["type"] = "cleaning"
    best_clean_schedule.drop(columns=["date"], inplace=True)
    return best_clean_schedule


def combine_dfs(bookings, cleaning):
    dfa = bookings[["arrival", "departure", "apartment", "adults", "children"]]
    dfa["type"] = "booking"
    df_new = pd.concat([dfa, cleaning]).fillna("")
    df_new.sort_values("arrival", inplace=True)
    return df_new


def create_dfs(df, max_days_uncleaned, start, end):
    bookings = prepare_df(df)
    cleaning = return_best_cleaning_days(bookings,max_days_uncleaned)
    cleaning_schedule = prepare_cleaning_df(bookings, cleaning)
    all_appointments = combine_dfs(bookings, cleaning_schedule)

    best_days = best_cleaning_day_table(cleaning_schedule)
    best_days_with_numbers = get_number_of_people(best_days, bookings)

    all_appointments = all_appointments.astype(str)
    best_days_with_numbers.sort_values("Datum", ascending=True, inplace=True)
    best_days_with_numbers = best_days_with_numbers[best_days_with_numbers["Datum"].between(start,end)]
    best_days_with_numbers["Datum"] = [datetime.strftime(t, "%d.%m.%y") for t in
                                      best_days_with_numbers["Datum"].tolist()]
    for c in all_appointments.columns:
        all_appointments[c] = all_appointments[c].astype(str)

    return all_appointments, best_days_with_numbers, cleaning_schedule


# endregion


# region Algorithms
def return_best_cleaning_days(df, max_days_uncleaned):
    """
    Determines the best cleaning days for each apartment based on booking gaps.

    Parameters:
    - df (DataFrame): The DataFrame containing booking information.

    Returns:
    - dict: A dictionary with apartments as keys and lists of optimal cleaning dates as values.
    """

    # Get a list of all unique apartments
    all_apartments = df['apartment'].unique()

    # Get the date range
    date_range = pd.date_range(df['arrival'].min().date(), df['departure'].max().date())

    # Create a dictionary to store cleaning days for each apartment
    cleaning_days = {apartment: [] for apartment in all_apartments}

    # Iterate through each apartment
    for apartment in all_apartments:
        # Get bookings for the current apartment
        apartment_bookings = df[df['apartment'] == apartment].sort_values('arrival')
        # Iterate through bookings for the current apartment
        for i in range(len(apartment_bookings)):
            # Get departure date of current booking
            departure_date = apartment_bookings.iloc[i]['departure'].date()
            # Get arrival date of next booking (if any)
            try:
                arrival_date = apartment_bookings.iloc[i + 1]['arrival'].date()
            except IndexError:
                arrival_date = date_range[-1].date() + pd.Timedelta(days=1)  # End of date range

            # Check if arrival date is longer than max days without clean
            if (arrival_date-departure_date).days > max_days_uncleaned:
                arrival_date = departure_date + pd.Timedelta(max_days_uncleaned)

            # Find the best cleaning day within the available window
            cleaning_day = departure_date  # Default to departure date
            # If there's a gap between bookings, find the day with the most free apartments
            if departure_date <= arrival_date:
                max_free_apartments = 0
                best_cleaning_day = None
                for day in pd.date_range(departure_date, arrival_date):
                    occupied_apartments = set()
                    for index, row in df.iterrows():
                        if row['arrival'].date() < day.date() < row['departure'].date():
                            occupied_apartments.add(row['apartment'])
                    num_free_apartments = len(all_apartments) - len(occupied_apartments)
                    if num_free_apartments > max_free_apartments:
                        max_free_apartments = num_free_apartments
                        best_cleaning_day = day.date()

                cleaning_day = best_cleaning_day if best_cleaning_day else cleaning_day

            # Add the cleaning day to the dictionary
            cleaning_days[apartment].append(cleaning_day)
    return cleaning_days


def get_number_of_people(best_days, bookings):
    bookings = bookings[["arrival", "apartment", "adults", "children"]]
    bookings.sort_values("arrival", ascending=True, inplace=True)
    bookings["date"] = bookings["arrival"].dt.date
    bookings["people"] = (bookings["adults"] + bookings["children"]).astype(int)
    bookings = bookings[["date", "apartment", "people"]]
    dfa_p = bookings.pivot(index="date", columns="apartment", values="people").fillna(method="bfill")
    dfa_p.fillna(0, inplace=True)

    dfa_p[dfa_p.columns] = dfa_p[dfa_p.columns].astype(int)

    dfa_p.reset_index(inplace=True)
    dfa_p.sort_values("date", ascending=True, inplace=True)
    dfa_p["date"] = [datetime.strftime(t, "%d.%m.%y") for t in dfa_p["date"].tolist()]
    dfa_p = dfa_p.rename_axis(None, axis=1)
    #dfa_p = dfa_p.iloc[1:]
    dfa_p["date"] = [datetime.strptime(k, "%d.%m.%y") for k in dfa_p["date"].tolist()]

    def nearest(items, pivot):
        return min(items, key=lambda x: abs(x - pivot))

    rows = []
    for i, r in best_days.iterrows():
        try:
            r["Datum"] = datetime.strptime(r["Datum"], "%d.%m.%y")
            n_date = nearest(dfa_p["date"], r["Datum"])
            values = dfa_p[dfa_p["date"] == n_date]
        except (KeyError, IndexError):
            pass
        cols = best_days.columns[1:]
        for c in cols:
            if r[c] == "Reinigung":
                v = values[c].item()
                if v:
                    r[c] = f"Reinigung ({v} Personen)"
                else:
                    r[c] = f"Reinigung (# Personen folgt)"
        rows.append(r)
    cleaning_with_people = pd.DataFrame(rows)
    return cleaning_with_people


def best_cleaning_day_table(df):
    dfa = df[["arrival", "apartment"]]
    dfa.columns = ["Datum", "Apartment"]
    apartments = dfa["Apartment"].unique()
    dfa.sort_values("Datum", inplace=True)
    dfa["Datum"] = [datetime.strftime(t, "%d.%m.%y") for t in dfa["Datum"].tolist()]
    dfa_p = dfa.pivot(index="Datum", columns="Apartment", values="Apartment")
    dfa_p.fillna("-")
    for apartment in apartments:
        dfa_p[apartment].replace(apartment, "Reinigung", inplace=True)
    dfa_p.reset_index(inplace=True)
    return dfa_p


# endregion


# region Exports
def create_pdf(fig, table):
    os.makedirs("tmp", exist_ok=True)
    tab = plt.figure()

    ax = tab.add_subplot(111)
    table = pd.DataFrame.from_records(table)
    table.replace("nan","-",inplace=True)
    cell_text = []
    for row in range(len(table)):
        cell_text.append(table.iloc[row])

    ax.table(cellText=cell_text, colLabels=table.columns, loc='center')

    ax.axis('off')

    pdf = matplotlib.backends.backend_pdf.PdfPages(os.path.join("tmp", "table.pdf"))

    pdf.savefig(tab, dpi=1000)

    pdf.close()

    fig = go.Figure(fig)
    fig.update_layout(

        paper_bgcolor="white",
        xaxis=dict(color="black"),
        yaxis=dict(color="black"),

        template="plotly_white",
    )
    fig.update_layout(
        width=3000,
        height=500,
    )
    pio.write_image(fig,os.path.join("tmp", "figure.pdf"),width=2500, height=500)
    merger = PdfMerger()
    merger.append(os.path.join("tmp", "figure.pdf"))
    merger.append(os.path.join("tmp", "table.pdf"))
    merger.write(os.path.join("tmp", "putzplan.pdf"))
    merger.close()


# endregion


# region AppConfig
def set_config(config_dict):
    global CONFIG
    CONFIG = config_dict
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, ensure_ascii=False, indent=4)

def get_config():
    return CONFIG

def set_or_load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            CONFIG.update(json.load(f))
    except FileNotFoundError:
        #CONFIG.update()
        pass

# endregion