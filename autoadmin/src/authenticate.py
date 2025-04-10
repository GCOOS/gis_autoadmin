from arcgis.gis import GIS
from getpass import getpass
import os, sys 

class auth:
    def __init__(self):
        platform: str = None

    def selfAuth(self, verbose=True) -> GIS:
        """For authenticating the user in the hosted notebook environment"""
        try:
            agol_gis = GIS("home")
            if verbose:
                print(f"\n Succesfully Authenticated In the ArcGIS Online Environment")
                print(f"Portal Name: {agol_gis.properties.portalName}")
                return agol_gis
            
        except Exception as e:
            print("An error occured during the environment-based authentication ArcGIS ")

    def getAuthFromVenv(Self) -> tuple:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        venv_path = r"/venv/"
        auth_file = os.path.join(venv_path, 'auth.txt')
    
        try:
            with open(auth_file, 'r') as file:
                lines = file.read().splitlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"auth.txt not found in the specified venv directory: {venv_path}")
        
        username = None
        password = None

        for line in lines:
            if line.startswith("username:"):
                username = line.split(":", 1)[1].strip()
            elif line.startswith("password:"):
                password = line.split(":", 1)[1].strip()

        if not username or not password:
            raise ValueError("The auth.txt file must contain both a username and a password in the correct format.")
        
        return username, password


    def portalAuth(self, portal_url: str, anon = False, venv_creds= False) -> GIS:
        if venv_creds:
            username, password = self.getAuthFromVenv()
        else:
            input("Input your Portal Username")
            password = getpass()
        if not anon:
            try:
                gis = GIS(
                    url= portal_url,
                    username= username,
                    password=password,
                    verify_cert= False
                )
                return gis
            except Exception as e:
                print(f"\nAn Exception occured while authenticating with your portal: {e}")
                return None
        else:
            try:
                gis = GIS(
                    url=portal_url
                )
                return gis
            except Exception as e:
                print(f"An error occured when anonymously connecting to {portal_url}")
                return None




        