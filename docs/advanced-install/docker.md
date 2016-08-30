# Docker

Docker is a great way to run "containerized" applications easily and without installing tons of stuff into your computer. 

If you are not familiar with Python, pip or the other stuff that is good to know before launching a PokemonGo-Map server, Docker is probably the easiest approach for you.

## Prerequisites

To get started, [install Docker by following their instructions](https://www.docker.com/products/docker).

## Introduction

The quickest way to get PokemonGo-Map up and running with docker is quite simple. However, given the disposable nature of docker containers, and the fact that the default database for PokemonGo-Map is SQLite, your data won't be persistent. In case the container is stopped or crashes, all the collected data will be lost.

If that doesn't bother you, and you just want to give PokemonGo-Map a go, keep on reading. If you prefer a persistent setup, skip to "Advanced Docker Setup"

## Simple Docker Setup

### Starting the server 

In order to start the map, you've got to run your docker container with a few arguments, such as authentication type, account, password, desired location and steps. If you don't know which arguments are necessary, you can use the following command to get help:

```
docker run --rm pokemap/pokemongo-map -h
```

To be able to access the map in your machine via browser, you've got to bind a port on you host to the one wich will be used by the map (default is 5000). The following docker run command is an example of to launch a container with a very basic setup of the map, following the instructions above:

```
docker run -d --name pogomap -p 5000:5000 \
  pokemap/pokemongo-map \
    -a ptc -u username -p password \
    -k 'your-google-maps-key' \
    -l 'lat, lon' \
    -st 5
```

If you would like to see what are the server's outputs (console logs), you can run:

```
docker logs -f pogomap
``` 

Press `ctrl-c` when you're done.

### Stopping the server

In the step above we launched our server in a container named 'pogomap'. Therefore, to stop it as simple as:

```
docker stop pogomap
```

After stopping a named container, if you would like to launch a new one re-using such name, you have to remove it first, or else it will not be allowed:

```
docker rm pogomap
```

### Local access

Given that we have bound port 5000 in your machine to port 5000 in the container, which the server is listening to, to access the server from your machine you just got to access 'http://localhost:5000' in you preferred browser.

### External access

If external access is necessary, there are plenty of ways to expose you server to the web. In this guide we are going to approach this using a [ngrok](https://ngrok.com/) container, which will create a secure introspected tunnel to your server. This is also very simple to do. Simply run the following command:

```
docker run -d --name ngrok --link pogomap \
  wernight/ngrok \
    ngrok http pogomap:5000
```

After the ngrok container is launched, we need to discover what domain you've been assigned. The following command can be used to obtain the domain:

```
docker run --rm --link ngrok \
  appropriate/curl \
    sh -c "curl -s http://ngrok:4040/api/tunnels | grep -o 'https\?:\/\/[a-zA-Z0-9\.]\+'"
```

That should output something like:

```
http://random-string-here.ngrok.io
https://random-string-here.ngrok.io
```

Open that URL in your browser and you're ready to rock!

## Updating Versions

In order to update your PokemonGo-Map docker image, you should stop/remove all the current running containers (refer to Stopping the server), pull the latest docker image version, and restart everything. To pull the latest image, use the following command:

```
docker pull pokemap/pokemongo-map
```

If you are running a ngrok container, you've got to stop it as well. To start the server after updating your image, simply use the same commands that were used before, and the containers will be launched with the latest version.

## Running on docker cloud 

If you want to run pokemongo-map on a service that doesn't support arguments like docker cloud or ECS, you'll need to use one of the more specialised images out there that supports variables. The image `ashex/pokemongo-map` handles variables, below is an example:

```bash
  docker run -d -P \
    -e "AUTH_SERVICE=ptc" \
    -e "USERNAME=UserName" \
    -e "PASSWORD=Password" \
    -e "LOCATION=Seattle, WA" \
    -e "STEP_LIMIT=5" \
    -e "GMAPS_KEY=SUPERSECRET" \
    ashex/pokemongo-map
```

## Advanced Docker Setup

In this session, we are going to approach a docker setup that allows data persistence. To do so, we are going to use the docker image for [MySQL](https://hub.docker.com/_/mysql/) as our database, and have our server(s) connect to it. This could be done by linking docker containers. However, linking is considered a [legacy feature](https://docs.docker.com/engine/userguide/networking/default_network/dockerlinks/#/legacy-container-links), so we are going to use the docker network approach.

### Creating the Docker Network

The first step is very simple, we are going to use the following command to create a docker network called 'pogonw':

``` 
docker network create pogonw
```

### Launching the database

Now that we have the network, we gotta launch the database into it. As noted in the introduction, docker containers are disposable. Sharing a directory in you machine with the docker container will allow the MySQL server to use such directory to store its data, and ensure it will remain there after the container stops. You can create this directory wherever you like. In this example we going to create a dir called /path/to/mysql/ just for the sake of it.

```
mkdir /path/to/mysql/
```

After the directory is created, we can lauch the MySQL container. Use the following command to launch a container named 'db' into our previously created network, sharing the directory we just created:

```
docker run --name db --net=pogonw -v /path/to/mysql/:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=yourpassword  -d mysql:5.6.32
```

The launched MySQL server will have a single user called 'root' and its password will be 'yourpassword'. However, there is no database/schema that we can use as the server will be empty on the first run, so we've got to create it. In order to connect to the server, and execute a MySQL command, execute this command:

```
docker run -it --net=pogonw --rm mysql sh -c 'exec mysql -hdb -P3306 -uroot -pyourpassword'
```

In the above, `-h` indicates the host name, which is the 'db' container, `-p` is 3306 which is the MySQL default port, `-u` is the default root user and `-p` was the password we provided. This will put you in the MySQL command line interface:

```
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 243
Server version: 5.6.32 MySQL Community Server (GPL)

Copyright (c) 2000, 2016, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>
```

Now we need to create a database in the server:

```
CREATE DATABASE pogodb;
```

Which should output:

```
Query OK, 1 row affected (0.01 sec)
```

Once you get that done, simply type `quit` and press enter to exit the MySQL CLI.

### Launching the PokemonGo-map server

Now that we have a persistent database up and running, we need to launch our PokemonGo-map server. To do so, we are going to use a slightly modified version of the docker run command from the "Simple Docker Setup" session. This time we need to launch our server inside the network and pass the database infos to it. Here's an example:

```
docker run -d --name pogomap --net=pogonw -p 5000:5000 \
  pokemap/pokemongo-map \
    -a ptc -u username -p password \
    -k 'your-google-maps-key' \
    -l 'lat, lon' \
    -st 5 \
    --db-type mysql \
    --db-host db \
    --db-port 3306 \
    --db-name pogodb \
    --db-user root \
    --db-pass yourpassword 
```

Just like before, in order to check the server's logs we can use 

```
docker logs -f pogomap
```

If everything is fine, it should be up and running.

### Launching workers

If you would like to launch a different worker to scan a different area, but sharing the same db, it is just as easy. We can use the docker run command from above, changing the container's name, and the necessary account and coordinate infos. For example:

```
docker run -d --name pogomap2 --net=pogonw \
  pokemap/pokemongo-map \
    -a ptc -u username2 -p password2 \
    -k 'your-google-maps-key' \
    -l 'newlat, newlon' \
    -st 5 \
    --db-type mysql \
    --db-host db \
    --db-port 3306 \
    --db-name pogodb \
    --db-user root \
    --db-pass yourpassword 
    -ns
```

The difference here being: we are launching with the `-ns` flag, which means that this container will only run the searcher and not the webserver (front-end), because we can use the webserver from the first container. That also means we can get rid of `-p 5000:5000`, as we dont need to bind that port anymore. 

If for some reason you would like this container to launch the webserver as well, simply remove the `-ns` flag and add back the `-p`, with a different pairing as 5000 will be already taken in the host, such as -p 5001:5000.

### External Access

Just like before, we can use ngrok to provide external access to the webserver. The only thing we need to change in the command from the previous session is the link flag, instead we need to launch ngrok in our network:

```
docker run -d --name ngrok --net=pogonw \
  wernight/ngrok \
    ngrok http pogomap:5000
```

To obtain the assigned domain from ngrok, we also need to execute the previous command in our network instead of using links:

```
docker run --rm --net=pogonw \
  appropriate/curl \
    sh -c "curl -s http://ngrok:4040/api/tunnels | grep -o 'https\?:\/\/[a-zA-Z0-9\.]\+'"
```

### Inspecting the network

If at any moment you would like to check what containers are running, you can execute:

```
docker ps -a
```

If you would like more detailed information about the network, such as its subnet, gateway or the ips that were assigned to the containers, you can execute:

```
docker network inspect pogonw
```

### Setting up notifications

If you have a docker image for a notification webhook that you want to be called by the server/workers, such as [PokeAlarm](https://github.com/kvangent/PokeAlarm), you can launch such container in the 'pogonw' network and give it a name such as 'hook'. This guide won't cover how to do that, but once such container is configured and running, you can stop your server/workers and relaunch them with the added flags: `-wh`, `--wh-threads` and `--webhook-updates-only`. For example, if the hook was listening to port 4000, and we wanted 3 threads to post updates only to the hook:

```
docker run -d --name pogomap --net=pogonw -p 5000:5000 \
  pokemap/pokemongo-map \
    -a ptc -u username -p password \
    -k 'your-google-maps-key' \
    -l 'lat, lon' \
    -st 5 \
    --db-type mysql \
    --db-host db \
    --db-port 3306 \
    --db-name pogodb \
    --db-user root \
    --db-pass yourpassword \
    -wh 'http://hook:4000' \ 
    --wh-threads 3 \
    --webhook-updates-only
```
