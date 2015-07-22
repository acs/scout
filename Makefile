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
	$(info - events_limit:		Generate events JSON file with a limit in number of events)
	$(info - deploy:		Deploy JSON file to be shown in the web)
	$(info )
	@echo ""

DBNAME=scout
DBUSER=root
BACKENDS=github stackoverflow mail reddit gmane meetup
# Used the meetup cache data to avoid having a real meetup api key by default
MEETUP_CACHE=data/meetup_groups_cache.json
# Used the github cache data to avoid having a real Big Query auth by default
GITHUB_CACHE=data/github_cache_month.201507.json

ifndef $(EVENTS_LIMIT)
	EVENTS_LIMIT=10
endif

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

# github: $(GITHUB_CSV)
github: $(GITHUB_CACHE)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

# stackoverflow: $(STACKOVERFLOW_CSV)
stackoverflow:
#	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

mail: $(MAIL_CSV)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

reddit:
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

gmane:
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

meetup: $(MEETUP_CACHE)
	@echo "meetup_api_key file must include a Meetup API KEY to refresh data\n"
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ --key `cat meetup_api_key`

.PHONY: events
events: cleandb $(BACKENDS)
	$(SCOUT) --events -u root -d scout

events_limit: events
	$(SCOUT) --events --limit $(EVENTS_LIMIT) -u root -d scout

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

all: jshint pep8 cleandb $(BACKENDS) events events_limit deploy

cleandb:
	echo "drop database if exists $(DBNAME)" | mysql -u $(DBUSER)

.PHONY: clean
clean: cleandb
	rm -rf $(KEYWORD).json $(KEYWORD)-*.json scout.json data/*.csv data/*.json data/*_cache.json
