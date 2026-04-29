import pandas as pd
import requests
import io

class CERNClient:
    @staticmethod
    def get_data(url: str = "https://opendata.cern.ch/record/700/files/MuRun2010B_0.csv"):
        filename = url.split("/")[-1]
        try:
            print(f"Downloading CERN Data: {url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))
            print(f"Data loaded into memory.")
            return df
        except Exception as e:
            print(f"Error downloading data: {e}")
            return None