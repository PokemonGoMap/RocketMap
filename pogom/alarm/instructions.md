
# Instructions for setting up notification using push bullet or slack. 

## Getting started

1. Open a terminal at the POGO directory and run $pip install --upgrade -r requirements.txt. If you are on Mac OS X and get an error about six being already installed, run this instead: $pip install --upgrade --ignore-installed six -r requirements.txt


## Setting up notification with Push Bullet: 

1. Sign up for a free push bullet account at https://www.pushbullet.com/. Next, go to Settings -> Account -> Create Access Token, and copy the provided key. 

2. Open alarms.json and on line 4, make sure "active" is set to "True". Paste your pushbullet key on line 6, where it says "your_api_key".

3. Beginning on line 29, are the pokemons you can receive notifications for. For any that you want to get notification for, just set "False" to "True".

4. Download the push bullet app on your phone and login using the username you created in #1. 


## Setting up notification with Slack: 

1. Sign up for a free slack account at https://slack.com/ and register a new team. Next, go to https://api.slack.com/web and click on "Generate test tokens". On the next page, click on "Create Token" next to your team name and copy the token. 

2. Open alarms.json and on line 9, make sure "active" is set to "True". Paste your slack token on line 11, where it says "your_api_key".

3. Beginning on line 29, are the pokemons you can receive notifications for. For any that you want to get notification for, just set "False" to "True".


4. Download the slack app and login to the team you created in #1. 

## Starting the map scanner with notification
Substitute your crendentials into the line below and run the map scanner.  You will immediately get a notification that the pokealarm has started and you will receive alerts for any pokemon in your list. 
$python runserver.py -a "$AUTH_SERVICE" -u "$USERNAME" -p "$PASSWORD" -l "$LOCATION" -st $STEP_COUNT -H 0.0.0.0 -P $PORT -k $GMAPS_KEY $EXTRA_ARGS 


