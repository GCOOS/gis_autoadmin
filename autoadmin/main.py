import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from autoadmin import autoadmin
from src.content import contentSearch


def main():
    content = contentSearch()

    print(content.functional_groups)
    print(content.thematic_groups)
    # publishing_user = "GCOOS_Admin"
    # admin = autoadmin(publishing_user=publishing_user)
    # admin.executeAllTagCommands()


if __name__ == "__main__":
    main()