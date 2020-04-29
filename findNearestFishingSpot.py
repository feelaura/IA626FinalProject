# -*- coding: utf-8 -*-
"""
Created on Wen Apr 15 12:11:39 2020

@author: Xiaolan Rong
"""

import pandas as pd
from math import cos, asin, sqrt

def getRecord(zipcode):
    df = df_zipcodes.loc[df_zipcodes['Zip Code']==int(zipcode)]
    return df

def getFishingSpots(species):
    df = df_fishing_spots[df_fishing_spots['Fish Species Present at Waterbody'].str.contains(species)]
    return df.to_dict('records')

# ------------------------------------------
# ----------- Calculation ------------------
# ------------------------------------------

# Function: distance, Purpose: Calculation
# Calculates distance between two points: zipcode lat-lon and fishing spot lat-lon
# Based on Haversine Formula (found in StackOverflow)
# Uses math library
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295  #Pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a)) #2*R*asin..

# Function: closest, Purpose: Calculation
# Runs distance function to given fishing spot dataset
# Returns fishing spot data with stocking trout number and smallest distance to the given zipcode
def closest(data, zipcode):
    dl = []
    for p in data:
        ap = {
        'zipcode': zipcode['Zip Code'],
        'country': zipcode['Country'],
        'state': zipcode['State Abbreviation'],
        'state_full': zipcode['State'],
        'county': zipcode['County'],
        'latitude-zip': zipcode['Latitude'],
        'longitude-zip': zipcode['Longitude'],
        'nearest-fishspot': p['Waterbody Name'],
        'latitude-fish': p['Latitude'],
        'longitude-fish': p['Longitude'],
        'distance': distance(zipcode['Latitude'],zipcode['Longitude'],p['Latitude'],p['Longitude'])
        }
        dl.append(ap)
    dl_sorted = sorted(dl, key=lambda k: k['distance'])
    
    # Only return the waterbody that DEC released the stocking trout in
    for i in range(0,len(dl_sorted)):
        if dl_sorted[i]['nearest-fishspot'] in df_group_fishstock['Waterbody'].values:
            dl_sorted[i].setdefault('trout_stocked', df_group_fishstock['Number'].loc[df_group_fishstock['Waterbody']
            == dl_sorted[i]['nearest-fishspot']])
            break

    return dl_sorted[i]

# ----------------------------------------------------
# ---------------- Inputs: FILES  --------------------
# ----------------------------------------------------

FILE_FISHING_SPOTS  = "Recommended_Fishing_Rivers_And_Streams_API.csv"
FILE_FISH_STOCK = "Fish_Stocking_Lists__Actual___Beginning_2011.csv"
FILE_ZIPCODES  = "us_postal_codes.csv"

# -------------------------------------------------------
# ---------------- Inputs: Dataframes -------------------
# -------------------------------------------------------

df_fishing_spots = pd.read_csv(FILE_FISHING_SPOTS,encoding = "ISO-8859-1")
columns_to_drop = ['Special Regulations on Waterbody', 'Waterbody Information', 'Location']
df_fishing_spots.drop(columns_to_drop, axis=1, inplace=True)

df_fishstock = pd.read_csv(FILE_FISH_STOCK,encoding = "ISO-8859-1")
# filter only trout
df_fishstock = df_fishstock[df_fishstock['Species'].str.contains('Trout', na=False)]

# calculate the total number of trout stocked in each waterbody since 2011
df_group_fishstock = df_fishstock.groupby(['Waterbody'])['Number'].sum().reset_index()

df_zipcodes = pd.read_csv(FILE_ZIPCODES,encoding = "ISO-8859-1")
# filter only NY
df_zipcodes = df_zipcodes[df_zipcodes['State Abbreviation']=='NY']

print('**********************************************************')
print('*               Trout fishing navigator                  *')
print('**********************************************************')

zc = ''
data_exist = False

while not zc.isdigit() or not data_exist:
    print('Input zipcode where you are plan to go: \n')
    zc = input()

    if zc.isdigit():
        if (df_zipcodes['Zip Code'] == int(zc)).any():
            data_exist = True
        else:
            print('%s is invalid zipcode!' % zc)
    
record = getRecord(zc)

fishingSpot = closest(getFishingSpots('Trout'), record)
print('Waterbody Name: ' + fishingSpot['nearest-fishspot'])
print('Trout stocked: %8d' % int(fishingSpot['trout_stocked']))
print('Location: %2.9f %2.9f' % (fishingSpot['latitude-fish'], fishingSpot['longitude-fish'])) 
print('Distance: %8.2f miles' % (fishingSpot['distance']*0.621371)) # converted from km to mile
