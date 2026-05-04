
echo "${USE_1_PASSWORD}"

if [ "$USE_1_PASSWORD" = "1" ]; then
    echo "Setting SSH_AUTH_SOCK"
    export SSH_AUTH_SOCK=~/Library/Group\ Containers/2BUA8C4S2C.com.1password/t/agent.sock
fi