# RocketMap tutorial completion for accounts (up to Level 2)

This is documentation to complete the Pokemon GO Tutorial for a number of
accounts while simultaneously become level 2 when completing it next to a
Pokestop due to the "First Pokestop of the Day" bonus.

## Instruction
* We assume you are running a basic RocketMap installation. It is best to run
the tutorial with hashing service on newest API to not get your fresh accounts
becoming flagged.
* Create a ``config/config.tutorial.ini`` file by copying and renaming the
``config/config.ini.example`` and make some changes to it afterwards which let
the tutorial run smooth and fast enough to go through a batch of accounts.
* Config changes are:
	* Location next to at least one known Pokestop, a cluster is preferred.
	* Set step distance to ``st: 1``.
	* Set scan delay ``sd`` to a value which provides enough calls during the
	following set search time (a good value is around ``sd: 15`` or lower).
	* Set the account search interval to around ``asi: 120``.
	* Set the account rest interval as high as possible that all accounts get
	cycled and none returns, a safe value is ``ari: 36000``.
	* Set login delay at least to ``login_delay: 1`` to avoid throttling.
* Put your accounts, which need to run the tutorial and need to level up, into
your ``accounts.csv`` file.
* Set up an instance with the following flags
	* ``--complete-tutorial`` or just ``-tut``
	* ``--config config/config.tutorial.ini`` or just
	``-cf config/config.tutorial.ini`` to use a designated config file.
	* ``--accountcsv PATH/accounts.csv`` or just ``-ac PATH/accounts.csv``
	* ``-w WORKER`` to set your simultaneously working accounts to a reasonable
	number, considering hash key limit and throttling. You can at least have 10
	accounts running at the same time without any problems.
* If you are not using fresh accounts and you are not running hash service,
prepare for occuring captchas. Set up your RocketMap accordingly.
* Enable ``-v`` in process if you want to see it working in log.
* Let it run and your accounts will complete the tutorial and rise to level 2.
