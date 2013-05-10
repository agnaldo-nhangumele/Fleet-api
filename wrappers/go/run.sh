#!/bin/sh
OLDGOPATH=$GOPATH
export GOPATH=.:$GOPATH

go run test_fleet_api.go

export GOPATH=$ODLGOPATH
