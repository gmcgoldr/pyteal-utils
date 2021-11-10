#!/bin/bash
shopt -s expand_aliases
source ~/.bashrc

python fs_test.py > contract.teal

sb copyTo contract.teal
sb copyTo clear.teal

app_id=`sb goal app create \
    --creator XHE7CG7TPQFIXNYG2INJDBMPOIZV7VZUJPSLHPA2FN5F6ZNCX4SBSK34KI \
    --global-byteslices 0 --global-ints 0 \
    --local-byteslices 16 --local-ints 0 \
    --approval-prog contract.teal \
    --clear-prog clear.teal | grep 'Created app' |awk '{print $6}' | tr -d '\r'`

echo "AppID: $app_id"

sb goal app optin --app-id $app_id --from XHE7CG7TPQFIXNYG2INJDBMPOIZV7VZUJPSLHPA2FN5F6ZNCX4SBSK34KI

txid=`sb goal app call --app-id $app_id --from XHE7CG7TPQFIXNYG2INJDBMPOIZV7VZUJPSLHPA2FN5F6ZNCX4SBSK34KI | grep Transaction | awk '{print $2}'`


echo "Transaction id: $txid"

curl -s localhost:4001/v2/transactions/pending/$txid \
    -H "X-Algo-API-Token: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
    | jq '.logs[]'  | xargs | base64 -d

echo ""