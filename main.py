# TODO figure out matplot lab and NOT PYPLOT
# TODO figure out how to get/give the csv file to the client.
# TODO use try/except to sanitize bad input, put up flash warnings
# TODO go directly to a pandas dataframe instead of a csv file

import csv
from datetime import datetime
from flask import Flask, render_template, request, url_for
import base64
from io import BytesIO
import pandas as pd
from matplotlib.figure import Figure
import numpy as np

# TODO try to make the import statements tighter and more specific but only after fully functional


columns = ["day_num", "perc_of_pop"]
calculated_data = []
now = datetime.now()

infected_decimal = ""
infection_rate = ""
recovery_days = ""
vac = 0


# This is the function that process the input and outputs a CSV
def sir_model(inf_pop, inf_rate, rec_days, v_info):
    infected_population = inf_pop
    b: float = inf_rate
    susceptible_population: float = (1 - v_info) - infected_population
    recovered_population: float = 0.
    day = 0
    recovery_rate = 1 / rec_days
    # the while conditions limit to 2 decimal places and the day is to just limit data
    title = f"SIR Model: Infection Rate = {b}, Recovery Rate = {rec_days} days, Effective Vaccination Rate = {v_info}"
    while (int(infected_population * 10000) / 100) > 0.05 and day < 100:
        day += 1
        new_infections = b * susceptible_population * infected_population
        susceptible_population -= new_infections
        infected_population += new_infections
        if day >= rec_days:
            recovered_population += infected_population * recovery_rate
            infected_population -= infected_population * recovery_rate
        calculated_data.append([day, int(infected_population * 10000) / 100])
    print("done this")

    # with open(f"KEY_{now.ctime()}.csv", 'w') as file:
    #     file.write(title)
    #
    # with open(f'SIR_{now.ctime()}.csv', 'w') as file:
    #     output = csv.writer(file)
    #     output.writerow(columns)
    #     output.writerows(calculated_data)


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
        print('done that')
        return results_page()

    else:
        return render_template("index.html")


def results_page():
    df = pd.DataFrame(calculated_data, columns=columns)
    fig = Figure()
    ax = fig.subplots()
    ax.plot(df.day_num, df.perc_of_pop, color="red")
    ax.set_xlabel("Day Number")
    ax.set_ylabel("Percentage of Population Currently Infected")
    # ax.set_title(f"SIR Model: Infection Rate = {b}, Recovery Rate = {rec_days} days, Effective Vaccination Rate = {v_info}")
    ax.set_title("SIR Epidemiology Model")
    ax.set_xticks(np.arange(0, len(df.day_num) + 1, step=5))
    ax.set_yticks(np.arange(0, (df.perc_of_pop.max() + 5), step=5))
    buf = BytesIO()
    fig.savefig(buf, format='png')
    image_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    buf.flush()
    ax.clear()
    return f"<img src='data:image/png;base64,{image_data}'/>"
    # return f"<img src='static/sir_web_fig_02.png'/>"

if __name__ == '__main__':
    app.run(debug=True)
