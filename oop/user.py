import typing
import asyncio
import argparse


def _args():
    """ Аргументы командной строки """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--apply',
        type=bool,
        required=False,
        default=False,
        # action='store_true',
        help='Подтвердить удаление',
    )

    return parser.parse_args()


class Base:
    id=0
    name=None

    # def __new__(cls, *args, **kwargs):
    #     # print(args, kwargs)
    #     self = super().__new__(cls)
    #     # self._rehashed = set()
    #     return self

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        # print(args, kwargs)
        # super().__init__(**kwargs)

    # @property
    # @abstractmethod
    # def database(self) -> str:
    #     pass

    @classmethod
    async def get(
        cls,
        ids: typing.Union[typing.List, int] = None,
        *,
        fields: typing.Optional[typing.List] = None,
        count: typing.Optional[int] = None,
        offset: typing.Optional[int] = 0,
        **kw,
    ) -> typing.Optional[list]:
        users = [] # Cursor(cls.database)
        return users

    async def save(
        self,
        **kw,
    ): # async
        print("SAVE")
        # return await super().save(**kw)
        # async with db() as conn:
        #     for name, value in row.items():
        #         setattr(self, name, value)

        #     return self

        return self.id

    async def delete(
        self,
        **kw,
    ):
        print("DELETE")
        # return await super().delete(**kw)

class User(Base):
    pass


async def main(args: argparse.Namespace):
    # apply = args.apply
    print()

    # Empty
    user = User()

    print(
        "",
        "------------------ Empty ------------------",
        user,
        user.id,
        sep="\n"
    )

    # Create
    user = User(**{
        'id': 1,
    })
    # user = User({
    #     'id': 1,
    # })
    # user = User(
    #     id=1,
    # )

    print(
        "",
        "------------------ Create ------------------",
        user,
        user.id,
        sep="\n"
    )

    # Add
    res = await user.save()

    print(
        "",
        "------------------ Add ------------------",
        res,
        sep="\n"
    )

    # Edit
    user.name = 'Test'
    res = await user.save()

    print(
        "",
        "------------------ Edit ------------------",
        res,
        user.name,
        sep="\n"
    )

    # Get
    users = await User.get()

    print(
        "",
        "------------------ Get ------------------",
        users,
        sep="\n"
    )

    # Delete
    res = await users[0].delete()

    print(
        "",
        "------------------ Delete ------------------",
        res,
        sep="\n"
    )

    print("\n")


if __name__ == '__main__':
    try:
        asyncio.run(main(_args()))
    except KeyboardInterrupt:
        print('--- Остановлено пользователем ---')