# -*- coding: utf-8 -*-
"""

Original file is located at
    https://colab.research.google.com/drive/1VGPpzYlMPzeVjmuuIH2g7rIC90qMI7lq
"""

import pandas as pd
import json
import os
import numpy
import glob
from zipfile import ZipFile
from functools import partial
from multiprocessing import Pool

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

def get_cbg_field_descriptions(year=2019):

  auth.authenticate_user()  # Authenticate and create the PyDrive client. 
  gauth = GoogleAuth()
  gauth.credentials = GoogleCredentials.get_application_default()
  drive = GoogleDrive(gauth)

  def get_drive_id(filename): #function to pull input files from Google Drive
      drive_ids = {'2016' : '13dLXo67IZDh3OZl042GQYG16Qn_NB7sz',
                  '2017' : '1b2RVBDgzdrDJkL0OCYRMGBc5zbLhv5MB',
                  '2018' : '1r7z3efdS5viIRMsQzu9ExHoIL29QjaVi',
                  '2019' : '1fJsLm6voxWsTq5FQrUzO9PpBltQ8n_lJ'
                  }
      return(drive_ids[filename])

  def pd_read_csv_drive(id, drive, dtype=None): #function to pull input files from Google Drive into pandas dataframes
    downloaded = drive.CreateFile({'id':id})
    downloaded.GetContentFile('Filename.csv')  
    return(pd.read_csv('Filename.csv',dtype=dtype))

  final_table = pd_read_csv_drive(get_drive_id(str(year)), drive)
  return(final_table.dropna(axis=1, how='all'))

def get_census_columns(columns, year):
    auth.authenticate_user()  # Authenticate and create the PyDrive client. 
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    file_list_2016 = dict([(i['title'], i['id']) for i in drive.ListFile({'q': "'17TexQTOM0RmpbekqNBvsiKs_jPH8ynQR' in parents"}).GetList() if i['title'].startswith('cbg')])
    if 'cbg_patterns.csv' in file_list_2016:
      del file_list_2016['cbg_patterns.csv']
    file_list_2017 = dict([(i['title'], i['id']) for i in drive.ListFile({'q': "'1jVF5Z5gf84AL09pGq_4nKAsfIM-lVrqi' in parents"}).GetList()])
    file_list_2018 = dict([(i['title'], i['id']) for i in drive.ListFile({'q': "'1g5uFI6ZfV2lPieZF63b4VYhqNiwe7dLC' in parents"}).GetList()])
    file_list_2019 = dict([(i['title'], i['id']) for i in drive.ListFile({'q': "'1LJFuG74zoy1FpMg3tcJ_UBCCA4OwGcpU' in parents"}).GetList()])
  
    def get_drive_id(year): #function to pull input files from Google Drive
      drive_ids_1 = {
      '2016': file_list_2016,
      '2017': file_list_2017,
      '2018': file_list_2018,
      '2019': file_list_2019} 
      return(drive_ids_1[year])

    def pd_read_csv_drive(id, drive, dtype=None): #function to pull input files from Google Drive into pandas dataframes
        downloaded = drive.CreateFile({'id':id})
        downloaded.GetContentFile('Filename.csv')  
        return(pd.read_csv('Filename.csv',dtype=dtype))

    column_dict = {}
    columns_short = [str.lower(i[0:3]) for i in columns]
    for i in range(0, len(columns)):
      for j in list(get_drive_id(year).keys()):
        if columns_short[i] in j:
          if j not in column_dict:
            column_dict[j] = ['census_block_group']
          column_dict[j].append(columns[i])
    table_dict = dict([(i, pd_read_csv_drive(get_drive_id(year)[i], drive)[column_dict[i]]) for i in column_dict.keys()])
    dfs = table_dict.values()
    dfs = [x.set_index('census_block_group') for x in dfs]
    df = pd.concat(dfs, axis=1, keys=range(1, len(dfs) + 1))
    df.columns = df.columns.map('{0[1]}{0[0]}'.format)
    df.reset_index(inplace = True)
    return df

