•	Open command prompt 
•	change directory to the project folder-

      cd <folder_path>
 
•	Set up a virtual environment with the following command-
      
      python -m venv artifex

•	note- "artifex" is the name of the environment, so you can use whatever name you want.
 
•	Activate the virtual environment with the following-
      
      artifex\Scripts\activate.bat
 
•	Install the libraries with the following-

      pip install -r requirements.txt
 
•	to run the app locally use-

      flask run
 
•	go to http://localhost:5000/

•	If you add more libraries/modules use the following command to rewrite the requirements.txt (but please make sure you are doing it in virtual environment)

      pip freeze > requirements.txt

•	To deactivate virtual environment use-

      deactivate

•	To remove virtual environment before pushing it to github use- (“artifex” is just a name)

      rmdir artifex /s
