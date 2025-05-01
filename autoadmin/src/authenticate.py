# auth.py

from arcgis.gis import GIS
from getpass import getpass
import os
import sys

# module-level global
gis: GIS = None


class auth:
    def __init__(self, platform: str = None):
        # store GIS on the instance too
        self.gis: GIS = None
        self.platform = platform

    def selfAuth(self, verbose: bool = True) -> GIS:
        """Authenticate via the notebook’s ‘home’ profile and set global gis."""
        global gis
        try:
            self.gis = GIS("home")
            
            if verbose:
                print("Successfully authenticated in ArcGIS Online.")
                print("Portal Name:", self.gis.properties.portalName)
            return None

        except Exception as e:
            print("Error during environment-based authentication:", e)
            return None

    def getAuthFromVenv(self) -> tuple:
        """Read username/password from auth.txt in the virtual environment."""
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        venv_path = r"/venv/"
        auth_file = os.path.join(venv_path, "auth.txt")

        try:
            with open(auth_file, "r") as file:
                lines = file.read().splitlines()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"auth.txt not found in the specified venv directory: {venv_path}"
            )

        username = password = None
        for line in lines:
            if line.startswith("username:"):
                username = line.split(":", 1)[1].strip()
            elif line.startswith("password:"):
                password = line.split(":", 1)[1].strip()

        if not username or not password:
            raise ValueError(
                "The auth.txt file must contain both a username and a password."
            )
        return username, password

    def portalAuth(self, portal_url: str, anon: bool = False, venv_creds: bool = False) -> GIS:
        """
        Authenticate against a Portal or anonymously, set global gis,
        and return the GIS object (or None on failure).
        """
        global gis

        if not anon:
            if venv_creds:
                username, password = self.getAuthFromVenv()
            else:
                username = input("Portal username: ")
                password = getpass()

            try:
                portal_gis = GIS(
                    url=portal_url,
                    username=username,
                    password=password,
                    verify_cert=False,
                )
                gis = portal_gis
                self.gis = portal_gis
                print("Successfully authenticated with portal.")
                return portal_gis

            except Exception as e:
                print("Error authenticating with portal:", e)
                return None

        else:
            try:
                anon_gis = GIS(url=portal_url)
                gis = anon_gis
                self.gis = anon_gis
                print("Successfully connected anonymously to portal.")
                return anon_gis

            except Exception as e:
                print("Anonymous connection failed:", e)
                return None
        