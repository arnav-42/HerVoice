# HerVoice

## Windows Instructions
  
After cloning repo:  
1) 'python -m venv venv'  
2) 'Set-ExecutionPolicy Unrestricted -Scope Process -Force'  
3) '.\venv\Scripts\Activate'  
4) 'pip install -r requirements.txt'  
  
Running instructions:  
1) delete instance folder and bills.db (if it exists)  
2) 'python database_setup.py'  
3) 'python app.py'  
Webapp will be available at: http://127.0.0.1:5000/index