from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import glob
import importlib
import uvicorn
import sys  
  
class StdoutStderrLogger(object):  
    def __init__(self, file_path):  
        self.log_file = open(file_path, "a")  
  
    def write(self, message):  
        # This method gets called whenever print is used  
        self.log_file.write(message)  
  
    def flush(self):  
        # This can be important for smaller writes to ensure they're actually written out  
        self.log_file.flush()  
  
# Replace /path/to/your/logfile.log with the actual path to your log file  
log_path = "/scripts/sys.applog"  
logger = StdoutStderrLogger(log_path)  
  
# Redirecting stdout and stderr  
sys.stdout = logger  
sys.stderr = logger  
  
# From this point onwards, print statements and errors will go to /path/to/your/logfile.log  
print("App Log capturing started.")  

log_config = {  
    "version": 1,  
    "disable_existing_loggers": False,  
    "formatters": {  
        "default": {  
            "()": "uvicorn.logging.DefaultFormatter",  
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",  
            "use_colors": True,  # This might not work as expected in a file.  
            "datefmt": "%Y-%m-%d %H:%M:%S",  
        },  
    },  
    "handlers": {  
        "file": {  
            "level": "DEBUG",  
            "class": "logging.FileHandler",  
            "filename": "/scripts/sys.applog",  
            "formatter": "default",  
        },  
    },  
    "loggers": {  
        "uvicorn": {"handlers": ["file"], "level": "DEBUG"},  
        "uvicorn.error": {"level": "DEBUG"},  
        "uvicorn.access": {"handlers": ["file"], "level": "DEBUG"},  
        "": {"handlers": ["file"], "level": "DEBUG"},
    },  
}  


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router_files = glob.glob("app/routers/*.py")

# Import each file and add the routes to the app
for router_file in router_files:
    if "model" in router_file:
        continue
    module = router_file[:-3].replace('/', '.')
    print(module)
    router_module = importlib.import_module(module)
    app.include_router(router_module.router)


if __name__ == "__main__":  
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=log_config,reload=False)  