# Kosha Crowdstrike Falcon Connector

Crowdstrike Falcon can be used to help you improve your incident response operations by standardizing and streamlining your processes

![Crowdstrike Falcon](images/cs-logo.png)

This Connector API exposes REST API endpoints to perform any operations on Falcon SDK in a simple, quick and intuitive fashion.

It describes various API operations, related request and response structures, and error codes. 

## Build

To start the virtualenv of the project, run
```
    pipenv shell
```

To install dependencies, run
```
    pipenv install
```

## Run

To run the project, simply provide env variables crowdstrike account credentials such as client key, client secret to connect to.


```bash
CLIENT_ID=<CLIENT_ID> CLIENT_SECRET=<CLIENT_SECRET>  uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8002
```

This will start a worker and expose the API on port `8002` on the host machine 

Swagger docs is available at `https://localhost:8002/docs`
