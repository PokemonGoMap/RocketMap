SET latitude=51.5561097
SET longitude=7.9132573
SET stepsize=6
SET leaps=2

@echo Generating Beehive for Lat:%latitude%, Lon:%longitude%, Steps:%stepsize%, Leaps:%leaps%

pause
python location_generator.py -lat %latitude% -lon %longitude% -st %stepsize% -lp %leaps%
pause