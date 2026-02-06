# Zsh completion for pythondocker
# Source: source /path/to/pythondocker.zsh
# Or: source <(pythondocker completions zsh)

_pythondocker() {
    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -C \
        '(-h --help)'{-h,--help}'[Показать справку]' \
        '(--shell)'--shell'[Интерактивный shell]' \
        '(-p --python)'{-p,--python}'[Версия Python]:версия:(2.7 3.11 3.12 3.13 pypy3.11 pypy3.10 pypy2.7 jython)' \
        '(-r --requirements)'{-r,--requirements}'[requirements.txt]:файл:_files -g "*.txt"' \
        '(--args)'--args'[Аргументы для скрипта]' \
        '(--env)'--env'[Переменные окружения]' \
        '(-v --verbose)'{-v,--verbose}'[Подробный вывод]' \
        '(--force-recreate)'--force-recreate'[Пересоздать окружение]' \
        '(-e --encoding)'{-e,--encoding}'[Кодировка]:кодировка:(utf-8 cp1251 latin1)' \
        '(--no-deps)'--no-deps'[Не устанавливать зависимости]' \
        '(-l --log-file)'{-l,--log-file}'[Файл лога]:файл:_files' \
        '(-d --debug)'{-d,--debug}'[Отладочный вывод]' \
        '(--offline)'--offline'[Режим offline]' \
        '1:команда или скрипт:((list\:Список\ окружений info\:Информация clean\:Очистка remove\:Удалить freeze\:pip\ freeze "*.py:Python скрипт" "*.ipynb:Jupyter notebook"))'
}

compdef _pythondocker pythondocker
