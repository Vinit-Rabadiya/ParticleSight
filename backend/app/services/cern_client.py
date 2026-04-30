import pandas as pd
import requests
import io
import os

class CERNClient:
    @staticmethod
    def get_data(url: str = "https://opendata.cern.ch/record/700/files/MuRun2010B_0.csv"):
        # Derive filename from the URL and save to backend/data/
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.normpath(os.path.join(base_dir, "..", "..", "data"))
        filename = os.path.join(data_dir, url.split("/")[-1])
        
        # 1. Always check if the file is already here first
        if os.path.exists(filename):
            print(f"Found {filename} locally. Skipping download.")
            return pd.read_csv(filename)
        
        # 2. If not local, try the CERN link with a 'Browser' identity
        try:
            print(f"Downloading from CERN: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            # Increased timeout to 30 seconds for CERN's slow response
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(filename, "w") as f:
                f.write(response.text)
                
            df = pd.read_csv(io.StringIO(response.text))
            print(f"Success! Data loaded and saved as {filename}")
            return df

        except Exception as e:
            print(f"CERN Server Error: {e}")
            print("\nTIP: If the download fails, open the link in your browser,")
            print(f"save the file as '{filename}' in D:\\cernsight\\backend\\")
            return None