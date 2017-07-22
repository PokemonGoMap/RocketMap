# Contributing to RocketMap

## Table Of Contents

[I just have a question/need help](#i-just-have-a-questionneed-help)

[How do I get started?](#how-do-i-get-started)
* [Python Packages](#python-packages)
* [NodeJS Packages](#nodejs-packages)

[Reporting code issues](#reporting-code-issues)
* [Before you report](#before-you-report)
* [Submitting a helpful bug report](#submitting-a-helpful-bug-report)

[Contributing Code](#contributing-code)
* [Basic Knowledge](#basic-knowledge)
* [Styleguides](#styleguides)
* [Submitting a helpful pull request](#submitting-a-helpful-pull-request)
* [Collaborating with other contributors](#collaborating-with-other-contributors)

## I just have a question/need help.

Please do not open a GitHub issue for support or questions. They are best answered via [Discord](https://discord.gg/RocketMap). GitHub issues are for RocketMap code issues *only*.

## How do I get started?

RocketMap has two main dependencies to get started:

1. RocketMap is a Python2 project, therefor, you need [Python 2](https://www.python.org/downloads/)!
2. RocketMap also requires [NodeJS](https://nodejs.org/en/download/) in order to minify frontend assets.

### Python Packages

All the required packages to operate RocketMap are found in requirements.txt in the project root, and can easily be installed by executing `pip install --upgrade -r requirements.txt`.

### NodeJS Packages

NodeJS packages are found in package.json in the project root, and can be easily installed by simply executing `npm install`.

## Reporting code issues

### Before you report

1. **Make sure you are on the latest version!** When in doubt, `git pull`.
2. Ensure it is an actual issue with the project itself. Confirm that you do not have faulty config, and that you have properly installed all the required dependencies. ***READ THE ERROR OUTPUT YOU ARE GIVEN!*** It may have the solution readily printed for you!
3. Reproduce. Confirm the circumstances you are able to reproduce the bug. If specific configuration is required, include in your report the configuration required. Find a friend, spin up a virtual machine, or use a different computer and test the issue there. If you do not have the issue on the new machine, it may be indicative that it is something with your configuration.
4. *USE GITHUB SEARCH.* Search open issues and look for any open issues that already address the problem. Duplicate issues will be closed.

### Submitting a helpful bug report

When you begin the process of opening an issue, you will be given a template in the text box that should help guide you through the process.

* **Expected Behavior** - What did you expect to happen? Should the map have handled an exception, or have done something different?
* **Current Behavior** - What actually happened? Did the map crash? Did a function behave in a way it was not intended?
* **Possible Solution** - If you know how this issue is caused, and have a possible solution, please include it. Be as detailed as you can.
* **Steps to reproduce** - Here is where your “Reproduce” stage comes in. Provide specific configuration that you ran with. Frontend issue? Provide instructions on what to click or do on the frontend to cause the issue.
* **Context** - Why is this an issue?
* **Your environment** - Operating system, `python --version`, `pip --version`, etc.

If you are asked for more details, *please provide details*. Any issues not following the above layout, or that is not detailed enough to determine the issue, may be subject to closure.

## Contributing code

### Basic Knowledge

To contribute code to RocketMap, it is heavily advised that you are knowledgeable in Git. At a minimum, you should know how to commit, push, pull and do basic rebasing.

### Styleguides

RocketMap follows and adheres to the [pep8 standards](https://www.python.org/dev/peps/pep-0008/) for Python code, and has established rules for JavaScript in the .eslintrc.json file in the project root. Checks of these standards are run when pull requests are opened, however, you can save some time by running these checks on your local machine. 

To check if your Python code conforms to PEP8, you can use the flake8 package (pip install flake8). After making changes, open a terminal in the project root and run `flake8 --statistics --show-source --disable-noqa`.

To check if your Python code conforms to the eslint rules, you can run `npm run lint`.

### Submitting a helpful pull request

* **Description** - Describe in detail the changes you made. If you add or subtract specific libraries, frameworks, etc, please list the specific frameworks. Any movements between files, eg, moving code from runserver.py to utils.py, should be noted as such.
* **Motivation and Context** - What’s the need for this change? What issue does it solve? If there’s an open issue, please write this exact phrase: “Fixes #prnumber” This will automatically close the issue when the pull request is merged.
* **How has this been tested?** - Please include the details of your test. Scan area, configuration, operating system, python version, any other relevant details.
* **Screenshots** - If you have made frontend changes, screenshots are highly advised to give context.
* **Types of changes & Checklist** - Please put a x in boxes that apply. Make sure it looks like [x], instead of [x ] or [ x], so you get a nice checkbox.

### Collaborating with other contributors

When you have an open pull request and wish to collaborate with other contributors, you may request access to the #pr channel in the RocketMap [Discord](https://discord.gg/rocketmap). To request access, you may send a message to Seb or Thunderfox. Please provide a link to your open pull request with your message.
