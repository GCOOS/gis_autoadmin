import os
import sys

os.environ['AGOL_HOME'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from autoadmin.autoadmin import autoadmin
from autoadmin.src.admin import adminTasks 
from autoadmin.src.authenticate import auth
from autoadmin.src.content import contentGroups
from autoadmin.src.tags import tagCommands

def main():

    publishing_user = "GCOOS_Admin"
    admin = autoadmin(publishing_user=publishing_user)
    # groups = admin.getThematicGroups(as_object=True)
    # print(groups[2].title)
    admin.enforceThematicContentOwner("54a8889f2d0841c3a31cb4fa120cf0ff", transfer_owner=True, remove_content=False)
    # admin.executeAllTagCommands()


if __name__ == "__main__":
    main()