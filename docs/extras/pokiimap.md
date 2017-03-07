# Get data on android with PokiiMap

If you want to see the Pokemon data on an android phone, you can open the web browser interface or use an app to connect to the server.
On android you can use [PokiiMap](http://pokiimap.readthedocs.io/en/latest/livemap.html#private-server).


## Bind the server to an ip address

By default, PokemonGO-map listens on address 127.0.0.1, this address cannot be accessed from another device.
You need to change it first. 
Find out the local ip address of the server: http://bit.ly/2aweVR1 (if you have a local server) and http://bit.ly/1dWVBmR (if you want to remote server).

Edit config\config.init to change the listen address to the ip address of the server

   ```
   # Webserver settings
   host:               192.168.11.48 # address to listen on (default 127.0.0.1)
   ```

## Connect PokiiMap to your running server

Download the latest release of [PokiiMap](http://pokiimap.readthedocs.io/en/latest/download.html) and install it on an android phone. 
The ip address of the server needs to be accessible from the android phone. If it's a private server, it means they need to be on the same WIFI network. 

see [this doc](http://pokiimap.readthedocs.io/en/latest/livemap.html#private-server) for detailed instructions. 

