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

•	Notes for running the latest version on Windows
      •	Make sure you are using python version higher than 3.5
      •	Make sure you have 64bit Python to check this make use of (the ouput should print fffff True)-

      import sys;print("%x" % sys.maxsize, sys.maxsize > 2**32)

      •	If you are getting file path errors make sure you follow the following tutorial-
      https://www.howtogeek.com/266621/how-to-make-windows-10-accept-file-paths-over-260-characters/
      •	In the requirements.txt delete the following before installing the libraries from requirements.txt - tensor2tensor==1.15.7
      •	After installing the libraries use the following command to install tensor2tensor

      pip install --no-deps tensor2tensor
