import csv
from datetime import datetime

fields = ["Day", "% of Pop"]
data = []
now = datetime.now()


def sir_model(infected_population: float,
              infection_rate: float,
              recovery_rate: float,
              vaccinated_population: float = 0.,
              vaccine_efficacy: float = 1.0):
    inf = infected_population
    b: float = infection_rate
    r: float = recovery_rate
    vac: float = vaccinated_population * vaccine_efficacy
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

    with open(f"KEY_{now.ctime()}.csv") as file:
        file.write(title)

    with open(f'SIR_{now.ctime()}.csv', 'w') as file:
        output = csv.writer(file)
        output.writerow(fields)
        output.writerows(data)


sir_model(.01, 0.9, .071)
