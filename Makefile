.PHONY: help
help:
	$(info )
	$(info This makefile will help you build scout tool and generate events data)
	$(info )
	$(info Available options:)
	$(info )
	$(info - all:			Load events from all data sources and generate events)
	$(info - github:		Load data for github)
	$(info - stackoverflow: 	Load data for stackoverflow)
	$(info - mail:			Load data for mail archives)
	$(info - events:		Generate events JSON file)
	$(info )
	@echo ""

SCOUT=./scout.py
DBNAME=scout
DBUSER=root
BACKENDS=github stackoverflow mail

%.csv: %.csv.gz
	gunzip -c $^  > $@

github: GithubReposCentOS-P1.csv
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

stackoverflow: StackOverFlowCentOS-P1.csv
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

mail: MailmanOpenStackCentOS-P1.csv
	$(SCOUT) -d $(DBNAME) -u $(DBUSER) -b $@ -f $^

.PHONY: events
events:
	$(SCOUT) -j events.json  -u root -d scout

all: $(BACKENDS) events

cleandb:
	echo "drop database $(DBNAME)" | mysql -u $(DBUSER)

.PHONY: clean
clean:
	rm -rf *.csv events.json
