all:
	echo "#!/bin/sh\npython3 exercise.py\n" > exercise
	chmod 755 exercise

clean:
	rm -f exercise