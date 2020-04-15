all:
	echo "#!/bin/sh\npython3.8 exercise.py\n" > exercise
	chmod 755 exercise

clean:
	rm -f exercise