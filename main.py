"""
Main script to initialize logger and server
"""
import minio
from fastapi import Query
import os
from minio import Minio
import uvicorn


from fastapi import FastAPI, status, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse
from influxdb_client import InfluxDBClient
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.helpers.config_helper import props
from app.routers.user import router as user_router

from getminio import read_minio_object

__author__ = "Dinesh Sinnarasse"
__copyright__ = "Copyright 2023, Enterprise Minds"
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Enterprise Minds"
__status__ = "Development"


def get_application() -> FastAPI:
    """
    Initialize the application server with logger
    :return: fastApi app
    """
    application = FastAPI(title="Anomaly-detection", debug=True)
    return application


app = get_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


def init_database_connection():
    """
    Mehtod to initiate DBConnection
    :return: database_object
    """
    try:
        connection_url = props.get_properties("database", "connection_url")
        db_name = props.get_properties("database", "db_name")
        client = InfluxDBClient(
            connection_url, token="sIokMknLOBmfxMMrtkrMQTqImwd_wGnMH1-b6Hz_WDvuWp4-ysJ0Cl7UHpaRw-0SovIfMPXwcwmN8bd_HERnGA==", org="eminds")
    except Exception:
        raise Exception("Database connection error")
    return client


@app.get('/healthcheck', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'healthcheck': 'Everything OK!'}


@app.get("/download/{bucket_name}/{object_name}")
async def download_bucket_object(bucket_name: str, object_name: str):
    #local_file_path = f"D:\\Anomaly\\Anomaly-detection\\{object_name}"
    try:
        influx_client = init_database_connection()

        read_minio_object(bucket_name, object_name,
                          influx_client=influx_client)
        # Call perform_insertdata with the file path
        # perform_insertdata(file_path=local_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Read server connection details
    host = props.get_properties("connection", "host")
    port = props.get_properties("connection", "port")

    uvicorn.run(app, host=host, port=int(port))
