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
BACKENDS=github stackoverflow reddit gmane meetup
APP_JSON_DIR=html/app/data/json/

ifndef $(KEYWORDS)
	KEYWORDS=centos,CentOS
endif
ifndef $(CATEGORY)
	CATEGORY=CentOS
endif

# In order to generate fresh events just comments the CACHE lines and configure
# access grants for meetup and github
# Used the meetup cache data to avoid having a real meetup api key by default
MEETUP_CACHE=data/meetup_groups_cache-$(KEYWORDS).json
# Used the github cache data to avoid having a real Big Query auth by default
GITHUB_CACHE=data/github_cache-$(KEYWORDS).json
GMANE_CACHE=data/gmane_cache-$(KEYWORDS).csv
REDDIT_CACHE=data/reddit_cache-$(KEYWORDS).json
STACKOVERFLOW_CACHE=data/stackoverflow_cache-$(KEYWORDS).json
ALL_CACHE=$(MEETUP_CACHE) $(GITHUB_CACHE) $(GMANE_CACHE) $(REDDIT_CACHE) $(STACKOVERFLOW_CACHE)

ifndef $(EVENTS_LIMIT)
	EVENTS_LIMIT=10
endif

SCOUT=PYTHONPATH=. bin/scout --keywords $(KEYWORDS) --category $(CATEGORY) --limit $(EVENTS_LIMIT)
SCOUT_CONF=PYTHONPATH=. bin/scout --conf conf/scout.conf

#
# PYTHON
#

%.csv: %.csv.gz
	gunzip -c $^  > $@

%.json: %.json.gz
	gunzip -c $^  > $@

pep8:
	pep8 --exclude=VizGrimoireJS,./html . bin/scout

github: $(GITHUB_CACHE)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

stackoverflow: $(STACKOVERFLOW_CACHE)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

reddit: $(REDDIT_CACHE)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

gmane: $(GMANE_CACHE)
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

meetup: $(MEETUP_CACHE)
	@echo "conf/meetup_api_key file must include a Meetup API KEY to refresh data\n"
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ --key `cat conf/meetup_api_key`

# By default work with cache files for default keyword
newevents: $(ALL_CACHE)
	$(SCOUT_CONF)

#
# JAVASCRIPT
#

APP=html/browserng/app
APP_JS= $(APP)/app.js $(APP)/controllers.js $(APP)/scout $(APP)/lib/events.js

jshint:
	jshint html/app/lib/events.js

DEPLOY=/home/bitergia

deploy: $(APP_JSON_DIR)/scout-categories.json
	cat $^ | python -m json.tool > /dev/null
	cd html && npm install && cd ..
	rm -rf $(DEPLOY)/app
	cp -a html/app $(DEPLOY)
	rm -rf $(DEPLOY)/app/bower_components
	cp -a html/bower_components $(DEPLOY)/app
	# rm -rf $(DEPLOY)/app/data/json
	# mkdir -p $(DEPLOY)/app/data/json
	# cp $^ $(DEPLOY)/app/data/json
	# cp *.json $(DEPLOY)/app/data/json
	cp -a logs $(DEPLOY)/app

all: jshint pep8 newevents deploy

.PHONY: clean
clean: 
	rm -rf *-*.json data/*.csv data/*.json data/*_cache.json

tests: deploy
	protractor html/e2e-tests/protractor.conf.js
