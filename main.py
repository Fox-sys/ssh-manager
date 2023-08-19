import dataclasses
import sys
import os
import json
from pathlib import Path
import readchar

CONFIG_DIR = os.path.expanduser('~/ssh_manager')


@dataclasses.dataclass
class Config:
    config_dir: str
    exec_dir: str
    list_active: list[str]

    def to_dict(self):
        return {
            'config_dir': self.config_dir,
            'exec_dir': self.exec_dir,
            'list_active': self.list_active
        }


# Создавать папку для конфига
try:
    os.mkdir(CONFIG_DIR)
except FileExistsError:
    pass

try:
    CONFIG = Config(**json.load(open(f'{CONFIG_DIR}/config.json', 'r')))
except FileNotFoundError:
    pass
except TypeError:
    pass


def list_active():
    print('Список активных подключений:')
    print((' ' * 2).join(CONFIG.list_active))


def enable(name):
    """Закинуть файл в директорию с исполняемыми файлами"""
    if name not in CONFIG.list_active:
        CONFIG.list_active.append(name)
    os.system(f'cp {CONFIG.config_dir}/server_connections/ssh_shortcuts/{name}.sh {CONFIG.exec_dir}/{name}.sh')
    _save_active()


def disable(name):
    """Убрать файл из директории с исполняемыми файлами"""
    if name in CONFIG.list_active:
        CONFIG.list_active.remove(name)
    os.system(f'rm {CONFIG.exec_dir}/{name}.sh')
    _save_active()


def _save_active():
    with open(f'{CONFIG_DIR}/config.json', 'w') as file:
        json.dump(CONFIG.to_dict(), file)


def init(config_dir_path, exec_dir_path='/usr/bin'):
    """Конфигурация приложения"""
    config_dir = Path(config_dir_path)
    exec_dir = Path(exec_dir_path)
    json.dump(
        {
            'config_dir': str(config_dir),
            'exec_dir': str(exec_dir),
            'list_active': []
        },
        open(f'/{CONFIG_DIR}/config.json', 'w')
    )
    try:
        os.mkdir(config_dir / 'server_connections')
    except FileExistsError:
        pass
    try:
        os.mkdir(config_dir / 'server_connections' / 'ssh_shortcuts')
    except FileExistsError:
        pass
    try:
        os.mkdir(config_dir / 'server_connections' / 'pem_keys')
    except FileExistsError:
        pass


def give_sh_permitions(name):
    """Дать разрешения файлы для запуска"""
    os.system(f'chmod 777 {CONFIG.config_dir}/server_connections/ssh_shortcuts/{name}.sh')


def give_pem_permitions(name):
    """Дать разрешение файлу с ключём"""
    os.system(f'chmod 600 {CONFIG.config_dir}/server_connections/pem_keys/{name}')


def help():
    print('enable (-e) - включить sh\n\tПередавать:\n\tназвание sh файла')
    print('disable (-d) - выключить sh\n\tПередавать:\n\tназвание sh файла')
    print('init - начальная настройка\n\tПередавать:\n\tПуть до папки с конфигами\n\tПуть до папки в '
          'которой находятся исполняемые файлы (По умолчанию /usr/bin)')
    print('give_sh_permitions (-sp) - дать разрешение для запуска файла \n\tПередавать:\n\tназвание sh файла')
    print(
        'give_pem_permitions (-pp) - дать разрешение для подключения pem файла'
        '\n\tПередавать:\n\tназвание pem файла (обязательно дописывать .pem)')
    print(
        'list_active (-la) - Список активных подключений'
    )
    print(
        'create (-c) - создаёт новое подключение или заменяет существующее'
    )


def create_connection():
    print('Выберете способ авторизации при подключении к серверу')
    print('1 - sshpass')
    print('2 - pem key')
    print('3 - без авторизации')
    print(choice := str(readchar.readchar()))
    match choice:
        case '1':
            template = 'sshpass -p {password} ssh {username}@{ip}'
        case '2':
            template = 'ssh -i ' + CONFIG.config_dir + '/server_connections/pem_keys/{pem_key_name} {username}@{ip}'
        case '3':
            template = 'ssh {username}@{ip}'
        case _:
            print('Вы выбрали не существующий вариант')
            return
    name = input('Введите название подключения: ')
    username = input('Введите пользователя, под которым вы хотите подключаться: ')
    ip = input('Введите ip/домен сервера, к которому хотите подключаться: ')
    password = ''
    pem_key_name = ''
    if choice == '1':
        password = input('Введите пароль: ')
    if choice == '2':
        pem_key_name = input('Введите полное название файла с ключом (вместе с расширением): ')
    print(f'Проверьте корректность данных')
    print(f'Название файла {name}.sh')
    print(f'username: {username}')
    print(f'ip/домен: {ip}')
    if password:
        print(f'Пароль: {password}')
    if pem_key_name:
        print(f'Путь до ключа: ' + str(Path(CONFIG.config_dir) / 'server_connections' / 'pem_keys' / pem_key_name))
    print('Всё верно [y/N]:')
    print(choice := str(readchar.readchar()))
    if choice != 'y':
        print('Abort')
        return
    with open(f'{CONFIG.config_dir}/server_connections/ssh_shortcuts/{name}.sh', 'w') as file:
        file.write(template.format(password=password, username=username, ip=ip, pem_key_name=pem_key_name))
    print(f'Создано новое подключение, название файла {name}.sh')


def list_all():
    print('Список подключений:')
    os.system(f'ls {CONFIG.config_dir}/server_connections/ssh_shortcuts')


func_dict = {
    'disable': disable,
    'enable': enable,
    'init': init,
    'give_sh_permitions': give_sh_permitions,
    'give_pem_permitions': give_pem_permitions,
    '-e': enable,
    '-d': disable,
    '-sp': give_sh_permitions,
    '-pp': give_pem_permitions,
    'help': help,
    '-h': help,
    'list_active': list_active,
    '-la': list_active,
    '-l': list_all,
    'list': list_all,
    '-c': create_connection,
    'create': create_connection,
}


def main(args):
    try:
        func_dict[args[0]](*args[1:])
    except NameError:
        print(
            'Необходимо создать конфиг, пропишите ssh-manager init'
        )


if __name__ == '__main__':
    main(sys.argv[1:])
