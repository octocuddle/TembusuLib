# copy and execute the command directly
set-credentials-dev:
	. ./scripts/set_credential_dev.sh

create-virtual-env:
	virtualenv -p `which python3` .venv

# copy and execute the command directly
activate-virtual-env:
	. ./.venv/bin/activate

install-requirements:
	pip3 install -r ./requirements.txt

start-server:
	python ./main.py
