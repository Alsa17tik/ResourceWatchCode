import boto3
import io
import pandas as pd
import numpy as np

from dateutil import parser
import pytz
import datetime


### Functions for reading and uploading data to/from S3

s3_bucket = "wri-public-data"
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def read_from_S3(bucket, key, index_col=0):
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()), index_col=[index_col], encoding="utf8")
    return(df)

def write_to_S3(df, key, bucket=s3_bucket):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    s3_resource.Object(bucket, key).put(Body=csv_buffer.getvalue())

    
    
    
### Standardizing ISO3 codes

CONVERSIONS = "resourcewatch/blog_data/GHG-GDP_Divergence_D3/Conversions/"
wb_name_to_iso3_conversion = read_from_S3(s3_bucket, CONVERSIONS+"World Bank to ISO3 name conversion.csv")
def add_iso(name):
    try:
        return(wb_name_to_iso3_conversion.loc[name,"ISO"])
    except:
        return(np.nan)


    
### Standardizing datetimes
    
def structure_dttm_from_parts(row, dttm_elems, dttm_pattern):
    dt = datetime.datetime(year=int(row[dttm_elems["year_col"]]), 
                           month=int(row[dttm_elems["month_col"]]),
                           day=int(row[dttm_elems["day_col"]]))
    if "hour_col" in dttm_elems:
        dt = dt.replace(hour=int(row[dttm_elems["hour_col"]]))
    if "min_col" in dttm_elems:
        dt = dt.replace(minute=int(row[dttm_elems["min_col"]]))
    if "sec_col" in dttm_elems:
        dt = dt.replace(second=int(row[dttm_elems["sec_col"]]))
    if "milli_col" in dttm_elems:
        dt = dt.replace(milliseconds=int(row[dttm_elems["milli_col"]]))
    if "micro_col" in dttm_elems:
        dt = dt.replace(microseconds=int(row[dttm_elems["micro_col"]]))
    if "tzinfo_col" in dttm_elems:
        timezone = pytz.timezone(row[dttm_elems["tzinfo_col"]])
        dt = timezone.localize(dt)
    
    dttm_str = dt.strftime(dttm_pattern)
    return(dttm_str)

def fix_datetime_UTC(data_df, dttm_elems_in_sep_columns=True, 
                     dttm_elems={},
                     dttm_col=None, 
                     dttm_pattern="%Y-%m-%dT%H:%M:%SZ"):
    """
    Desired datetime format: 2017-12-08T15:16:03Z
    Corresponding date_pattern for strftime: %Y-%m-%dT%H:%M:%SZ
    
    If date_elems_in_sep_columns=True, then there will be a dictionary date_elems
    That at least contains the following elements:
    date_elems = {"year_col":`int or string`,"month_col":`int or string`,"day_col":`int or string`}
    OPTIONAL KEYS IN date_elems:
    * hour_col
    * min_col
    * sec_col
    * milli_col
    * micro_col
    * tz_col
    
    Depends on:
    from dateutil import parser
    """
    default_date = parser.parse("January 1 1900 00:00:00")
        
    # Mutually exclusive to provide broken down datetime factors, 
    # and either a date, time, or datetime object
    if dttm_elems_in_sep_columns:
        assert(type(dttm_elems)==dict)
        assert(dttm_col==None)
        
        tmp = data_df.copy()
        if "year_col" not in dttm_elems:
            dttm_elems["year_col"] = "year_tmp"
        if dttm_elems["year_col"] not in tmp.columns:
            tmp[dttm_elems["year_col"]] = 1990
            
        if "month_col" not in dttm_elems:
            dttm_elems["month_col"] = "month_tmp"
        if dttm_elems["month_col"] not in tmp.columns:
            tmp[dttm_elems["month_col"]] = 1
            
        if "day_col" not in dttm_elems:
            dttm_elems["day_col"] = "day_tmp"
        if dttm_elems["day_col"] not in tmp.columns:
            tmp[dttm_elems["day_col"]] = 1
        
        dttm_col = tmp.apply(lambda row: structure_dttm_from_parts(row, dttm_elems, dttm_pattern), axis=1)
        
    else:
        # Need to provide the default parameter to parser.parse so that missing entries don't default to current date
        dttm_col = data_df.apply(lambda row: parser.parse(row[dttm_col], default=default_date).strftime(dttm_pattern), axis=1)
    
    return(dttm_col)


