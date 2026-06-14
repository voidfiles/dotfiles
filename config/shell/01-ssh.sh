if [ "${IS_DARWIN:-0}" = "1" ] && [ "${USE_1_PASSWORD:-0}" = "1" ]; then
    export SSH_AUTH_SOCK=~/Library/Group\ Containers/2BUA8C4S2C.com.1password/t/agent.sock
fi
