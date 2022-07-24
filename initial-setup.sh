envname=notion-page-creator-book-notes-highlight-venv
if [ ! -d "$envname" ]; then
  python3 -m venv $envname
fi
source ./$envname/bin/activate
pip3 install -r ./requirements.txt