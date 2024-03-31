from sgp4.api import Satrec
from sys import stdout
from sgp4.conveniences import dump_satrec
from astropy.time import Time
from sgp4.api import SGP4_ERRORS
from astropy.coordinates import TEME, ITRS, CartesianDifferential, CartesianRepresentation
from astropy import units as u
import requests
import pandas as pd
import configparser
from astropy.coordinates import EarthLocation, AltAz
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime
from datetime import datetime as dt
import plotly.express as px

def get_latest_tle():
    uriBase = 'https://www.space-track.org'
    requestLogin = '/ajaxauth/login'

    requestCmdAction = "/basicspacedata/query" 
    requestFindStarlinks = "/class/tle_latest/NORAD_CAT_ID/>40000/ORDINAL/1/OBJECT_NAME/STARLINK~~/format/json/orderby/NORAD_CAT_ID%20asc"

    # Select the number of object to download
    # To download all the objects, set to -1
    nb_objects = -1

    # Build the request part of the URL
    if nb_objects == -1:
        requestAll = '/class/gp/orderby/OBJECT_ID%20asc/emptyresult/show'
    else:
        requestAll = f"/class/gp/orderby/OBJECT_ID%20asc/limit/{nb_objects}/emptyresult/show"

    print(requestAll)

    # Use configparser package to pull in the ini file (pip install configparser)
    config = configparser.ConfigParser()
    config.read("./SLTrack.ini")
    configUsr = config.get("configuration","username")
    configPwd = config.get("configuration","password")
    siteCred = {'identity': configUsr, 'password': configPwd}

    with requests.Session() as session:
        # Send login request
        resp = session.post(uriBase + requestLogin, data = siteCred)
        print(resp)

        resp = session.get(uriBase + requestCmdAction + requestAll)
        print(resp)

        session.close()

    response_json = resp.json()

    meta_columns =  ['CCSDS_OMM_VERS', 'COMMENT', 'FILE', 'GP_ID']
    no_info_columns = ['TIME_SYSTEM', 'ELEMENT_SET_NO', 'REF_FRAME', 'CENTER_NAME', 'ORIGINATOR', 'MEAN_ELEMENT_THEORY', 'CLASSIFICATION_TYPE']
    tle_columns = ['TLE_LINE0', 'TLE_LINE1', 'TLE_LINE2']

    drop_cols = meta_columns + no_info_columns + tle_columns

    # Save all objects in a DataFrame + reorder columns
    objects_df = pd.DataFrame(response_json).drop(columns=drop_cols)[['NORAD_CAT_ID', 'OBJECT_ID', 'OBJECT_NAME', 'OBJECT_TYPE', 'EPOCH', 'MEAN_MOTION',
        'ECCENTRICITY', 'INCLINATION', 'RA_OF_ASC_NODE', 'ARG_OF_PERICENTER',
        'MEAN_ANOMALY', 'EPHEMERIS_TYPE',
        'REV_AT_EPOCH', 'BSTAR', 'MEAN_MOTION_DOT', 'MEAN_MOTION_DDOT',
        'SEMIMAJOR_AXIS', 'PERIOD', 'APOAPSIS', 'PERIAPSIS',
        'RCS_SIZE', 'COUNTRY_CODE', 'LAUNCH_DATE', 'SITE', 'DECAY_DATE', 'CREATION_DATE']]

    # Keep original TLE in a different DataFrame
    tle_df = pd.DataFrame(response_json)[['OBJECT_ID', 'OBJECT_NAME'] + tle_columns]

    return objects_df, tle_df