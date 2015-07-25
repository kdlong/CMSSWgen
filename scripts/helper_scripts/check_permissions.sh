#!/bin/bash
# Taken from farmoutAnalysisJobs

check_proxy() {
  hours=$1
  proxy=$2
  if ! [ -f "$proxy" ]; then
    echo
    echo "NOTE: No grid proxy found.  (Expecting to find it here: $proxy.)"
    return 1
  fi

  #Issue a warning if less than this many seconds remain:
  min_proxy_lifetime=$((3600*$hours))

  seconds_left="`voms-proxy-info --timeleft --file=$proxy 2>/dev/null`"

  if [ "$seconds_left" = "" ]; then
    echo "WARNING: cannot find time remaining for grid proxy."
    voms-proxy-info -all -path $proxy
    return 0
  fi
  if [ "$seconds_left" -lt "$min_proxy_lifetime" ]; then
    echo
    echo "NOTE: grid proxy is about to expire:"
    echo "voms-proxy-info"
    voms-proxy-info --file=$proxy
    return 1
  fi
}

MIN_PROXY_HOURS=24
proxy=${X509_USER_PROXY:-/tmp/x509up_u$UID}

if [ "$NO_SUBMIT" != 1 ] && ! check_proxy $MIN_PROXY_HOURS $proxy; then
  echo
  echo "Create a new grid proxy"
  echo "and rerun this command. Example of how to create a grid proxy:"
  echo
  echo "voms-proxy-init --voms=cms --valid=48:00"
  echo
  exit 1
fi
