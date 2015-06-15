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
	$(info - reedit:		Load data from reedit)
	$(info - events:		Generate events JSON file)
	$(info - deploy:		Deploy JSON file to be shown in the web)
	$(info )
	@echo ""

SCOUT=./scout.py
DBNAME=scout
DBUSER=root
BACKENDS=github stackoverflow mail reedit
DEPLOY=../VizGrimoireJS/browser

%.csv: %.csv.gz
	gunzip -c $^  > $@

%.json: %.json.gz
	gunzip -c $^  > $@

github: data/GithubReposCentOS-P1.csv
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

stackoverflow: data/StackOverFlowCentOS-P1.csv
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

mail: data/MailmanOpenStackCentOS-P1.csv
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

reedit: data/reedit_cache.json.gz
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@

.PHONY: events
events: cleandb github stackoverflow mail
	$(SCOUT) -j scout.json  -u root -d scout

# scout.json: events

deploy: scout.json
	cp $^ $(DEPLOY)/data/json
	cp -a html/browser/* $(DEPLOY)
	cp -a html/browser/scout.html $(DEPLOY)/index.html

pep8:
	pep8 --exclude=VizGrimoireJS .

all: pep8 cleandb $(BACKENDS) events deploy

cleandb:
	echo "drop database if exists $(DBNAME)" | mysql -u $(DBUSER)

.PHONY: clean
clean: cleandb
	rm -rf data/*.csv data/*.json scout.json
