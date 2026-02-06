# Bash completion for pythondocker
# Source: source /path/to/pythondocker.bash
# Or: source <(pythondocker completions bash)

_pythondocker() {
    local cur prev words cword
    _init_completion -s || return

    case $prev in
        -p|--python|-r|--requirements|-e|--encoding|-l|--log-file|-o|--output)
            return
            ;;
        remove)
            COMPREPLY=($(compgen -W "2.7 3.11 3.12 3.13 pypy3.11 pypy3.10 pypy2.7 jython" -- "$cur"))
            return
            ;;
    esac

    if [[ $cur == -* ]]; then
        COMPREPLY=($(compgen -W "--help --shell --python -p --requirements -r --args --env --verbose -v --force-recreate --encoding -e --no-deps --log-file -l --debug -d --offline" -- "$cur"))
    elif [[ $cword -eq 1 ]]; then
        COMPREPLY=($(compgen -W "list info clean remove freeze completions" -- "$cur") $(compgen -f -X '!*.py' -- "$cur") $(compgen -f -X '!*.ipynb' -- "$cur"))
    else
        _filedir
    fi
}

complete -F _pythondocker pythondocker
