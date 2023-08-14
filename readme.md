# SSH-MANAGER

### Зависимости
- python3.11

### Билд под Unix
- pyinstaller -D -F -n ssh-manager -c "main.py"

## Использование

1) Закинуть сбилженый файл в /usr/bin или /local/bin или в любую другую папку, которая находится в path
2) создать папку ssh-manager в /etc
3) sudo ssh-manager init *Путь до папки, в которой хранятся sh файлы и пем ключи\* *Путь до папки, числящейся в path (По стандарту /usr/bin)\*
4) ssh-manager -h что бы посмотреть список команд