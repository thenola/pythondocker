# Интеграция PythonDocker с IDE

Инструкции по настройке запуска скриптов через PythonDocker в Visual Studio Code и PyCharm.

## Требования

- Установлен PythonDocker: `pip install python-docker-package`
- Команда `pythondocker` доступна в PATH

---

## Visual Studio Code

### Способ 1: Tasks (рекомендуется)

1. Скопируйте содержимое `ide/vscode/tasks.json` в `.vscode/tasks.json` вашего проекта.
2. Если папки `.vscode` нет — создайте её в корне проекта.

**Или** скопируйте файл целиком:
```bash
mkdir -p .vscode
cp ide/vscode/tasks.json .vscode/
```

3. Откройте любой Python-файл и нажмите:
   - **Ctrl+Shift+B** (Windows/Linux) или **Cmd+Shift+B** (macOS) — запуск по умолчанию
   - Или: **Terminal → Run Build Task** и выберите нужную задачу

**Доступные задачи:**
- **PythonDocker: Run current file** — автопроверка версии (по умолчанию)
- **PythonDocker: Run with Python 2.7**
- **PythonDocker: Run with requirements**
- **PythonDocker: Run with encoding cp1251**

### Способ 2: Launch (Run and Debug)

1. Скопируйте `ide/vscode/launch.json` в `.vscode/launch.json`.
2. Откройте панель **Run and Debug** (Ctrl+Shift+D).
3. Выберите конфигурацию и нажмите зелёную кнопку запуска.

> **Примечание:** Конфигурация использует встроенный терминал. Если Run and Debug не срабатывает, используйте Tasks (Ctrl+Shift+B).

### Горячие клавиши

Можно назначить задачу на свою клавишу:
1. **File → Preferences → Keyboard Shortcuts**
2. Найдите `workbench.action.tasks.runTask`
3. Назначьте, например, **F5** или **Ctrl+F5**

---

## PyCharm

### Настройка External Tools

1. Откройте **Settings/Preferences** (Ctrl+Alt+S).
2. Перейдите в **Tools → External Tools**.
3. Нажмите **+** (Add).

#### Инструмент 1: PythonDocker Run

| Поле | Значение |
|------|----------|
| Name | `PythonDocker: Run` |
| Program | `pythondocker` |
| Arguments | `$FilePath$` |
| Working directory | `$FileDir$` |

#### Инструмент 2: PythonDocker Run (Python 2.7)

| Поле | Значение |
|------|----------|
| Name | `PythonDocker: Run (2.7)` |
| Program | `pythondocker` |
| Arguments | `$FilePath$ --python 2.7` |
| Working directory | `$FileDir$` |

#### Инструмент 3: С requirements.txt

| Поле | Значение |
|------|----------|
| Name | `PythonDocker: Run (requirements)` |
| Program | `pythondocker` |
| Arguments | `$FilePath$ --requirements $ProjectFileDir$/requirements.txt` |
| Working directory | `$FileDir$` |

4. Сохраните настройки (**Apply** → **OK**).

### Использование

- **Правый клик по файлу** → **External Tools** → **PythonDocker: Run**
- Или через меню **Tools** → **External Tools** → выберите нужный инструмент

### Добавление в Run Configurations (опционально)

Чтобы запускать через зелёную кнопку Run:

1. **Run → Edit Configurations**
2. **+** → **Shell Script**
3. Укажите:
   - **Name:** `PythonDocker`
   - **Script text:** `pythondocker "$FilePath$"`
   - **Working directory:** `$FileDir$`
4. Сохраните. Теперь можно выбрать эту конфигурацию и нажать Run.

---

## Переменные окружения в IDE

| VS Code | PyCharm | Описание |
|---------|---------|----------|
| `${file}` | `$FilePath$` | Путь к текущему файлу |
| `${fileDirname}` | `$FileDir$` | Директория файла |
| `${workspaceFolder}` | `$ProjectFileDir$` | Корень проекта |

---

## Устранение неполадок

### «pythondocker не найден»

Убедитесь, что PythonDocker установлен и в PATH:
```bash
pip install python-docker-package
pythondocker --help
```

### VS Code не находит задачу

Проверьте, что `.vscode/tasks.json` в корне проекта (рядом с открытой папкой).

### PyCharm: инструмент не запускается

- Укажите полный путь к `pythondocker`: `C:\...\Scripts\pythondocker.exe` (Windows) или `/usr/local/bin/pythondocker` (Linux/macOS).
- Узнать путь: `where pythondocker` (Windows) или `which pythondocker` (Linux/macOS).
