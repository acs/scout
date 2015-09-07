export PATH=$PATH:/usr/local/bin
SCOUT_HOME=/home/bitergia/scout
LOGS=$SCOUT_HOME/logs
mkdir -p $LOGS
cd $SCOUT_HOME
make clean newevents deploy 2>&1 | cat > $LOGS/scout.log-`date +%s`
