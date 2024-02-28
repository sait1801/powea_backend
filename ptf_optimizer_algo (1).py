ptf = {
    '01': 2299,
    '02': 1780,
    '03': 1600,
    '04': 2000,
    '05': 2199,
    '06': 2499,
    '07': 1450,
    '08': 2700,
    '09': 2626,
    # '10': 1300,
    # '11': 1000,
    # '12': 500,
    # '13': 980,
    # '14': 1175,
    # '15': 1495,
    # '16': 1940,
    # '17': 2200,
    '18': 2700,
    '19': 2700,
    '20': 1400,
    '21': 2700,
    '22': 2700,
    '23': 2700,
}


## Vehicle ids - max bat kwh - needed kwh to charge
vehicles = {
    'id1' : [100,70],
    'id2' : [100,80],
    'id3' : [80,30],
    'id4' : [52,20],
    'id5' : [52,12],
    'id6' : [52,22],
    'id7' : [52,32],
    'id8' : [52,42],
    'id9' : [42,30],
    'id10' : [150,100],

}

#This is the maximum total grid capacity that is WANTED by the grid algo

#Individual Charger Capacity
charger_cap = 22
max_grid_cap = 22*30 #kW total grid- normally 220

import random

vehicles = {
    'id1' : [100,70],
    'id2' : [100,80],
    'id3' : [80,30],
    'id4' : [52,20],
    'id5' : [52,12],
    'id6' : [52,22],
    'id7' : [52,32],
    'id8' : [52,42],
    'id9' : [42,30],
    'id10' : [150,100],
}

# Generate data for vehicles 11 to 100
for i in range(11, 101):
    # Generate a random max capacity between 70 and 150
    max_capacity = random.randint(70, 150)

    # Generate a random needed charge between 10% and 70% of the max capacity
    needed_charge = random.randint(int(max_capacity * 0.1), int(max_capacity * 0.7))

    # Add the vehicle to the dictionary
    vehicles[f'id{i}'] = [max_capacity, needed_charge]

# Now the 'vehicles' dictionary contains data for 100 vehicles

"""###PTF Saatleri Sıralama Sorting"""

# Sort the dictionary by values in descending order
sorted_dict_desc = dict(sorted(ptf.items(), key=lambda item: item[1]))

# Print the sorted dictionary in descending order
print(sorted_dict_desc)

"""###Araçların İhtiyaç Duyduğu Toplam KWH"""

# Initialize a variable to store the sum of "needend kwh"
sum_needend_kwh = 0
single_needs = []
# Iterate through the dictionary and sum the second element of each value list
for vehicle_id, values in vehicles.items():
    single_needs.append(values)
    sum_needend_kwh += values[1]

# Print the sum of "needend kwh"
print("Sum of 'needend kwh':", sum_needend_kwh)


if(max_grid_cap*len(ptf.values()) < sum_needend_kwh):
  print("ERROR IN MAX CAPACITY")

elif(max(single_needs)[0] > charger_cap*len(ptf.values())):
  print("ERROR IN SINGLE CAPACITY")

else:
  print("ALL CHECKS DONE")

"""###İhtiyaç Duyulan Saat Ve Dakika"""

needed_hours = int(sum_needend_kwh/max_grid_cap)
neede_minutes = round(((sum_needend_kwh%max_grid_cap)/max_grid_cap)*60)
print("needed hours:", needed_hours)
print("minutes: ",neede_minutes)
ptf_index = needed_hours +1
print("kaç adet saat lazım :",ptf_index)


##add if check if needed hours > 12 hours or len of dict. FAIL IT

"""###En Uygun PTF Saatlerin Seçilmesi"""

from itertools import islice
# Get the first 5 values from the sorted dictionary
selected_hours = dict(islice(sorted_dict_desc.items(), ptf_index))

# Print the first 5 values
print("Selected Hours:", selected_hours)

"""#Araçların Önem Sırası"""

