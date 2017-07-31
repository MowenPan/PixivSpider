import os
import sys
import json
import msvcrt
import requests
from pixivpy3 import AppPixivAPI, PixivError


_REQUESTS_KWARGS = {
  # 'proxies': {
  #   'https': 'http://127.0.0.1:8888',
  # },
  # 'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}

aapi = AppPixivAPI(**_REQUESTS_KWARGS)


def mkdir(path):
    """
        判断路径是否存在
        1) 如果不存在就新建文件夹
        2) 如果存在就打印相关信息
    """
    is_exixts = os.path.exists(path)
    # 如果不存在就新建文件夹
    if not is_exixts:
        print("    [*]新建了一个文件夹 ", path)
        os.makedirs(path)
    else:
        print("    [+]文件夹 " + path + " 已创建")


def get_artist_url(artist_id):
    """获取画师主页url"""
    url = "https://www.pixiv.net/member_illust.php?id=" + artist_id
    return url


def pwd_input():
    chars = []
    while True:
        try:
            newChar = msvcrt.getch().decode(encoding="utf-8")
        except:
            return input("你很可能不是在cmd命令行下运行，密码输入将不能隐藏:")
        if newChar in '\r\n':  # 如果是换行，则输入结束
             break
        elif newChar == '\b':  # 如果是退格，则删除密码末尾一位并且删除一个星号
             if chars:
                 del chars[-1]
                 msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格
                 msvcrt.putch( ' '.encode(encoding='utf-8'))  # 输出一个空格覆盖原来的星号
                 msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格准备接受新的输入
        else:
            chars.append(newChar)
            msvcrt.putch('*'.encode(encoding='utf-8')) # 显示为星号
    return ''.join(chars)


def check_login():
    username = input('请输入你的P站账户名或者邮箱：\n')
    print('请输入你的P站账户密码：')
    password = pwd_input()
    # password = input('请输入你的P站账户密码：\n')
    try:
        if aapi.login(username=username, password=password):
            print('\n    [*]登陆成功！！！')
    except PixivError:
        print('    [!]请检查账户名和密码！！！')
        check_login()


def check_url():
    check_login()
    while True:
        artist_id = input("请输入画师id(输入 q 结束程序): \n")
        if artist_id == 'q':
            sys.exit()
        else:
            url = get_artist_url(artist_id)
            req = requests.get(url)
            if not int(req.status_code) == 200:
                print("    [!]URL ERROR!!!")
                print("    [!]请检查画师id是否正确！！！")
                continue
            else:
                offset = 0
                get_illustration(artist_id, offset)
                while True:
                    offset += 30
                    # json_result = aapi.user_illusts(artist_id, type='illust', offset=offset, req_auth=True)
                    next_url = get_illustration(artist_id, offset)
                    if next_url == 'None':
                        break


def get_illustration(artist_id, offset=30):

    json_result = aapi.user_illusts(artist_id, type='illust', offset=offset, req_auth=True)
    # print(json_result)
    path = str(artist_id)
    mkdir(path)

    filename = str(artist_id) + '_illustrations_info.json'
    if os.path.isfile(path + '/' + filename):
        print('    [!]File has already Exisits,the content will append to the file!!!')
        with open(path + '/' + filename, 'a', encoding='utf-8') as f:
            f.write(',' + json.dumps(json_result, ensure_ascii=False))
    else:
        print("    [!]File don't Exisits,program will create the file!!!")
        with open(path + '/' + filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_result, ensure_ascii=False))

    illust_dict = json.loads(json.dumps(json_result))
    # print(illust_dict)
    illusts = illust_dict['illusts']
    next_url = json_result['next_url']

    for illust in illusts:
        page_count = int(illust['page_count'])
        print(page_count)
        if page_count == 1:
            image_url = illust['meta_single_page']['original_image_url']
            print('    [*]Downloading.......')
            print("%s: %s" % (illust['id'], image_url))
            name = image_url.split('/')[-1]
            print("    [*]Downloading illustration" + "————" + name)
            aapi.download(image_url, path=path, name=name)
            print("    [*]Downloaded illustration" + "————" + name)
        else:
            for page in illust['meta_pages']:
                image_url = page['image_urls']['original']
                print("%s: %s" % (illust['id'], image_url))
                name = image_url.split('/')[-1]
                print("    [*]Downloading illustration" + "————" + name)
                aapi.download(image_url, path=path, name=name)
                print("    [*]Downloaded illustration" + "————" + name)

    print('    [!]Downloading Complete.......')
    print('offset = ' + str(offset))
    print('next_url = ' + str(next_url) + '\n\n')
    return str(next_url)


def main():
    check_url()


if __name__ == '__main__':
    main()
