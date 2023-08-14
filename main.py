import dataclasses
import sys
import os
import json
from pathlib import Path


@dataclasses.dataclass
class Config:
    config_dir: str
    exec_dir: str


try:
    CONFIG = Config(**json.load(open('/etc/ssh_manager/config.json', 'r')))
except FileNotFoundError:
    print(
        'Необходимо сначала прописать sudo ssh-manager init *Путь к папке с конфигами* '
        '*Путь к доступной папке, находящейся в переменной PATH*')


def enable(name):
    os.system(f'cp {CONFIG.config_dir}/server_connections/ssh_shortcuts/{name}.sh {CONFIG.exec_dir}/{name}.sh')


def disable(name):
    os.system(f'rm {CONFIG.exec_dir}/{name}.sh')


def init(config_dir_path, exec_dir_path='/usr/bin'):
    config_dir = Path(config_dir_path)
    exec_dir = Path(exec_dir_path)
    try:
        os.mkdir('/etc/ssh_manager')
    except FileExistsError:
        pass
    json.dump(
        {
            'config_dir': str(config_dir),
            'exec_dir': str(exec_dir)
        },
        open('/etc/ssh_manager/config.json', 'w')
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
    os.system(f'chmod 777 {CONFIG.config_dir}/server_connections/ssh_shortcuts/{name}.sh')


def give_pem_permitions(name):
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
}


def main(args):
    func_dict[args[0]](*args[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
