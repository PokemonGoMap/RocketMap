# How to Setup Webhooks on Linux with Node.js

## Supported Events
* Pokemon Spawn

## Requirements

* Node.js (min. v4.4.7)
* Python (WORKS ONLY WITH 2.7)
* PiP (min 8.1.2)
* NPM
* A linux distribution

## Webserver
At first we will setup the webserver to register post requests. You can use this small setup:

	var express = require("express");
	var bodyParser = require("body-parser");
	var morgan = require("morgan");

	var app = express();

	app.use(morgan("dev"));
	app.use(bodyParser.json());
	app.use(bodyParser.urlencoded({extended: true})); 
	app.use(bodyParser());	

	app.post("/", function(req, res){

		console.log(req.body);
		res.send("ok");

	});

	app.listen(80);

Now you can insert your code to work with retrieving pokemon info.
Do not forget to startup your webserver and install all dependencies

	sudo npm install --save express body-parser morgan
	sudo node app.js

## Setting up your worker
To feed our webserver with information, we need to tell your worker to contact your webserver. Nothing easier than this:

	sudo python ./runserver.py ... --webhook "http://your.url/"

Now you are done!

## (Optional) Setup worker with HTTPS
If your webserver is reachable through HTTPS,you have to install some dependencies on your linux system.

	sudo apt-get install python-dev python-openssl
	sudo pip install requests[security]