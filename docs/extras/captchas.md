# Handling Captchas

## Enabling Manual/Hybrid Captchas:
You can setup RocketMap to enable manual captcha solving. This feature uses common web browsers to let users rescue captcha'd accounts.
We use a JavaScript bookmarlet _<link to website with good explanation>_ to trigger the captcha and allow the user to solve it in its web browser.

To enable manual captcha solving you need to add the following parameters:

Example: `python runserver.py -cs -mcd "http://localhost:5000"`
Or using config.ini:
```
captcha-solving: True
manual-captcha-domain: http://localhost:5000
```
