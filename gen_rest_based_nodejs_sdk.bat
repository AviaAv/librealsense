@echo off
REM Generate Python SDK from OpenAPI spec
echo.Note: triggering openapi-generator-cli requires installing it using npm
call openapi-generator-cli generate -i http://127.0.0.1:8000/openapi.json -g javascript -o ./nodejs-client

echo.client generated, installing NodeJS requirements using npm...

set /p answer="Do you want to delete the folder used for generation? (y/N): "
if /i "%answer%"=="y" (
    echo Folder will be deleted, packing and installing
    call npm install .\nodejs-client\
    cd nodejs-client
    npm pack
    cd ..
    REM this might need to be modified for future versions
    npm install ./nodejs-client/real_sense_api-1.0.0.tgz
    rmdir /s /q .\nodejs-client\
) else (
    echo Folder won't be deleted, installing from it
    call npm install .\nodejs-client\
)

echo.setup completed