def importance(vehicles_dict):
  # Calculate the ratio of charge needed over total battery capacity
  ratios = {car_id: charge_needed / total_capacity for car_id, (total_capacity, charge_needed) in vehicles_dict.items()}

  # Sort the cars by the ratio from smallest to highest
  sorted_cars = sorted(ratios.items(), key=lambda x: x[1],reverse= True)
  print(sorted_cars)
  urgent_cars = []
  # Print the sorted cars
  for car_id, ratio in sorted_cars:
      if ratio < 1: ## to make sure that if an car is fully charged, remove it from the importance matrix
        urgent_cars.append(car_id)
      print(f'{car_id}: {ratio:.2f}')
  return urgent_cars

# urgent_ids = importance(vehicles)

# urgent_ids

"""#Şarj Güncelleme Algortiması"""

def charge_update(grid_cap, charger_kw ,ev_list,ids_to_update,hour_coefficient):
  charge = []
  number_of_evs_tobe_charged = int(grid_cap/charger_kw)
  for vehicle_id in ids_to_update[:number_of_evs_tobe_charged]:
    if vehicle_id in ev_list:
      if  ev_list[vehicle_id][1] >  charger_kw * hour_coefficient:
        ev_list[vehicle_id][1] -= charger_kw * hour_coefficient #60 mins : 1 and 30 mins = 0.5
        # print(f"charged : {charger_kw * hour_coefficient}, id : {vehicle_id} ")
        charge.append((vehicle_id,charger_kw * hour_coefficient))

      else:
        # print(f"charged : {ev_list[vehicle_id][1]}, id : {vehicle_id} ")
        charge.append((vehicle_id,ev_list[vehicle_id][1]))
        ev_list[vehicle_id][1] =0 #60 mins : 1 and 30 mins = 0.5


  return ev_list,charge

# vehicle_new = charge_update(max_grid_cap, charger_cap, vehicles, urgent_ids,1)

"""#Main Kod"""

vehicle_new = []
counter = 0
charges = []
for index in range(ptf_index):
  if counter == ptf_index:
    coefficient = neede_minutes/60
  else:
    coefficient = 1

  urgent_ids = importance(vehicles)
  vehicles,charge_item = charge_update(max_grid_cap, charger_cap, vehicles, urgent_ids,coefficient)
  charges.append(charge_item)
  print()
  if(len(urgent_ids) == 0):
    break

charges

"""#Demo"""

!pip install plotly

list(selected_hours.keys())
import pandas as pd
import plotly.express as px

# Create an empty DataFrame with columns as vehicle ids and rows as hours sorted
# df = pd.DataFrame(columns=list(vehicles.keys()), index=sorted(list(selected_hours.keys())))
df = pd.DataFrame(columns=list(vehicles.keys()), index=list(selected_hours.keys()))

# # Fill the DataFrame with charging amounts
# for hour in sorted(list(selected_hours.keys())):
#   for hour_data in charges:
#       for vehicle_id_data, kw_charged_data in hour_data:
#           print(f"id: {vehicle_id_data}, kw : {kw_charged_data}")
#           df.loc[hour,vehicle_id_data] = kw_charged_data
#       print()

# Fill the DataFrame with charging amounts
for index,hour_data in enumerate(charges):
  for vehicle_id_data, kw_charged_data in hour_data:
    # print(f"id: {vehicle_id_data}, kw : {kw_charged_data}")
    # df.loc[sorted(list(selected_hours.keys()))[index],vehicle_id_data] = kw_charged_data
    df.loc[list(selected_hours.keys())[index],vehicle_id_data] = kw_charged_data

  # print()


# Fill NaN values with 0
df.fillna(0, inplace=True)

# Display the DataFrame
print(df)

"""#ShowCase"""

plotting = pd.DataFrame(df, index=list(selected_hours.keys()))

# Reshape the dataframe for plotting
plotting = plotting.reset_index().melt(id_vars='index', var_name='ID', value_name='Value')
plotting['index'] = pd.to_datetime(plotting['index'], format='%H').dt.time

# Create a figure and plot the histogram
fig = px.bar(plotting, x='index', y='Value', color='ID',
             title='Araç Şarj Planları', labels={'index': 'Saatler'})
fig.update_layout(yaxis_title='kW', barmode='stack')

# Show the plot
fig.show()

"""##Ne Kadar Kar ettiriyor"""

