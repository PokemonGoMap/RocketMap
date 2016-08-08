# Nginx

If you do not want to expose pokemongo-map to the web directly or you want to place it under a prefix, follow this guide:

Assuming the following:

* You are running pokemongo-map on the default port 5000
* You've already made your machine available externally (for example, [port forwarding](external.md))

1. Install nginx (I'm not walking you through that, google will assist) - http://nginx.org/en/linux_packages.html
2. In /etc/nginx/nginx.conf add the following before the last `}`

   ```
   include conf.d/pokemongo-map.conf;
   ```

3. Create a file /etc/nginx/conf.d/pokemongo-map.conf and place the following in it:

   ```
   server {
       location /go/ {
          proxy_pass http://127.0.0.1:5000/;
       }
   }
   ```

You can now access it by http://yourip/go

## Add a free SSL Certificate to your site:

1. https://certbot.eff.org/#debianjessie-nginx
2. For webroot configuration, simplest for this use, do the following:
   - Edit your `/etc/nginx/conf.d/pokemongo-map.conf`
   - Add the following location block:
   ```
   location /.well-known/acme-challenge {
     default_type "text/plain";
     root /var/www/certbot;
   }
   ```
3. Create the root folder above `mkdir /var/www/certbot`
4. Set your permissions for the folder
5. Run `certbot certonly -w /var/www/certbot -d yourdomain.something.com`
6. Certificates last for 3 Months and can be renewed by running `certbot renew`

## Example Config

```
server {
    listen       80;
    server_name  PokeMaps.yourdomain.com;

    location /.well-known/acme-challenge {
        default_type "text/plain";
        root /var/www/certbot;
    }

    # Forces all other requests to HTTPS
    location / {
        return      301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name PokeMaps.yourdomain.com;

    location /go/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_redirect off;
    }
}
```

##Adding simple httpd Authentication. 

This will guide you through setting up simple HTTP Authentication using nginx and reverse proxy protocols. These instructions are written for someone using a Debian/Ubuntu VPS. Your enviroment may have slightly different requirements, however the concepts as a whole should still stand. This guide assumes you have nginx installed and running, and a `conf.d/*.conf` file created, such as `/etc/nginx/conf.d/pokemongo-map.conf`, as the example above provides, and that you're running your service on port 5000, and want it to be accessable at http://your_ip/go/, although it supports other ports and locations.  

`*` denotes a wildcard, and will be used to stand for your site's `*.conf` file, please __do not__ literally type `sudo nano /etc/nginx/conf.d/*.conf`. 

1. Create a .htpasswd file inside `/etc/nginx/`. Some suggested methods to create a .htpasswd file are below.
   - Linux users can use the apache2-tools package to create the files.  
 
      First, get the apache2-utils package

      ``` sudo apt-get install apache2-utils   ``` 
      
      Then run the htpasswd command 
      
      ```      sudo htpasswd -c /etc/nginx/.htpasswd exampleuser ``` 
      
      This will prompt you for a new password for user exampleuser. Remove the `-c` tag for additional entries to the file. Opening the file with a text exitor such as nano should show one line for each user, with an encrypted password following, in the format of user:pass. 
      
   - Manual generation of the file can be done using tools such as: http://www.htaccesstools.com/htpasswd-generator/. After manually generating the file, please place it in `/etc/nginx/`, or wherever your distro installs `nginx.conf` and the rest of your config files. 

2. Open your `*.conf` file with a text editor, with a command such as `sudo nano /etc/nginx/conf.d/pokemongo-map.conf`. Add the following two lines underneath the domain path. 

   ```
         auth_basic "Restricted";
         auth_basic_user_file /etc/nginx/.htpasswd;
   ```

   If your `*.conf` file matches the example provided above, you should have the following. 

   ```
   server {
       location /go/ {
          auth_basic "Restricted";
          auth_basic_user_file /etc/nginx/.htpasswd;
          proxy_pass http://127.0.0.1:5000/;
       }
   }
   ```
   Now, we're going to go ahead and fill out the `*.conf` file with the rest of the information to make our service work, and shore up our nginx config, by appending the following between the authentication block and proxy_pass.

   ```
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto http;
         proxy_set_header Host $http_host;
         proxy_redirect off;
   ```
   
   Here is a fully completed example `*.conf`, with working httpd authentication. Notice, this example does not use SSL / 443, although the method can be adapted to it! 
   
   ```
   upstream pokemonmap{
      server 127.0.0.1:5000 fail_timeout=0
   }
   server {
      listen 80;
      server_name [sub.domain.com] [your_ip];
      
      location /go/ {
         auth_basic "Restricted";
         auth_basic_user_file /etc/nginx/.htpasswd;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto http;
         proxy_set_header Host $http_host;
         proxy_redirect off;
         proxy_pass http://[your_ip]:5000;
         break;
      }
   }
   ```

3. Test your nginx configuration using the command `sudo nginx -t`. If this returns a positive result, restart the nginx service using `sudo service nginx restart`. 

4. Verify your configuration is working by loading http://your_ip/go/ or http://sub.your.domain/go/, or however else you have it set in your `*.conf`. Please verify it's working before proceeding to step 5, or it will be much harder to troubleshoot! 

      Troubleshooting:

      * __I can't reach my server at http://your_ip/go/!__
      
      Check http://your_ip:5000/. If you cannot see it there, your issue lies with your server, not with nginx! If you can see it there, but cannot see it at http://your_ip/go/, your issue lies with nginx. Please check your config files to make sure they are pointing at the right places, and that your `sudo nginx -t` checks out. 
      
      * __nginx -t doesn't check out.__
      
      Check the error messages for which line is creating the error, and work your way backwards from there. Many times it's just a missed `;` or `}`. 

5. Use ufw or another service to block direct access to port 5000. The authentication wouldn't be very good if you could bypass it by appending a :5000 to the url, so we're going to have to shut down port 5000 access remotely, only allowing internal services, IE nginx, to access it. We're going to assume, for the purposes of this tutorial, that you are going with ufw, but many firewall options exist! First step is to verify ufw is installed. 

   ```sudo apt-get install ufw```
   
   Once you know it's installed, go ahead and add the following ports, along with any others you may need. UFW may have many turned on by default, but it's worth checking them. 80 = http, 443 = ssl/https, 22 = ssh (you need to get into your server, after all) and we're going to assume you want to deny all other incoming traffic, and approve all outgoing traffic by default. We're also going to go ahead and proactively block all traffic on port 5000, making your map only accessable via nginx, at the destination provided in your `*.conf`.  
   
   ```
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw default allow outgoing
   sudo ufw default deny incoming
   sudo ufw deny 5000
   ```
   
   If you want any additional information on how to configure more ufw services, please refer to the following guide: https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server 
   
   Finally, we're going to enable ufw using the command 
   
   ``` sudo ufw enable ```
   
From there, we're going to want to check and see that you can get to your server, albeit through authentication, at http://your_ip/go/, and that you cannot get to your server at http://your_ip/go:5000/. If that works, you're all set up! 
