.PHONY: help
help:
	$(info )
	$(info This makefile will help you build docker images for Bitergia Scout platform)
	$(info components based on the bitergia baseimages.)
	$(info )
	$(info Available options:)
	$(info )
	$(info - all:			Build all available images)
	$(info - scout:			Build scout core image)
	$(info )
	@echo ""

.PHONY: scout
scout: $@
	docker build -t bitergia/$@ $@/

.PHONY: all
all: scout

.PHONY: clean clean_scout
clean: clean_scout

clean_idm:
	-@docker rmi bitergia/scout
