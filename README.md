•	Open command prompt 
•	change directory to the project folder. 
o	cd <folder_path>
 
•	Set up a virtual environment with the following command-
o	python -m venv artifex
•	"artifex" is the name of the environment, so you can use whatever name you want.
 
•	Activate the virtual environment with the following-
o	artifex\Scripts\activate.bat
 
•	Install the libraries with the following-
o	pip install -r requirements.txt
 
•	to run the app locally use-
o	flask run
 
•	go to http://localhost:5000/

If you add more libraries/modules use the following command to rewrite the requirements.txt (but please make sure you are doing it in virtual environment)
o	pip freeze > requirements.txt
To deactivate virtual environment use-
o	deactivate
To remove virtual environment before pushing it to github use- (“artifex” is just a name)
o	rmdir artifex /s
