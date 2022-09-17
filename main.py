
# TODO Put in more comments for future reference
# TODO use try/except to sanitize bad input, put up flash warnings

import csv
from datetime import datetime
from flask import Flask, render_template, request, url_for, send_file
import base64
from io import BytesIO
import pandas as pd
from matplotlib.figure import Figure
import numpy as np

# TODO try to make the import statements tighter and more specific but only after fully functional


columns = ["day_num", "perc_of_pop"]
calculated_data = []
chart_subtitle = ""
now = datetime.now()

infected_decimal = ""
infection_rate = ""
recovery_days = ""
vac = 0


# This is the function that process the input and outputs a CSV
def sir_model(inf_pop, inf_rate, rec_days, v_info):
    global chart_subtitle
    infected_population = inf_pop
    b: float = inf_rate
    susceptible_population: float = (1 - v_info) - infected_population
    recovered_population: float = 0.
    day = 0
    recovery_rate = 1 / rec_days
    # the while conditions limit to 2 decimal places and the day is to just limit data
    chart_subtitle = f"Infection Rate = {b},  Recovery Rate = {rec_days} days,  Effective Vaccination Rate = {v_info}"
    # while (int(infected_population * 10000) / 100) > 0.05 and day < 100:
    while (int(infected_population * 10000) / 100) > 0.05:
        day += 1
        new_infections = b * susceptible_population * infected_population
        susceptible_population -= new_infections
        infected_population += new_infections
        if day >= rec_days:
            recovered_population += infected_population * recovery_rate
            infected_population -= infected_population * recovery_rate
        calculated_data.append([day, int(infected_population * 10000) / 100])
    print(f"day = {day}")
    with open('csv_delivery.csv', 'w') as file:
        output = csv.writer(file)
        output.writerow(columns)
        output.writerows(calculated_data)

# ~~~~~~~~~~~~~~~~~  This is the web part of the program  ~~~~~~~~~~~~~~~~~
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def front_page():
    global infected_decimal, infection_rate, recovery_days, vac
    if request.method == "POST":
        vax_state = request.form['vax_radio']
        if vax_state == "True":
            pass
            vp = request.form["vax_per"]
            ve = request.form["vax_eff"]
            vac = float((int(vp) / 100) * (int(ve) / 100))
        else:
            vac = 0
        infected_decimal = float(request.form['inf_perc']) / 100
        infection_rate = float(request.form["inf_rate"]) / 100
        recovery_days = int(request.form["rec_days"])
        sir_model(infected_decimal, infection_rate, recovery_days, vac)
        return results_page()
    else:
        return render_template("index.html")



def results_page():
    global calculated_data
    df = pd.DataFrame(calculated_data, columns=columns)
    fig = Figure(dpi=150, figsize=(7,4))
    ax = fig.subplots()
    ax.plot(df.day_num, df.perc_of_pop, color="red")
    ax.set_xlabel("Day Number")
    ax.set_ylabel("Percentage of Population Currently Infected")
    if df.day_num.max() <= 100:
        ax.set_xticks(np.arange(0, len(df.day_num) + 1, step=5))
    else:
        ax.set_xticks(np.arange(0, len(df.day_num) + 1, step=20))

    if df.perc_of_pop.max() >= 10:
        ax.set_yticks(np.arange(0, (df.perc_of_pop.max() + 5), step=10))
    else:
        ax.set_yticks(np.arange(0, (df.perc_of_pop.max() + 1), step=1))
    fig.savefig("speedy_delivery.png", format='png')
    buf = BytesIO()
    fig.savefig(buf, format='png')
    # noinspection PyTypeChecker
    image_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    buf.flush()
    ax.clear()
    calculated_data = []
    # return f"<img src='data:image/png;base64,{image_data}'/>"
    return render_template("results.html", subtitle=chart_subtitle, picture=image_data)

@app.route("/download1")
def download_page_1():
    return send_file("csv_delivery.csv", as_attachment=True)

@app.route("/download2")
def download_page_2():
    return send_file("speedy_delivery.png", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
