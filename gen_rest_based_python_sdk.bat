@echo off
REM Generate Python SDK from OpenAPI spec
echo.Note: triggering openapi-generator-cli requires installing it using npm
call openapi-generator-cli generate -i http://127.0.0.1:8000/openapi.json -g python -o python_sdk

echo.client generated, installing python requirements...
cd python_sdk
call pip install .
echo.setup completed
cd ..

set /p answer="Do you want to delete the folder used for generation? (y/N): "
if /i "%answer%"=="y" (
    rmdir /s /q python_sdk
    echo python_sdk folder has been deleted.
) else (
    echo Operation cancelled.
)
