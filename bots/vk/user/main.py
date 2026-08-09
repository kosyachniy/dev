from lib.vk import VkResponseError, get_stat


def main():
    try:
        print(get_stat(140420515))
    except VkResponseError as error:
        raise SystemExit(str(error))

    # for i in read():
    # 	print(i[0], i[1])

    # send(140420515, 'хоба работает', ['https://w-club.com.ua/images/Blog/gvata/Gvatemala_kurort_puerto_san_hose.jpg', 'photo-151412216_456239019'])

    # print(dial())

    # print(info(140420515))

    # print(stats())

    # print(wall(-23303030))

    # print(groups())

    # print(post(-200093870))


if __name__ == '__main__':
    main()
