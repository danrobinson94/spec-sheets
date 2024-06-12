# spec-sheets
Use PyMuPDF library to analyze pdf's quickly

Go to route folder and run this command:
```python -m venv venv```
```source venv/bin/activate```
```pip install -r requirements.txt```
```uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload```

For debugging in VSCode
~~~{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload"
            ],
            "jinja": true,
            "cwd": "${workspaceFolder}/spec-sheets",
            "python": "${workspaceFolder}/spec-sheets/venv/bin/python"
        }
    ]
}~~~