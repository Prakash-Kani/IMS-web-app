# #!/bin/bash
# apt-get update
# apt-get install -y libgl1-mesa-glx
# gunicorn --bind=0.0.0.0 app:app

#!/bin/bash
apt-get update
apt-get install -y libgl1-mesa-glx
python3 -m venv /home/site/wwwroot/antenv
source /home/site/wwwroot/antenv/bin/activate
pip install -r /home/site/wwwroot/requirements.txt
gunicorn --bind=0.0.0.0 app:app