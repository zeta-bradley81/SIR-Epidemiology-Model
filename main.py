#  TODO CSS Style Sheet
#  TODO figure out graphing - Am i better off with API or NumPy?
# If numpy, I think I need to save it as a graphic and then import the graphic into my page
# TODO figure out how to get/give the csv file to the client.
# TODO use try/exept to sanitize bad input, put up flash warnings

import csv
from datetime import datetime
from flask import Flask, render_template, request, url_for

fields = ["Day", "% of Pop"]
data = []
now = datetime.now()

infected_decimal = ""
infection_rate = ""
recovery_days = ""
vac = 0


def sir_model(inf_pop, inf_rate, rec_days, v_info):
    infected_population = inf_pop
    b: float = inf_rate
    susceptible_population: float = (1 - v_info) - infected_population
    recovered_population: float = 0.
    day = 0
    recovery_rate = 1 / rec_days
    # the while conditions limit to 2 decimal places and the day is to just limit data
    title = f"SIR Model: Infection Rate = {b}, Recovery Rate = {rec_days} days, Effective Vaccination Rate = {v_info}"
    while (int(infected_population*10000)/100) > 0.05 and day < 100:
        day += 1
        new_infections = b * susceptible_population * infected_population
        susceptible_population -= new_infections
        infected_population += new_infections
        if day >= rec_days:
            recovered_population += infected_population * recovery_rate
            infected_population -= infected_population * recovery_rate
        data.append([day, int(infected_population*10000)/100])

    with open(f"KEY_{now.ctime()}.csv", 'w') as file:
        file.write(title)

    with open(f'SIR_{now.ctime()}.csv', 'w') as file:
        output = csv.writer(file)
        output.writerow(fields)
        output.writerows(data)


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
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
