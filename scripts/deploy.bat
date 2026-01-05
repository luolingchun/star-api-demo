@echo off
setlocal
call ..\.venv\Scripts\activate.bat
set PG_URL=172.18.77.18:20262
cd ..\src
set pythonpath=%cd%
star create_db
star drop_alembic_version && for %%f in (.\migrations\versions\*) do if /i not "%%~nxf"=="__init__.py" del /q "%%f"
cd .\migrations
alembic revision --autogenerate
alembic upgrade head
cd ..
star init_db
star register_permission
pause