

cat start.sh
sed -i '$ d' start.sh

# git clone https://github.com/resource-watch/nrt-scripts.git

# echo "pulling repository"
# cd nrt-scripts
# git pull origin master
# cd ..
# echo "Creating cronfile"
# ls -a
# rm -f crontab
# find . -name "*.cron"|while read fname; do
#   rm -rf nrt-scripts/$(basename $(dirname $fname))/.env
#   cp .env nrt-scripts/$(basename $(dirname $fname))
#   echo "$(cat $fname) root cd nrt-scripts/$(basename $(dirname $fname)) && LOG=udp://lo
# gs6.papertrailapp.com:37123 ./start.sh  " >> crontab
# done
# rm -f /etc/cron.d/crontab
# mv crontab /etc/cron.d
# echo "Finished"
#
# echo "Examine:"
# cat /etc/cron.d/crontab
