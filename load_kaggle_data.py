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


storage_account_name = "storagerenero"
storage_account_key = "kbgke+J0a3F0suRS/57crAYIAhNU22Ro9hjGcf56K/1e5DTI7j+gkBCNgC3T3cN9Vs2s05RxjQVC+AStie1ZWg=="

spark.conf.set("fs.azure.account.key.{0}.blob.core.windows.net".format(storage_account_name),storage_account_key)

df = spark.read.format("csv")\
    .option("header","true")\
    .load("wasbs://{0}@{1}.blob.core.windows.net/{2}".format(container_name,storage_account_name,file_load_blob))

from pyspark.sql.functions import *
from delta.tables import *
# Remove invalid characters from column names
new_col_names = [col_name.replace(',', '_').replace(';', '_').replace('{', '_').replace('}', '_').replace('(', '_').replace(')', '_').replace('\n', '_').replace('\t', '_').replace('=', '_').replace(' ','') for col_name in df.columns]

df1 = df.toDF(*new_col_names)
#display(df1)
df2 = df1.withColumn("date_process",to_date(df1.PickUpDatetime))

#Validate if exist data in delta table
try:
    df_delta = spark.read.format("delta").load("dbfs:/user/hive/warehouse/ubertrips")
    joined_df = df_delta.join(df2,df_delta.TripID == df2.TripID,"left_anti")
    joined_df.write.format("delta").mode("append").saveAsTable("ubertrips")
except :
    df2.write.format("delta").mode("overwrite").saveAsTable("ubertrips")

#############
storage_account_name = "storagerenero"
storage_account_key = "kbgke+J0a3F0suRS/57crAYIAhNU22Ro9hjGcf56K/1e5DTI7j+gkBCNgC3T3cN9Vs2s05RxjQVC+AStie1ZWg=="
container_name = "deltatables"
dbfs_mount_point = "/mnt/delta"

dbutils.fs.mount(
    source=f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net",
    mount_point = dbfs_mount_point,
    extra_configs={
        f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net":storage_account_key
    }
)

df2.write.format("delta").mode("overwrite").option("path","dbfs:/mnt/delta/ubertrips").saveAsTable("ubertrips")