SET latitude=51.5100694
SET longitude=7.4739465
SET stepsize=5
SET leaps=3

@echo Generating Beehive for Lat:%latitude%, Lon:%longitude%, Steps:%stepsize%, Leaps:%leaps%

pause
python location_generator.py -lat %latitude% -lon %longitude% -st %stepsize% -lp %leaps%
pause