import datetime
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
app = Flask(__name__)

""""Usage 
http://localhost:5001/calculate_energy_consumption?starting_date=2022-01-06&day_shifting=Enabled&starting_hour=20&car_battery_capacity=82&end_date=2023-04-06&end_hour=8&daily_average_electricity_consumption=10
"""


def day_left(current_charge, bat_cap, consumption):
    kwh_left = (bat_cap * (current_charge-20)/100)

    return int(kwh_left/consumption)


def days_between(date1, date2):
    date1 = datetime.datetime.strptime(date1, '%Y-%m-%d')
    date2 = datetime.datetime.strptime(date2, '%Y-%m-%d')
    return (date2 - date1).days


def find_max_ren_tot_rate_bus(df, next_days, daily_consumption, date_index, increment):
    kw_renewed_bus = []
    kw_charged_bus = []
    renewability_rates_bus = []

    for day_number in range(0, next_days):
        start_index = date_index + 24*day_number
        end_index = date_index+increment + 24*day_number
        renewability_rate = df.loc[start_index:
                                   end_index]['ren/tot'].values.flatten()

        renewability_rates_bus.append(max(renewability_rate))
        kw_charged_bus.append(daily_consumption * (day_number+1))

        kw_renewed_bus.append(daily_consumption * (day_number+1)
                              * renewability_rates_bus[-1] / 100)

    max_value = max(renewability_rates_bus)

    max_index = renewability_rates_bus.index(max_value)

    return kw_renewed_bus[max_index], max_index, kw_charged_bus[max_index]


def find_max_ren_tot_rate(starting_date, df_plot, df, next_days, daily_consumption, date_index, increment):
    kw_renewed = []
    kw_charged = []
    renewability_rates = []
    day_inc = df_plot.loc[(
        df_plot['Date'] == pd.Timestamp(starting_date))].shape[0]

    for day_number in range(0, next_days):

        start_index = date_index + 24*day_number
        end_index = date_index+increment + 24*day_number

        renewability_rate = df.loc[start_index:
                                   end_index]['ren/tot'].values.flatten()

        renewability_rates.append(max(renewability_rate))

        kw_renewed.append(daily_consumption * (day_number+1)
                          * renewability_rates[-1] / 100)
        kw_charged.append(daily_consumption * (day_number+1))

    print(f"ren rates of days: {renewability_rates}")
    print(f"kwh renewed rates of days: {kw_renewed}")

    max_value_ren_based = max(renewability_rates)
    max_index = renewability_rates.index(max_value_ren_based)
    print(f"max_index: {max_index}")

    try:
        if (max_index == 0):
            print("Index = 0")
            copy_renewability_rates = renewability_rates
            renewability_rates.sort()
            max_index = copy_renewability_rates.index(renewability_rates[-2])

    except:
        print(f"max index == 0 and the day left is 1 ")
        max_index += 1
        kw_renewed.append(kw_renewed[0])
        kw_charged.append(kw_charged[0])

    return kw_renewed[max_index], max_index, kw_charged[max_index]


