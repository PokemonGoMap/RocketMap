# Docker

Docker is a great way to run "containerized" applications easily and without installing tons of stuff into your computer.

## Prerequisits

To get started, [install Docker by following their instructions](https://www.docker.com/products/docker).

Some VPS may have an image you can deploy that already has Dockers installed.

- [Docker's commandline reference](https://docs.docker.com/engine/reference/commandline/)

### Downloading image
Run this command to download the map files (image)
```
docker pull sych74/pokemongo-map
```

### Commandline params

This will print out the parmaters that you can use for your map
```
docker run --rm sych74/pokemongo-map:develop -h
```

### Installing map (default settings)

Run the following command with your `LOGINTYPE`,`USERNAME`, `PASSWORD`, `LOCATION`, `GMAPSKEY` and any add any other params you would like to use.

Login Type:  `google` or `ptc` (use your email as the username for google)

```
docker run -d --name pogomap \
-p 80 \
sych74/pokemongo-map:develop \
-a LOGINTYPE -u USERNAME -p PASSWORD \
-l "LOCATION" \
--gmaps-key "GMAPSKEY" \
-st 10
```

### Stopping and Starting Map

Once you already have a container with the map all we have to do it start and stop it by it's container name
```
docker stop pogomap
docker start pogomap
```

### Viewing Map logs

You can run this command to view the logs and exit by hitting `ctrl-c`

```
docker logs -f pogomap
```

## Updating Map version

Check https://hub.docker.com/r/sych74/pokemongo-map for updates

When you update, you remove all the current containers, pull the latest version, and restart everything fresh.

```
docker rm -f pogomap
docker pull sych74/pokemongo-map
```

Now just do the command from before to install again

If you don't wish to lose data you have collected then I suggest using a database like [MariaDB](https://pgm.readthedocs.io/en/develop/extras/mysql.html)

You can file the sqlite file under the /var/lib/docker/vfs/`<container name>`/usr/src/app/pogom.db and you can back that up if mysql is not an option for you.

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
