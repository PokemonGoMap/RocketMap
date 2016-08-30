# Docker

Docker is a great way to run "containerized" applications easily and without installing tons of stuff into your computer.

## Prerequisits

To get started, [install Docker by following their instructions](https://www.docker.com/products/docker).

## First Install

For your first install, there's only a few steps. Let's get to it!

### Start the Map 

You'll need to change the command line params. If you don't know what they are, you can run `docker run --rm pokemap/pokemongo-map -h` and you'll get the full help text. The command below examples out a very basic setup.

```
docker run -d --name pogomap \
  pokemap/pokemongo-map \
    -a ptc -u your -p login \
    -k 'google-maps-key' \
    -l 'coords' \
    -st 5
```

If you've like to see that the application is outputting (console logs) you can run `docker logs -f pogomap` and just type `ctrl-c` when you're done watching.

### Start an SSL Tunnel

At this point, the map is running, but you can't get to it. Also, you'll probably want to access this from places other than `localhost`. Finally, if you want location services to work, you'll need SSL.

We'll use [ngrok](https://ngrok.com/) to make a secure tunnel to solve all of those issues!

```
docker run -d --name ngrok --link pogomap \
  wernight/ngrok \
    ngrok http pogomap:5000
```

### Discover ngrok URL

Now that ngrok tunnel is running, let's see what domain you've been assigned. You can run this command to grab it from the ngrok instance

```
docker run --rm --link ngrok \
  appropriate/curl \
    sh -c "curl -s http://ngrok:4040/api/tunnels | grep -o 'https\?:\/\/[a-zA-Z0-9\.]\+'"
```

That should return something like:

```
http://random-string-here.ngrok.io
https://random-string-here.ngrok.io
```

Open that up and you're ready to rock!

## Updating Versions

When you update, you remove all the current containers, pull the latest version, and restart everything.

Run:

```
docker rm -f pogomap ngrok
docker pull pokemap/pokemongo-map
```

Then redo the steps from "First Install" and you'll be on the latest version!

## Running with docker compose 


```yml
version: "2"

services:
  web:
    image: pokemap/pokemongo-map:latest
    ports:
      - "5000:5000"
    environment:
      - POGOMAP_AUTH_SERVICE=ptc
      - POGOMAP_USERNAME=UserName
      - POGOMAP_PASSWORD=Password
      - POGOMAP_LOCATION=Chicago, IL
      - POGOMAP_STEP_LIMIT=5 
      - POGOMAP_GMAPS_KEY=SuperSecret 
    container_name: docker-pogomap
  ngrok:
    image: 'wernight/ngrok'
    command: ngrok http docker-pogomap:5000 -log stdout -log-level debug
    depends_on:
      - web
    container_name: docker-ngrok
```
