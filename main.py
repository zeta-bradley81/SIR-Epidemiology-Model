import csv
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)


fields = ["Day", "% of Pop"]
data = []
now = datetime.now()

infected_population = ""
infection_rate = ""
recovery_rate = ""
vac = ""

@app.route("/")
def front_page():
    return render_template("index.html")


def user_input():
    global infected_population
    global infection_rate
    global recovery_rate
    global vac

    def vax_stat_func():
        vs = input("Will this model include vaccination? Please enter T or F ").lower()
        if vs != 't' and vs != 'f':
            print('Invalid Input')
            vax_stat_func()
        return vs

    def vax_input():
        vaccinated_population = ""
        vaccine_efficacy = ""
        if vaccinated_population is not float:
            try:
                vaccinated_population = float(input("What percentage of the population is vaccinated?")) / 100
            except ValueError:
                print("Please enter a number with up to two decimal places.\nFor example '43.25'")
                vax_input()
        if vaccine_efficacy is not float:
            try:
                vaccine_efficacy = float(input("The vaccine is what % effective?")) / 100
            except ValueError:
                print("Please enter a number with up to two decimal places.\nFor example '43.25'")
                vax_input()
        if vaccine_efficacy > 1.0:
            print("Efficacy cannot be higher than 100%")
            vax_input()
        return vaccinated_population * vaccine_efficacy

    if vac == "":
        vax_stat = vax_stat_func()
        if vax_stat == "t":
            vac = vax_input()
        else:
            vac = 0.0

    if infected_population is not float:
        try:
            infected_population = float(input("What percentage of the population is infected (0.01 - 100.00)?: ")) / 100
        except ValueError:
            print("Please enter a number with up to two decimal places.\nFor example '43.25'")
            user_input()

    if infection_rate is not float:
        try:
            infection_rate = float(input("What is the infection rate (0.0 = 1.0)?"))
        except ValueError:
            print("Please enter a number between 0.00 and 1")
            user_input()
        if infection_rate > 1.0:
            print("Please enter a number with up to two decimal places.\nFor example '43.25'")
            user_input()

    if recovery_rate is not float:
        try:
            recovery_rate = 1 / float(input("What is the rate of recovery in days?"))
        except ValueError:
            print("Invalid input")
            user_input()
    return infected_population, infection_rate, recovery_rate, vac


def sir_model(infected_population,
              infection_rate,
              recovery_rate,
              vac = 0.0):
    inf = infected_population
    b: float = infection_rate
    r: float = recovery_rate
    # Susceptible population
    sus: float = (1 - vac) - inf
    # Recovered population
    rec: float = 0.
    day = 0
    recovery_date = 1 // r
    # the while conditions limit to 2 decimal places and the day is to just limit data
    title = f"SIR Model: Infection Rate = {b}, Recovery Rate = {recovery_date} days, Effective Vaccination Rate = {vac}"
    while inf > 0.0001 and day < 100:
        day += 1
        today = b * sus * inf
        sus -= today
        inf += today
        if day >= recovery_date:
            rec += inf * r
            inf -= inf * r
        data.append([day, (inf * 100) // 1])

    with open(f"KEY_{now.ctime()}.csv", 'w') as file:
        file.write(title)

    with open(f'SIR_{now.ctime()}.csv', 'w') as file:
        output = csv.writer(file)
        output.writerow(fields)
        output.writerows(data)
args = user_input()
sir_model(args[0], args[1], args[2], args[3])


if __name__ == '__main__':
    app.run()