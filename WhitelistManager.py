# -*- code by: utf-8 -*-
# original author: Sinbing.
# edited by: yokina
from urllib.request import urlopen
from mcdreforged.api.all import *
import hashlib
import shutil
import time
import json
import os
import re

DEBUG = False
# Set [Minecraft Server Dir Name] and [World Dir Name] if changed.
server_dirname = 'server'
world_dirname = 'world'

# 1: Caculate uuid from API  |  2: diff offline uuid from playerdata  |  3： local calculator by: 账号己注销  |
uuid_method = 3
bot_wait_time = 3


PLUGIN_METADATA = {
    'id': 'whitelist_manager',
    'version': '1.0.0',
    'name': 'Whitelist Manager',
    'description': 'Manager whitelist when server using MultiYggdrasil.',
    'author': 'yokina',
    'link': 'https://github.com/yokinanya',
    'dependencies': {
        'mcdreforged': '>=2.0.0'
    }
}


def server_cmd(info: Info, command: str):
    if DEBUG:
        print(f'CMD: {command}')
    else:
        info.get_server().execute(command)


def Dprint(info: Info, text: str):
    if DEBUG:
        print(text)
    else:
        info.get_server().reply(info, text)


def check_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def json_file_to_list(json_path: str) -> list:
    with open(json_path, 'r', encoding='UTF-8') as file:
        output_dict = json.load(file)
    return output_dict


def create_whitelist_file(json_list: list, workpath: str, type: str):
    format_time = time.strftime('%y-%m-%d_%H-%M-%S', time.localtime())
    # Backup old whitelist & create new whitelist.
    check_dir(os.path.join(workpath, 'whitelist_backup'))
    backup_whitelist_name = format_time + type + 'whitelist.json'
    shutil.move(os.path.join(workpath, 'whitelist.json'), os.path.join(workpath, 'whitelist_backup', backup_whitelist_name))

    # Create new whitelist.
    file_name: str = os.path.join(workpath, 'whitelist.json')
    with open(file_name, 'w', encoding='UTF-8') as file:
        file.write(json.dumps(json_list, indent=4, ensure_ascii=False))


def get_playerdata_filename_list():
    filename_all = os.listdir(os.path.join(server_dirname, world_dirname, 'playerdata'))
    playerdata_name_list = []
    for filename in filename_all:
        if filename[-4:] == '.dat':
            playerdata_name_list.append(str(filename.split('.dat')[0]))
    return playerdata_name_list


def get_offline_uuid_m1(player_name: str):
    flag = True
    url = 'https://api.yokinanya.icu/mcuuid/' + player_name
    try:
        js = json.loads(urlopen(url, timeout=10).read().decode('utf8'))
    except Exception as e:
        flag = False
    return js['offlinesplitteduuid'], flag


def get_online_uuid_m1(player_name: str):
    flag = True
    url = 'https://api.yokinanya.icu/mcuuid/' + player_name
    try:
        js = json.loads(urlopen(url, timeout=10).read().decode('utf8'))
    except Exception as e:
        flag = False
    return js['splitteduuid'], flag


def get_offline_uuid_m2(info: Info, player_name: str):
    # Get playdata list.
    uuid_list_old = get_playerdata_filename_list()

    # Create offline playerdata by Carpet Bot.
    server_cmd(info, f'/player {player_name} spawn')
    time.sleep(bot_wait_time)
    server_cmd(info, f'/player {player_name} kill')

    # Diff playerdata filename list.
    diff_uuid, count = '', 0
    uuid_list_new = get_playerdata_filename_list()
    for uuid in uuid_list_new:
        if uuid not in uuid_list_old:
            count = count + 1
            diff_uuid, Flag = uuid, True
    if diff_uuid == '' or count > 1:
        Flag = False
        Dprint(info, '未找到UUID，请重试')
    return diff_uuid, Flag


def get_offline_uuid_m3(player_name: str):
    # Thanks for [账号己注销 - BiliUID:5995861]
    md5Bytes = bytearray(hashlib.md5(b'OfflinePlayer:'+player_name.encode()).digest())
    md5Bytes[6] &= 0x0f    # clear version
    md5Bytes[6] |= 0x30    # set to version 3
    md5Bytes[8] &= 0x3f    # clear variant
    md5Bytes[8] |= 0x80    # set to IETF variant
    offline_uuid = md5Bytes.hex()[:8]+ '-'+ md5Bytes.hex()[8:12]+ '-'+ md5Bytes.hex()[12:16]+ '-'+ md5Bytes.hex()[16:20]+ '-'+ md5Bytes.hex()[20:]
    return offline_uuid, True


