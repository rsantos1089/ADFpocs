import json

dictionary = {"username":"renero","key":"0a4079a3c55f212224b7fe0426a66d37"}
json_object = json.dumps(dictionary, indent=4)
with open("/root/.kaggle/kaggle.json", "w") as outfile:
    outfile.write(json_object)
	
from azure.storage.blob import BlobClient
import kaggle
import zipfile

dataset_name = 'eugenekoutiloff/synthetic-dataset-of-uber-trips-in-sydney-nsw'
zip_file_path = f'./synthetic-dataset-of-uber-trips-in-sydney-nsw.zip'
kaggle.api.dataset_download_files(dataset_name,path='.')

with zipfile.ZipFile(zip_file_path,'r') as zip_ref:
    zip_ref.extractall('./')
	
conn_azure_blob = "DefaultEndpointsProtocol=https;AccountName=storagerenero;AccountKey=kbgke+J0a3F0suRS/57crAYIAhNU22Ro9hjGcf56K/1e5DTI7j+gkBCNgC3T3cN9Vs2s05RxjQVC+AStie1ZWg==;EndpointSuffix=core.windows.net"
container_name = "artifacts"
file_load_blob = "final_dataset.csv"

blob = BlobClient.from_connection_string(conn_str=conn_azure_blob,container_name=container_name,blob_name=file_load_blob)
with open(file_load_blob,'rb') as data:
    blob.upload_blob(data, overwrite=True)
