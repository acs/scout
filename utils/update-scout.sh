export PATH=$PATH:/usr/local/bin
SCOUT_HOME=/home/bitergia/scout
LOGS=$SCOUT_HOME/logs

if [ "$#" -eq 1 ]
    then LOGS=$1
fi

mkdir -p $LOGS
cd $SCOUT_HOME
make newevents deploy 2>&1 | cat > $LOGS/scout.log-`date +%s`
