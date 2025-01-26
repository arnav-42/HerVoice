# HerVoice
## Overview
[![HerVoice_logo](https://github.com/arnav-42/HerVoice/blob/main/image.jpg?raw=true)](https://github.com/arnav-42/HerVoice/blob/main/static/images/Screenshot_2025-01-26_154744.png?raw=true)
Keep women informed about pending political actions that could affect them. Stores Congress bills and reports in database, classifies topics with LLM technology, and then pushes alerts to users who have opted to track said topics.
### Tech Stack
- Backend:
  - Flask
  - SQLite
  - SQLAlchemy
  - Flask-Mail
  - Flask Extensions  
- Frontend:
  - HTML/CSS (with Skeleton)  
  - JavaScript  
- Technologies:
  - Congress API to fetch bill data
  - Llama-3.3-70b for bill classification
  - Grok API for fast AI inference  
### Media
- View our Figma [here](https://www.figma.com/design/f2T2xYPbOuf5uBQeAcvpPN/Untitled?node-id=0-1&t=rvvZaNZIvsKVM3L3-1).  
- Our presentation is [here](https://www.canva.com/design/DAGdQQKBXrU/J5fvwameXF6RvzpHV0lJkA/edit).
## Windows Instructions
After cloning repo:  
1) `python -m venv venv`  
2) `Set-ExecutionPolicy Unrestricted -Scope Process -Force` (temporary, session only)  
3) `.\venv\Scripts\Activate`   
4) `pip install -r requirements.txt`  
  
Running instructions:  
1) delete instance folder and bills.db (if it exists)  
2) `python database_setup.py`  
3) `python app.py`  
Webapp will be available at: http://127.0.0.1:5000/index

**You will need your own API keys!** Set environmental variables `CONGRESS_API_KEY` and `GROQ_API_KEY` with said api keys.  
Set the following for email alerts:
```
MAIL_SERVER  
MAIL_PORT  
MAIL_USERNAME
MAIL_PASSWORD # enable 2FA and use app password if using Gmail  
MAIL_USE_TLS  
MAIL_USE_SSL
```
