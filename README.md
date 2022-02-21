# fastapi sample

Simple demonstration of Fastapi framework with [Exponea Testing HTTP server] (https://exponea-engineering-assignment.appspot.com/api/work) (ETS)
- endpoint returns JSON response {'time': int}
- endpoint can be inaccessible
- ...it means a lot of fun

Fastapi listens on /api/smart, ev. api/smart?timeout=int and whenever gets request, sends request to ETS (with some secret rules to follow) and processes response...mostly.

Features and/or limitations:
- when no timeout is defined, max timeout value is set to 600 ms
- when incorrect timeout number is entered (timeout <= 0 or timeout > 600), max timeout value is set to 600 ms (no compromise, life is a hard game, folks)
- when string value is used for timeout instead od number, JSON with error description is raised (cool Fastapi build-in message)
- when timeout is reached during processing or error occurs, server returns {'time': 0}

Used technologies
- Python and Fastapi :)
- Httpx for sending asynchronous request
- Docker - Dockerfile + docker-compose...cool combination (unfortunately no time to invite DigitalOcean to this party)
- GitHub of course
- Brain (I mean the thing consuming the most of human body energy without knowing exactly why) and a bunch of documentation and tutorials

Motivation:
- I have never worked with Fastapi or async mindset and Sunday was a good time to make a change

How to run:
- must have: Docker & docker-compose
- do: clone repo and go to folder where docker-compose.yml is located
- run: docker-compose up -d
- do: open your bowser and navigate to localhost:8080/api/smart
