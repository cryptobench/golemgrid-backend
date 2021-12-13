#! /bin/bash
# Start yagna service in the background and log it
mkdir -p /golem/work
touch /golem/work/yagna.log
echo "Starting Yagna"
RUST_LOG=error MARKET_DB_CLEANUP_INTERVAL=10min /root/.local/bin/yagna service run > /dev/null 2>&1 &
sleep 5
key=$(/root/.local/bin/yagna app-key create requester)
/root/.local/bin/yagna payment fund --driver zksync
/root/.local/bin/yagna payment init --sender --driver zksync
echo "Installing custom yapapi"
pip3 install git+https://github.com/golemfactory/yapapi.git
echo "Finished installing yapapi"