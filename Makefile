
.PHONY: clean

ifeq ("$(VIRTUAL_ENV)", "")
  ENV=. venv/bin/activate;
endif

venv/bin/django-admin: venv/bin/activate requirements.txt
	$(ENV) pip install --upgrade --force pip
	$(ENV) pip install --force -Ur requirements.txt
	touch venv/bin/django-admin

venv/bin/activate: requirements.txt
	 test -d venv || virtualenv -p python3 venv
	 venv/bin/pip install -U pip
	 touch venv/bin/activate

clean:
	rm -rf venv
