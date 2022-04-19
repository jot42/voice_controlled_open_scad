import argparse
import subprocess
import os
import sys
import requests
from pathlib import Path

def download_server_files(file):

    if file == 1:
        pbmm_url = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm"
        pbmm_file = requests.get(pbmm_url, stream=True)
        print("Downloading deepspeech-server/deepspeech-0.9.3-models.pbmm")
        with open("deepspeech-server/deepspeech-0.9.3-models.pbmm","wb") as pbmm:
            for chunk in pbmm_file.iter_content(chunk_size=1024):
                if chunk:
                    pbmm.write(chunk)

    if file == 2:
        scorer_url = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer"
        scorer_file = requests.get(scorer_url, stream=True)
        print("Downloading deepspeech-server/deepspeech-0.9.3-models.scorer")
        with open("deepspeech-server/deepspeech-0.9.3-models.scorer","wb") as scorer:
            for chunk in scorer_file.iter_content(chunk_size=1024):
                if chunk:
                    scorer.write(chunk)

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose'  , help='Provide additional logging while installing components', required=False, action='store_true')
args = parser.parse_args()


if args.verbose:
    subprocess.Popen('sudo apt-get install -y curl', shell=True, stdin=None, stdout=None, stderr=None, executable="/bin/bash")
    subprocess.Popen('sudo apt-get install -y python3-pip', shell=True, stdin=None, stdout=None, stderr=None, executable="/bin/bash")
    subprocess.Popen('sudo pip3 install deepspeech', shell=True, stdin=None, stdout=None, stderr=None, executable="/bin/bash")
    subprocess.Popen('sudo pip3 install deepspeech-server', shell=True, stdin=None, stdout=None, stderr=None, executable="/bin/bash")

else:
    #Install system prerequisites
    print("Installing curl")
    curl = subprocess.Popen('sudo apt-get install -y curl', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=None, executable="/bin/bash")
    curl.wait()

    print("Installing python3-pip")
    pip = subprocess.Popen('sudo apt-get install -y python3-pip', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=None, executable="/bin/bash")
    pip.wait()

    #Install python prerequisites
    print("Installing deepspeech")
    ds = subprocess.Popen('sudo pip3 install deepspeech', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=None, executable="/bin/bash")
    ds.wait()

    print("Installing deepspeech-server")
    ds_s = subprocess.Popen('sudo pip3 install deepspeech-server', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=None, executable="/bin/bash")
    ds_s.wait()

    print("Installing PyAudio")
    pa = subprocess.Popen('sudo apt-get install python3-pyaudio', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=None, executable="/bin/bash")
    pa.wait()

    print("Installing Pandas")
    pa = subprocess.Popen('sudo pip3 install pandas', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=None, executable="/bin/bash")
    pa.wait()

    #Verify local deepspeech directory exists
    if os.path.isdir('deepspeech-server'):
    
        pbmm_path = Path("deepspeech-server/deepspeech-0.9.3-models.pbmm")
        scorer_path = Path("deepspeech-server/deepspeech-0.9.3-models.scorer")

        print("Found deepspeech-server/")

        if (pbmm_path).is_file():
            print("Found", pbmm_path)
        else:
            download_server_files(1)

        if scorer_path.is_file():
            print("Found", scorer_path)
        else:
            download_server_files(2)

    #Triggers if no deepspeech files are found 
    else:
        print("Creating server directory")
        os.mkdir("deepspeech-server")

        download_server_files(1)
        download_server_files(2)

    

        
    print("Done")
    quit(0)
