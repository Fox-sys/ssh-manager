import dataclasses
import sys
import os
import json
from pathlib import Path


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
    os.mkdir('/etc/ssh_manager')
except FileExistsError:
    pass

try:
    CONFIG = Config(**json.load(open('/etc/ssh_manager/config.json', 'r')))
except FileNotFoundError:
    print(
        'Необходимо сначала прописать sudo ssh-manager init *Путь к папке с конфигами* '
        '*Путь к доступной папке, находящейся в переменной PATH*')
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
    with open('/etc/ssh_manager/config.json', 'w') as file:
        json.dump(CONFIG.to_dict(), file)


def init(config_dir_path, exec_dir_path='/usr/bin'):
    """Конфигурация приложения"""
    config_dir = Path(config_dir_path)
    exec_dir = Path(exec_dir_path)
    try:
        os.mkdir('/etc/ssh_manager')
    except FileExistsError:
        pass
    json.dump(
        {
            'config_dir': str(config_dir),
            'exec_dir': str(exec_dir),
            'list_active': []
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
    'list': list_all
}


def main(args):
    try:
        func_dict[args[0]](*args[1:])
    except NameError:
        print(
            'Нужно пересоздать конфиг, возможно вы перешли со старой версии по, пропишите sudo ssh-manager init ещё раз'
        )


if __name__ == '__main__':
    main(sys.argv[1:])
