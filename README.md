# spartan

## Project Setup
```bash
pyenv install 3.11.0
pyenv virtualenv 3.11.0 py3.11-spartan
pyenv activate py3.11-spartan
```

## UI
```bash
cd spartan-engine
uvicorn ui.main:app --reload
```
urls:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc
