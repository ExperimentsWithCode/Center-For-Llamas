import csv
import os
import json
import traceback
import pandas as pd

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

def read_csv(filename, path='source'):
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
        traceback.format_exc() 
        return False

def write_csv(filename, data, path='output'):
    try:
        with open(cwd+"/app/data/"+ path +"/"+ filename+".csv", 'w') as f:
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
        with open(cwd+"/app/data/"+path+'/'+ filename+'.json') as f:
           data = json.load(f)
        return data
    except Exception as e:
        print (filename)
        print(cwd)
        print (e)
        return False

def write_json(filename, data):
    print(cwd+"/app/data/source/"+ filename+'.json')
    try:
        with open(cwd+"/app/data/output/"+ filename+'.json', "w") as f:
            json.dump(data, f)
        return True
    except:
        return False


def write_dataframe_csv(filename, df):
    print(cwd+"/app/data/output/"+ filename+'.csv')
    try:
        full_filename = cwd+"/app/data/output/"+ filename+'.csv'
        df.to_csv(full_filename) 
        return True
    except Exception as e:
        print(e)
        traceback.format_exc() 
        return False
    

def write_dfs_to_xlsx(filename, dfs, titles=None):
    with pd.ExcelWriter(cwd+"/app/data/output/"+ filename+'.xlsx') as writer:
        i= 1
        print(titles)
        for df in dfs:
            title = None
            if titles:
                if len(titles) > i:
                    title = titles[i-1]
            if not title:
                title = f"Sheet {i}"
            print(title)
            df.to_excel(writer, sheet_name = title)
            i+= 1