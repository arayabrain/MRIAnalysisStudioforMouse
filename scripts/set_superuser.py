import sys
import os
import argparse
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from backend.models.user import UserUpdate
from backend.service.firebase.crud_user import update_user, read_user


async def set_superuser(user_id: str, lab: str, name: str):
    user = await read_user(user_id)
    print(user)
    updated_user = await update_user(
        user_id,
        UserUpdate(display_name=name, lab=lab, role=1),
    )
    print(updated_user)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uid", help="ID of the firebase user to be set as the admin")
    parser.add_argument("--lab", help="Lab name")
    parser.add_argument("--name", help="Display name")

    args = parser.parse_args()

    asyncio.run(set_superuser(args.uid, args.lab, args.name))