def add_whitelist(info: Info, player_name: str, online: bool):
    # Get whitelist name.
    whitelist_list: list = json_file_to_list(os.path.join(server_dirname, 'whitelist.json'))
    whitelist_name_list = []
    for value in whitelist_list:
        whitelist_name_list.append(value['name'])

    # Check player name in whitelist.
    if player_name in whitelist_name_list:
        Dprint(info, f'添加 {player_name} 白名时出现错误：白名单中已存在该玩家。')
    else:

    # Get uuid.
        if online == True:
            uuid = get_online_uuid_m1(player_name)
        else:
            if uuid_method == 1:
                uuid = get_offline_uuid_m1(player_name)
            elif uuid_method == 2:
                uuid = get_offline_uuid_m2(info, player_name)
            elif uuid_method == 3:
                uuid = get_offline_uuid_m3(player_name)

    # Add whitelist.
        if uuid[1]:
            new_whitelist_dict = {'uuid': uuid[0], 'name': player_name}
            whitelist_list.append(new_whitelist_dict)
            create_whitelist_file(whitelist_list, os.path.join(server_dirname), '_A_')
            time.sleep(1)
            server_cmd(info, '/whitelist reload')
            Dprint(info, f'\n|  白名单已添加新玩家:\n|  name: {player_name}\n|  UUID: {uuid[0]}')
        else:
            Dprint(info, f'添加 {player_name} 白名时出现错误，请重试。')


def remove_whitelist(info: Info, player_name: str):
    # Get whitelist name.
    whitelist_list: list = json_file_to_list(os.path.join(server_dirname, 'whitelist.json'))
    for value in whitelist_list:
        if player_name == value['name']:
            sub_dict = {'uuid': value['uuid'], 'name': value['name']}
            whitelist_list.remove(sub_dict)

    # Remove whitelist.
    create_whitelist_file(whitelist_list, os.path.join(server_dirname), '_R_')
    Dprint(info, f'白名单已移除玩家: name: {player_name}.')


def show_whitelist(info: Info):
    # Get whitelist name.
    whitelist_list: list = json_file_to_list(os.path.join(server_dirname, 'whitelist.json'))
    Dprint(info, '===== 服务器白名单 =====：')
    for i in range(0, len(whitelist_list)):
        player_name, player_uuid = whitelist_list[i]['name'], whitelist_list[i]['uuid']
        Dprint(info, f'{i+1}: {player_name} - {player_uuid}')


def show_help_msg(info: Info):
    Dprint(info, '''
    ============== 白名插件 ===============
    !!wlist add [name] (online) 添加白名单
    !!wlist remove [name]       移除白名单
    !!wlist list                显示完整白名单
    !!wlist help                显示此帮助信息
    ======================================''')


# MCDR.
def on_user_info(server: PluginServerInterface, info: Info):
    if info.content.startswith('!!wlist'):
        args = info.content.split(' ')

        try:
            if args[1] == 'add':
                if server.get_permission_level(info) >= 3:
                    if len(args) > 2:
                        if len(args) <= 3:
                            online = False
                        elif re.search('o|online', args[3]):
                            online = True
                        else:
                            online = False
                        add_whitelist(info, args[2],online)
                    else:
                        Dprint(info, '你不告诉我名字我加啥啊')
                else:
                    Dprint(info, '你想屁吃')

            elif args[1] == 'remove':
                if server.get_permission_level(info) >= 3:
                    if len(args) > 2:
                        remove_whitelist(info, args[2])
                    else:
                        Dprint(info, '你不告诉我名字我删谁啊')
                else:
                    Dprint(info, '你想屁吃')

            elif args[1] == 'list':
                if server.get_permission_level(info) >= 3:
                    show_whitelist(info)
                else:
                    Dprint(info, '你想屁吃')

            elif args[1] == 'help':
                show_help_msg(info)
            else:
                Dprint(info, f'解析命令树第二项时发生BUG.')
        except IndexError:
            show_help_msg(info)


def on_load(server: PluginServerInterface, prev):
    server.register_help_message('!!wlist', '白名插件')