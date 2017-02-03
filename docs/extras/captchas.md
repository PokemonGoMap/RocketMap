# Handling Captchas
In the following examples we will be using `http://localhost:5000` as URL where RocketMap can be accessed (i.e. front-end instance).

## Automatic Mode (2captcha)
RocketMap can request tokens for captcha solving from an external service, allowing captchas to be solved "on-the-fly" - meaning that once an account encounters a captcha it immediately starts the uncaptcha process.

If you want to enable this behavior you need to specify:
- Enable captcha solving: `-cs` or `--captcha-solving`

- 2captcha API key: `-ck` or `--captcha-key`

## Enabling Manual/Hybrid Captcha Solving:
You can setup RocketMap to enable manual captcha solving. This feature uses common web browsers to let users rescue captcha'd accounts.
We use a JavaScript [bookmarklet](https://en.wikipedia.org/wiki/Bookmarklet) that triggers a captcha which allows the user to solve it in its web browser.
The result is then forwarded to the RocketMap instance running at the URL specified by `-mcd`.

Please remember that if you want your map to be accessed from the exterior you need to setup `--host` and `--manual-captcha-domain` to something like `http://<your-ip>:<port>` or `http://<your-domain>:<port>`.

To enable manual captcha solving you need to add the following parameters:

`python runserver.py -cs -mcd http://localhost:5000`

Or using config.ini:

    captcha-solving: True
    manual-captcha-domain: http://localhost:5000

### Bookmarklet
The required bookmarklet to solve captchas using only the web browser can be found at:

`http://localhost:5000/bookmarklet`

![bookmarklet page](../_static/img/captchas-bookmarklet-page.png)

After saving "Solve Recaptcha" link in your bookmarks (preferably in bookmarks menu)
you can start solving captchas!

Click the bookmarklet once to be redirected to `http://pgorelease.nianticlabs.com/`
which is normal to display a 404 error message.

![bookmarklet page](../_static/img/captchas-1st-click.png)

The "magic" happens when you **click the bookmarklet a second time** (while remaining in the same URL).

![bookmarklet page](../_static/img/captchas-page.png)

If `-mcd` / `--manual-captcha-domain` is correct, a similar page to the one above will appear and some statistics should be visible.

 - **Working accounts**: shows the total of available accounts (includes captcha'd accounts)

 - **Remaining captchas**: displays the number of accounts waiting for captcha token.

 This number can take some time to refresh since the uncaptcha process can take up to a minute to complete.

 - **Failed accounts**: total count of disabled accounts (can include captcha'd accounts if `--captcha-solving` is not enabled)

## Hybrid Mode
RocketMap also allows an hybrid mode for captcha solving.

This works by first putting the account aside and waiting for manual captcha solve. After `x` seconds you can force the captcha to be solved by the automatic method (2captcha).

To enable this behavior you need to specify:
- Enable captcha solving: `-cs` or `--captcha-solving`

- 2captcha API key: `-ck` or `--captcha-key`

- Manual captcha timeout: `-mct 1800` or `-manual-captcha-timeout 1800`

The number `1800` indicates how many seconds you want the accounts to wait for manual tokens before resorting to the automatic method (a.k.a. 2captcha).

`-mct` is by default set to `0` which disables this mode and if you have set `-ck` it will only use the automatic mode.

### Sample configuration: Hybrid mode

    captcha-solving: True
    captcha-key: <2Captcha API Key>
    manual-captcha-domain: http://<mydomain.com>:<port>
    manual-captcha-timeout: 1800
