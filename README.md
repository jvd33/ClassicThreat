![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiV2FxUGtoc05KOEVUeXdkbEVHK2NUM3hXTjkzaEk2dTd0YWVhZy92djZNVnlrcE15NFVIRXMvRk81STV0QldOTTRNRER1dURLaGV3czNSbGs5NWkyNXZrPSIsIml2UGFyYW1ldGVyU3BlYyI6IjQ2cHJqb1dXckVDVW14MGwiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

# [ClassicThreat](https://classicthreat.com)

ClassicThreat is a tool meant to help tanks in Classic WoW analyze their performance. This application seeks to build on top of the extensive reporting capabilities of [Warcraft Logs](classic.warcraftlogs.com) and provide analysis that is more valuable and accessible than previously possible.

Contact the author on discord at coandca#1313 or via GitHub
# Features and Usage

Right now, the application supports the calculation of Threat per Second (TPS) for Warrior tanks, Fury/Prot and Deep Protection specced. 

Given a link to a Warcraft logs report (optionally with a fight URL fragment to specify just one fight to analyze), the application will:
  - Retrieve and validate the metadata for the report URL, including boss fights and kill times.
  - Given the boss fight information, the application requests performance metrics for each specific boss encounter (which you can see in more detail on the website itself)
  - Processes the responses and estimates threat per second from ability usage and other events seen in the logs

Hopefully, this will be improved upon and we can get some actually valuable tank metrics spread around

### Tech

This was also kind of a tech playground for me, so there's some neat technologies being used:

* [Python3.7.5](https://www.python.org/) - The entire backend is writen in Python 3.7.5, using FastAPI as the API framework.
* [FastAPI](https://github.com/tiangolo/fastapi) - A powerful, completely async alternative to some of the more traditional Python frameworks
* [Redis](https://redis.io/) - Used to cache report results (possibly for future analysis) to improve performance primarily
* [VueJS](https://vuejs.org/)/[Quasar](https://quasar.dev/) - A powerful and easy-to-use modern web dev framework
* [node.js](https://nodejs.org/en/) - To support the frontend
* [AWS ECS](https://aws.amazon.com/ecs/) - The entire application is hosted in ECS, with a service for the front end, backend, and redis server to provide autoscaling and scalability as needed since this does some pretty hefty calculations

### Dev & Requirements

* Python3.7.5
* NodeJS 13.5
* Docker/Docker-compose


##### Building and running the backend 
make a Python 3.7.5 virtual environment first, then:
```sh
$ (venv) cd backend
$ (venv) pip install -r requirements.txt
$ (venv) uvicorn main:app --reload
```

The backend API will now be running on `localhost:8000`.

##### Building and running the frontend
Install node, npm etc etc...
```sh
$ cd tps-calc-ui
$ npm i
$ npm run serve
```

The front end will now be running on `localhost:8080`.

Environment variables are used for API urls and API keys, make either a global `.env` file or .env files for each environment at `/backend/.env` and `tps-calc-ui/.env`, using `.env.example` as a reference for the variables needed to run the application.

#### Building prod
To build prod, all you need to do is:
```sh
$ docker-compose up --build
```

### Development

Want to contribute? Clone the repo and submit a PR, if the code meets software best practices and adds value to the application I'll probably just approve it. 

To report bugs/errors, simply open an issue on GitHub stating the issue, repro steps, and any other applicable information.

### Todos
 - Calculate DPS needed to rip given the TPS per class
 - Bear tanks
 - Paladin tanks? (lol memespec)
 - Split TPS across individual mobs in the boss encounters (e.g. Lucifron TPS, Flamewaker 1 TPS, Flamewaker 2 TPS)
 - DPS/TPS correlation, tank survivability, CPM, etc.
 - Literally any other valuable analysis because this is so much easier than using WarcraftLogs
 - Write Tests (lazy)
 - Refactor pretty much all the `core/tasks.py` logic
 - Make calls to WCL more performant, they seem to not be running concurrently

License
----

MIT


