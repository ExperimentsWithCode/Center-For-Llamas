from app import MODELS_FOLDER_PATH, RAW_FOLDER_PATH
from app.data.reference import models_split_into_folders

import csv
import os
import json
import traceback
import pandas as pd
import glob 
import numpy as np
from pathlib import Path

def get_cwd():
    cwd_temp = os.getcwd()
    temp_split = cwd_temp.split('/')
    cwd = ""
    for x in temp_split:
        if x == 'experiments':
            break
        elif x == '':
            pass
        else:
            cwd += "/"+x    
    if temp_split[-1] == 'Musings':
        cwd += '/center-for-llamas'   
    if temp_split[-1] == 'analysis':
        cwd = cwd[: - len('/analysis')]   
    if temp_split[-1] == 'opperations':
        cwd = cwd[: - len('/opperations')]   
    if temp_split[-1] == 'ze_old_stuff':
        cwd = cwd[: - len('/ze_old_stuff')]   
    return cwd


cwd = get_cwd()

def read_csv(filename, path='source'):
    # print(cwd)
    try:
        data = []
        with open(cwd+"/app/data/"+ path+ "/"+ filename+".csv", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
            # for row in transactions:
        return data
    except Exception as e:
        print(e)
        # print(traceback.format_exc())
        return False

def write_csv(filename, data, path='output'):
    try:
        Path(f"{cwd}/app/data/{path}").mkdir(parents=False, exist_ok=True)
        with open(f"{cwd}/app/data/{path}/{filename}.csv", 'w') as f:
            w = csv.DictWriter(f, data[0].keys())
            w.writeheader()
            for t in data:
                w.writerow(t)
        return True
    except:
        return False

def read_json(filename, path='storage'):
    # print(cwd+"/app/data/storage/"+ filename+'.json')
    try:
        with open(f"{cwd}/app/data/{path}/{filename}.json") as f:
           data = json.load(f)
        return data
    except Exception as e:
        # print (filename)
        # print(cwd)
        print (e)
        return False

def write_json(filename, data, path='output'):
    # print(cwd+"/app/data/source/"+ filename+'.json')
    try:
        with open(f"{cwd}/app/data/{path}/{filename}.json", "w") as f:
            json.dump(data, f)
        return True
    except:
        return False


def write_dataframe_csv(filename, df, source='output'):
    # print(f"{cwd}/app/data/{source}/{filename}.csv")
    try:
        full_filename = f"{cwd}/app/data/{source}/{filename}.csv"
        df.to_csv(full_filename,  index=False)
        return True
    except Exception as e:
        print(e)
        # traceback.format_exc()
        return False


def write_dfs_to_xlsx(filename, dfs, titles=None):
    with pd.ExcelWriter(cwd+"/app/data/output/"+ filename+'.xlsx') as writer:
        i= 1
        # print(titles)
        for df in dfs:
            title = None
            if titles:
                if len(titles) > i:
                    title = titles[i-1]
            if not title:
                title = f"Sheet {i}"
            # print(title)
            df.to_excel(writer, sheet_name = title)
            i+= 1


def csv_to_df(filename, path='source'): 
    if use_folders_instead(filename, path):
        return csv_folder_to_df(filename, path)     
    resp_dict = read_csv(filename, path)
    df = pd.json_normalize(resp_dict)
    return df

def df_to_csv(df, filename, path='output'):
    if use_folders_instead(filename, path):
        return df_to_csv_folder(df, filename, path)
    cwd = get_cwd()
    Path(f"{cwd}/app/data/{path}").mkdir(parents=False, exist_ok=True)
    full_filename = f"{cwd}/app/data/{path}/{filename}.csv"
    df.to_csv(full_filename) 

def save_file(file, filename, path='imported_processed'):
    Path(f"{cwd}/app/data/{path}").mkdir(parents=False, exist_ok=True)
    full_filename = f"{cwd}/app/data/{path}/{filename}"
    file.save(full_filename)

def csv_folder_to_df(folder_name, path='source'):
    cwd = get_cwd()
    Path(f"{cwd}/app/data/{path}/{folder_name}").mkdir(parents=False, exist_ok=True)
    path = f"{cwd}/app/data/{path}/{folder_name}/"
    csv_files = glob.glob(os.path.join(path, "*.csv")) 
    # loop over the list of csv files 
    df_concat = []
    for f in csv_files: 
        # read the csv file 
        df = pd.read_csv(f) 
        # # print the location and filename 
        # print('Location:', f) 
        # print('File Name:', f.split("\\")[-1]) 
        # # print the content 
        # print('Content:') 
        # display(df) 
        # print() 
        if len(df_concat) == 0:
            df_concat = df
        else:
            df_concat = pd.concat([df_concat, df])
    return df_concat

def df_to_csv_folder(df, folder_name, path=MODELS_FOLDER_PATH):
    new_path = f"{path}/{folder_name}"
    df_split = np.array_split(df, 5)
    i = 0
    for df in df_split: 
        i += 1
        filename = f"{folder_name}_{i}"
        df_to_csv(df, filename, new_path)
    return True

def use_folders_instead(filename, path):
    if path == MODELS_FOLDER_PATH:
        if filename in models_split_into_folders:
            return True
    return False
#creating a new directory called pythondirectory

def get_csv_filenames_in_folder(path):
    path = f"{cwd}/app/data/{path}/"
    return glob.glob(os.path.join(path, "*.csv")) 