@app.route('/calculate_energy_consumption', methods=['GET'])
def calculate_energy_consumption():
    starting_date = request.args.get('starting_date', type=str)
    day_shifting = request.args.get('day_shifting', type=str)
    starting_hour = request.args.get('starting_hour', type=int)
    car_battery_capacity = request.args.get('car_battery_capacity', type=int)
    end_date = request.args.get('end_date', type=str)
    end_hour = request.args.get('end_hour', type=int)
    daily_average_electricity_consumption = request.args.get(
        'daily_average_electricity_consumption', type=int)

    # Load data
    df_plot = pd.read_csv('df_plot_full.csv')
    df_plot['Date'] = pd.to_datetime(df_plot['Date'], format='%d.%m.%Y')
    # ===================================================================
    first_index = df_plot.loc[(df_plot['Date'] == pd.Timestamp(starting_date))]
    first_index = first_index.loc[(first_index['Hour'] == starting_hour)]
    first_index = first_index.index[0]

    second_index = df_plot.loc[(df_plot['Date'] == pd.Timestamp(end_date))]
    second_index = second_index.loc[(second_index['Hour'] == end_hour)]
    second_index = second_index.index[0]

    hour_difference = second_index - first_index
    hour_difference

    if (starting_hour > end_hour):  # 23 -07
        increment = 24-starting_hour + end_hour
        df_plot = df_plot[df_plot['Hour'].between(
            starting_hour, 24) | df_plot['Hour'].between(0, end_hour)]
    elif (end_hour > starting_hour):
        increment = end_hour - starting_hour  # 07-01
        df_plot = df_plot[df_plot['Hour'].between(starting_hour, end_hour)]

    else:
        increment = 24
    print(f"incremenet : {increment}")

    date_index = df_plot.loc[(df_plot['Date'] == pd.Timestamp(starting_date))]

    date_index = date_index.loc[(date_index['Hour'] == starting_hour)]
    date_index.index[0]

    start_index = first_index
    end_index = second_index

    if (day_shifting == 'Enabled'):
        charged_percs = []
        starting_dates = []
        ren_rates = []
        charge_day = starting_date
        max_index = start_index
        start_index_clone = start_index
        current_charge = 80

        try:
            while (True):
                print("1")
                day_to_next_charge = day_left(
                    current_charge, car_battery_capacity, daily_average_electricity_consumption)
                print("2")

                day_between_dates = days_between(starting_date, end_date)
                print("3")

                print(f"day_between_dates: {day_between_dates}")

                if day_between_dates < day_to_next_charge:
                    print('HEREEEEEEE')
                    day_to_next_charge = day_between_dates
                print("5")

                try:
                    max_kw_renewed, max_index, kw_consumed = find_max_ren_tot_rate(
                        starting_date, df_plot, df_plot, day_to_next_charge, daily_average_electricity_consumption, start_index, increment)
                except Exception as e:
                    print(f"An exception occurred: {str(e)}")
                    print("Bitti")
                    break
                print(
                    f"max index ,kw_consumed, max renewed: {max_index, kw_consumed, max_kw_renewed}")

                if max_index == 0:
                    max_index += 1  # HERE

                start_index += max_index*24
                print(f"start_index = {start_index}")

                ren_rates.append(max_kw_renewed)
                if start_index > end_index:
                    print(f"EXITED SUCCESSFULLY :{start_index}, {end_index}")
                    break

                current_charge = 80
                print("============================")
        except Exception as e:
            print(f"exception: {e}")
            print(f"final cahrge day: {starting_date}")

    else:
        print("BUS SELECTED")
        charged_percs = []
        starting_dates = []
        ren_rates = []
        charge_day = starting_date
        max_index = start_index
        start_index_clone = start_index
        try:
            while (True):
                # day_to_next_charge = day_left(80, car_battery_capacity,daily_average_electricity_consumption)
                day_to_next_charge = 1  # todo: this was wrong before
                try:
                    max_kw_renewed, max_index, kw_consumed = find_max_ren_tot_rate_bus(
                        df_plot, day_to_next_charge, daily_average_electricity_consumption, start_index, increment)
                except Exception as e:
                    print(f"An exception occurred: {str(e)}")
                    print("Bitti")
                    break

                print(
                    f"max index ,kw_consumed,max_kwh renewed: {max_index, kw_consumed, max_kw_renewed}")

                start_index += 24  # ??  increment

                ren_rates.append(max_kw_renewed)
                if start_index > end_index:
                    print(
                        f"EXITED SUCCESSFULLY :startin : {start_index}, end in {end_index}")
                    break

                current_charge = 100
                print("============================")
        except:
            print(f"final cahrge day: {starting_date}")

    df_normal_bus = df_plot.loc[start_index_clone:end_index]

    df_normal_bus = df_normal_bus[df_plot['Hour'] == starting_hour]

    print(
        f" avergae consumption data :{daily_average_electricity_consumption}")
    df_normal_consumed_bus = (
        df_normal_bus['ren/tot'] * daily_average_electricity_consumption/100)
    # ===================================================================
    total_energy_consumed = daily_average_electricity_consumption * \
        len(df_normal_consumed_bus)
    renewable_Data = ren_rates
    normal_Data = df_normal_consumed_bus.tolist()
    print(renewable_Data)
    renewable_consumed = np.sum(ren_rates)
    return jsonify({
        'total_energy_consumed': f"{total_energy_consumed}",
        "renewable_consumed": f"{renewable_consumed}",
        "renewable_data": renewable_Data,
        "normal_data": normal_Data})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
