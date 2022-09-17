# TODO use try/except to sanitize bad input, put up flash warnings
# ~~~~~~~~~~  Importing Packages and Setting Variables  ~~~~~~~~~~
import base64
import csv
import pandas as pd

from flask import Flask, flash, render_template, request, url_for, send_file
from io import BytesIO
from matplotlib.figure import Figure
from numpy import arange as npar

columns = ["day_num", "perc_of_pop"]
calculated_data = []
chart_subtitle = ""
infected_decimal = ""
infection_rate = ""
recovery_days = ""
vac = 0



# ~~~~~~~~~~  This is the data processing part of the program  ~~~~~~~~~~
# This is the function that process the input and outputs CSV data
def sir_model(inf_pop, inf_rate, rec_days, v_info):
    # function variables
    global chart_subtitle
    infected_population = inf_pop
    b: float = inf_rate
    susceptible_population: float = (1 - v_info) - infected_population
    recovered_population: float = 0.
    day = 0
    recovery_rate = 1 / rec_days
    chart_subtitle = f"Infection Rate = {int((b)*100)}%, Recovery Rate = {int(rec_days)} days, \nEffective Vaccination Rate = {int(v_info*100)}%"

    """ This while loop runs the SIR model according to the input values entered into the browser.
    the multiplication and division limit the csv data to two decimal places. """
    while (int(infected_population * 10000) / 100) > 0.05 and day < 365:
        day += 1
        new_infections = b * susceptible_population * infected_population
        susceptible_population -= new_infections
        infected_population += new_infections
        if day >= rec_days:
            recovered_population += infected_population * recovery_rate
            infected_population -= infected_population * recovery_rate
        calculated_data.append([day, int(infected_population * 10000) / 100])

    # This writes a .csv datafile of the model output
    with open('csv_delivery.csv', 'w') as file:
        output = csv.writer(file)
        output.writerow(columns)
        output.writerows(calculated_data)


# def input_check(form_value):
#     if not form_value.isnumeric():
#         return True
#     elif 0 < form_value <= 100:
#         pass
#     else:
#         return True

# ~~~~~~~~~~~~~~~~~  This is the web part of the program  ~~~~~~~~~~~~~~~~~
app = Flask(__name__)
app.secret_key = "thisIsASecretKey"


# The front page function implements a web form for starting values and renders the home page
@app.route("/", methods=["GET", "POST"])
def front_page():
    global infected_decimal, infection_rate, recovery_days, vac
    error_state = False
    error_message = "Please enter a whole number between"
    # This if/else condition determines whether to post the homepage or import form data and then redirect
    if request.method == "POST":
        vax_state = request.form['vax_radio']
        # This if/else condition is only necessary if there is a vaccine in use.
        if vax_state == "True":
            try:
                vp = request.form["vax_per"]
                ve = request.form["vax_eff"]
                vac = float((float(vp) / 100) * (float(ve) / 100))
            except ValueError:
                error_state = True
        else:
            vac = 0
        try:
            infected_decimal = float(request.form['inf_perc']) / 100
            infection_rate = float(request.form["inf_rate"]) / 100
            recovery_days = float(request.form["rec_days"])
            sir_model(infected_decimal, infection_rate, recovery_days, vac)
        except ValueError:
            error_state = True
        else:
            return results_page()
        finally:
            if error_state:
                flash("Please enter numeric values between 1 and 100 with up to two decimal places")
                return render_template('index.html')
    else:
        return render_template("index.html")


# This function generates and posts the chart. It also links to downloadable csv and png files
def results_page():
    global calculated_data

    # Instantiate a Pandas dataframe from the output of the SIR model
    df = pd.DataFrame(calculated_data, columns=columns)

    # Generate the chart image
    fig = Figure(dpi=150, figsize=(7, 4))
    ax = fig.subplots()
    ax.plot(df.day_num, df.perc_of_pop, color="red")
    ax.set_xlabel("Day Number")
    ax.set_ylabel("Percentage of Population Currently Infected")
    ax.set_title(chart_subtitle)
    # Dynamically change the chart's tick markings depending on the size of the data set
    # x-axis
    if df.day_num.max() <= 100:
        ax.set_xticks(npar(0, len(df.day_num) + 1, step=5))
    else:
        ax.set_xticks(npar(0, len(df.day_num) + 1, step=20))
    # y-axis
    if df.perc_of_pop.max() >= 10:
        ax.set_yticks(npar(0, (df.perc_of_pop.max() + 5), step=10))
    else:
        ax.set_yticks(npar(0, (df.perc_of_pop.max() + 1), step=1))
    # Saves the image for later download
    fig.savefig("speedy_delivery.png", format='png')
    # removes extra caption for display
    ax.set_title(" ")
    # loads the image into a buffer for web display
    buf = BytesIO()
    fig.savefig(buf, format='png')
    # noinspection PyTypeChecker
    image_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    # Clears the underlying data in case the user generates a new chart
    calculated_data = []
    # return f"<img src='data:image/png;base64,{image_data}'/>"
    return render_template("results.html", subtitle=chart_subtitle, picture=image_data)


# Delivers csv
@app.route("/download1")
def download_page_1():
    return send_file("csv_delivery.csv", as_attachment=True)


# Delivers png
@app.route("/download2")
def download_page_2():
    return send_file("speedy_delivery.png", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)


