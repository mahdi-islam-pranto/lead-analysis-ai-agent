from fastapi import FastAPI

app = FastAPI()

# a simple hello world get request
@app.get("/")
def hello():
    return {
        "status": "success",
        "message": "Hello World"
    }

# a simple post request with a name parameter
@app.post("/name")
def post_name(name: str):
    try:
        return {
        "status": "200",
        "greeting" : "hello {name}".format(name=name)
    }
    except Exception as e:
        return {
            "status": "500",
            "message": "Internal Server Error"
        }
    
