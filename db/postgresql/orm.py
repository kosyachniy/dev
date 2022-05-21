import asyncio
import datetime

from libdev.codes import USER_STATUSES, LOCALES
from consql import make_base, Attribute, Table, coerces


Base = make_base('localhost:5432', 'main', 'postgres', 'password')


class User(Base, table=Table('users')):
    id = Attribute(types=int, required=False)
    status = Attribute(
        types=str,
        required=True,
        default='authorized',
        enum=USER_STATUSES,
    )
    image = Attribute(types=str, required=False)
    login = Attribute(types=str, required=False)
    name = Attribute(types=str, required=False)
    surname = Attribute(types=str, required=False)
    mail = Attribute(types=str, required=False)
    password = Attribute(types=str, required=False)
    phone = Attribute(types=int, required=False)
    lang = Attribute(
        types=str,
        required=False,
        enum=LOCALES,
    )
    birthday = Attribute(
        types=datetime.date,
        required=False,
        coerce=coerces.date,
    )
    tags=Attribute(
        types=list,
        required=True,
        default=lambda: [],
        tags='db_default',
    )
    created=Attribute(
        types=datetime.datetime,
        required=False,
        default=coerces.now,
        coerce=coerces.date_time,
    )
    updated=Attribute(
        types=datetime.datetime,
        required=False,
        default=coerces.now,
        coerce=coerces.date_time,
    )


async def main():
    user = User(
        login='kosyachniy',
        name='Alexey',
        surname='Poloz',
    )
    await user.save()

    print(await User.get(offset=0))

    await user.rm()


asyncio.run(main())
