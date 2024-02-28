from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)
""""Usage: http://localhost:5000/run_code?starting_date=2022-01-01&starting_hour=19&end_date=2023-02-01&end_hour=8
"""


@app.route('/run_code', methods=['GET'])
def run_code():
    starting_date = request.args.get(
        'starting_date', default='2022-01-01', type=str)
    starting_hour = request.args.get('starting_hour', default=19, type=int)
    end_date = request.args.get('end_date', default='2023-02-01', type=str)
    end_hour = request.args.get('end_hour', default=8, type=int)
    how_many_hours = request.args.get('hours', default=1, type=int)
    how_many_kw = request.args.get('kw_need', default=10, type=int)

    # Data Loading
    data = pd.read_csv('ptf-2-years-for-gui.csv')
    print(f"data size : {data.shape}")
    df = data.copy()

    # Main Code
    df['PTF (USD/MWh)'] = df['PTF (USD/MWh)'].str.replace('.', '')
    df['PTF (USD/MWh)'] = df['PTF (USD/MWh)'].str.replace(',', '.')
    df['PTF (USD/MWh)'] = pd.to_numeric(df['PTF (USD/MWh)'], errors='coerce')
    df['Datetime'] = pd.to_datetime(
        df['Tarih'] + ' ' + df['Saat'], format='%d/%m/%Y %H:%M')

    mask_date = (df['Datetime'] >= starting_date) & (
        df['Datetime'] <= end_date)
    hours = list(range(starting_hour, 24)) + list(range(0, end_hour + 1))
    mask_hour = df['Datetime'].dt.hour.isin(hours)
    filtered_df = df[mask_hour]

    # Now you have the filtered DataFrame between the specified dates
    # Step 3: Find the first index where the date matches '2023-01-01'
    formatted_start_date = datetime.strptime(
        starting_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    formatted_end_date = datetime.strptime(
        end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    if len(str(starting_hour)) != 2:
        saat_start = '0'+str(starting_hour)
    else:
        saat_start = str(starting_hour)

    if len(str(end_hour)) != 2:
        saat_end = '0'+str(end_hour)
    else:
        saat_end = str(end_hour)
    print(str(end_hour))

    first_index = df[(df['Tarih'] == formatted_start_date) &
                     (df['Saat'] == saat_start + ':00')].index[0]
    # first_index = df[(df['Tarih'] == formatted_start_date) & (df['Saat'] == str(starting_hour) + ':00')].index
    last_index = df[(df['Tarih'] == formatted_end_date) &
                    (df['Saat'] == saat_end + ':00')].index[-1]
    print(first_index)
    print(last_index)
    # last_index = df[(df['Tarih'] == formatted_end_date) & (df['Saat'] == str(end_hour) + ':00')].index
    # print(df[(df['Tarih'] == formatted_end_date) & (df['Saat'] == str(end_hour) + ':00')].index)

    filtered_df = filtered_df.loc[first_index:last_index, :]

    # filtered_df.loc[15979,:].head(5)

    # filtered_df.loc[15992,:].head(5)

    """end_index and start_index finder fucntions

    """

    if (starting_hour > end_hour):  # 23 -07
        increment = 24-starting_hour + end_hour
    elif (end_hour > starting_hour):
        increment = end_hour - starting_hour  # 07-01

    else:
        increment = 24
    print(f"incremenet : {increment}")

    """The starting date should have hour 19:00 so lets take the starting row as 10148"""

    days = last_index-first_index
    days/24

    # 5 ağaç arasınad 4 mesafe vardır mantığı
    unique_day_numbers = filtered_df['Datetime'].dt.date.nunique()-2
    unique_day_numbers

    # TESTER these two values must be same rigth ?
    # assert(days/24 == unique_day_numbers)

    best_ptf_df = pd.DataFrame(columns=['datetime', 'sum of best 3 values'])

    first_index

    last_index

    filtered_df.loc[first_index:last_index].head(30)

    unique_day_numbers

    print(list(range(1)))

    if unique_day_numbers == 0:
        unique_day_numbers += 1
    for i in range(unique_day_numbers):
        # Define the range of rows you are interested in
        start_index = first_index + 24*i
        # Assuming you've calculated the 14-hour difference correctly
        end_index = start_index + increment
        print(start_index)
        print(end_index)

        # Filter the DataFrame for the specified rows
        specific_rows_df = filtered_df.loc[start_index:end_index]
        # print(specific_rows_df)
        # print('-----')

        # Find the minimum 3 values in the 'PTF (TL/MWh)' column
        min_3_values = specific_rows_df['PTF (USD/MWh)'].nsmallest(
            how_many_hours)
        # print("min_3_values")
        # print(min_3_values)
        # Sum these minimum values
        sum_of_min_3 = min_3_values.sum()
        # print("sum_of_min_3")

        # print(sum_of_min_3)

        # Create a new DataFrame with the required information
        best_ptf = pd.DataFrame([{
            # Assuming 'Datetime' is a column in df
            'datetime': df.loc[start_index, 'Tarih'],
            'sum of best 3 values': sum_of_min_3
        }])
        # best_ptf_df = best_ptf_df.append(best_ptf, ignore_index=True)
        best_ptf_df = pd.concat([best_ptf_df, best_ptf], ignore_index=True)

    print(best_ptf_df)

    """well after finding best values, make generic the mentioned parameters.
    Then find the start_index + hour sum values

    Now its time for the normal times
    """

    normal_ptf_df = pd.DataFrame(columns=['datetime', 'normal ptf values'])

    for i in range(unique_day_numbers):
        # Define the range of rows you are interested in
        start_index = first_index + 24*i
        # Assuming you've calculated the 14-hour difference correctly
        end_index = start_index + how_many_hours

        # Filter the DataFrame for the specified rows
        specific_rows_df_normal = filtered_df.loc[start_index:end_index-1]

        # Find the minimum 3 values in the 'PTF (TL/MWh)' column
        normal_3_values = specific_rows_df_normal['PTF (USD/MWh)']

        # Sum these minimum values
        normal_3 = normal_3_values.sum()

        # Create a new DataFrame with the required information
        normal_ptf = pd.DataFrame([{
            # Assuming 'Datetime' is a column in df
            'datetime': df.loc[start_index, 'Tarih'],
            'normal ptf values': normal_3
        }])
        # normal_ptf_df = normal_ptf_df.append(normal_ptf, ignore_index=True)
        normal_ptf_df = pd.concat(
            [normal_ptf_df, normal_ptf], ignore_index=True)

    print(normal_ptf_df)

    assert ((sum(normal_ptf_df['normal ptf values'] -
            best_ptf_df['sum of best 3 values'])) >= 0)
    sum(normal_ptf_df['normal ptf values'] -
        best_ptf_df['sum of best 3 values'])*how_many_kw/(1000*how_many_hours)

    print(sum(best_ptf_df['sum of best 3 values']))
    print(sum(normal_ptf_df['normal ptf values']))
    best_ptf_json = best_ptf_df['sum of best 3 values'].tolist()
    # Convert the 'normal ptf values' column to a list
    normal_ptf_json = normal_ptf_df['normal ptf values'].tolist()

    response = jsonify({
        'sum of best 3 values': sum(best_ptf_df['sum of best 3 values']),
        'sum of normal ptf values': sum(normal_ptf_df['normal ptf values']),
        'best_ptf_values': best_ptf_json,
        'normal_ptf_values': normal_ptf_json
    })
    # Allow requests from any origin (not recommended for production)
    response.headers['Access-Control-Allow-Origin'] = '*'
    # You can also specify the specific origin of your frontend application
    # response.headers['Access-Control-Allow-Origin'] = 'https://your-frontend-app.com'
    return response


if __name__ == '__main__':
    app.run(debug=True)
