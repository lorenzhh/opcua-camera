add-apt-repository ppa:deadsnakes/ppa -y

apt update
apt upgrade


sudo apt install -y python3.13 
sudo apt install -y python3.13-venv 
sudo apt install -y libgl1-mesa-glx
sudo apt install -y python3.13-tk

sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.13 get-pip.py


sudo python3.13 -m venv camera-env
source camera-env/bin/activate
pip install Pillow opcua opencv-python cryptography



