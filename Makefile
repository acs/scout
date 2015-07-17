.PHONY: help
help:
	$(info )
	$(info This makefile will help you build scout tool and generate events data)
	$(info )
	$(info Available options:)
	$(info )
	$(info - all:			Load events from all data sources and generate events)
	$(info - github:		Load data from github)
	$(info - stackoverflow: 	Load data from stackoverflow)
	$(info - mail:			Load data from mail archives)
	$(info - reddit:		Load data from reddit)
	$(info - gmane:			Load data from gmane)
	$(info - meetup:		Load data from meetup)
	$(info - events:		Generate events JSON file)
	$(info - deploy:		Deploy JSON file to be shown in the web)
	$(info )
	@echo ""

DBNAME=scout
DBUSER=root
BACKENDS=github stackoverflow mail reddit gmane meetup


ifndef $(KEYWORD)
	KEYWORD=centos
endif

# TO BE REMOVED 
ifeq ($(KEYWORD),centos)
	GITHUB_CSV=data/GithubReposCentOS-P1.csv
	STACKOVERFLOW_CSV=data/StackOverFlowCentOS-P1.csv
	MAIL_CSV=data/MailmanOpenStackCentOS-P1.csv
endif
ifeq ($(KEYWORD),coreclr)
	GITHUB_CSV=data/GithubReposCoreCLR.csv
	STACKOVERFLOW_CSV=data/StackOverFlowCoreCLR.csv
	MAIL_CSV=data/MailmanOpenStackCoreCLR.csv
endif
# END TO BE REMOVED 

SCOUT=PYTHONPATH=. bin/scout --keyword $(KEYWORD)

#
# PYTHON
#

%.csv: %.csv.gz
	gunzip -c $^  > $@

%.json: %.json.gz
	gunzip -c $^  > $@

pep8:
	pep8 --exclude=VizGrimoireJS,./html .

github: $(GITHUB_CSV)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

stackoverflow: $(STACKOVERFLOW_CSV)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

mail: $(MAIL_CSV)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

reddit:
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

gmane:
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

meetup:
	@echo "meetup_api_key file must include a Meetup API KEY\n" 
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ --key `cat meetup_api_key`

.PHONY: events
events: cleandb github stackoverflow mail reddit gmane meetup
	$(SCOUT) --events -u root -d scout

#
# JAVASCRIPT
#

APP=html/browserng/app
APP_JS= $(APP)/app.js $(APP)/controllers.js $(APP)/scout $(APP)/lib/events.js

jshint:
	jshint html/app/lib/events.js

DEPLOY=/home/bitergia

# scout.json: events
deploy: scout.json
	cat $^ | python -m json.tool > /dev/null
	cd html && npm install && cd ..
	rm -rf $(DEPLOY)/app
	cp -a html/app $(DEPLOY)
	rm -rf $(DEPLOY)/app/bower_components
	cp -a html/bower_components $(DEPLOY)/app
	mkdir -p $(DEPLOY)/app/data/json
	cp $^ $(DEPLOY)/app/data/json
	cp $(KEYWORD)*.json $(DEPLOY)/app/data/json

all: jshint pep8 cleandb $(BACKENDS) events deploy

cleandb:
	echo "drop database if exists $(DBNAME)" | mysql -u $(DBUSER)

.PHONY: clean
clean: cleandb
	rm -rf $(KEYWORD).json $(KEYWORD)-*.json scout.json data/*.csv data/*.json data/*_cache.json
