package main

import "fmt"
import "net/http"
import "net/url"
import "io/ioutil"
import "encoding/json"

var LOCAL_ENV = map[string] string {
    "API_KEY": "6cc57fbdb46add230d3fd02c772e9ff4",
    "AUTH_CODE": "518267d3b6c1211aeadce33b",
    "REFRESH_TOKEN": "BBNtnoOA9gZWMzmGxVszWNUZApe6ASAV",
    "ACCESS_TOKEN": "518267d3b6c1211aeadce33a",
    "CLIENT_ID": "eiWZgrp41H@tdispatch.com",
    "CLIENT_SECRET": "vTxLDqHSCVdxZtFk24MKytDHAmjkFLOX",
    "REDIRECT_URL": "",
    "API_ROOT_URL": "http://tdispatch:9500/fleet",
    "SCOPE": "",
    }
var STAGING_ENV = map[string] string {
    "API_KEY": "6cc57fbdb46add230d3fd02c772e9ff4",
    "AUTH_CODE": "",
    "REFRESH_TOKEN": "",
    "ACCESS_TOKEN": "",
    "CLIENT_ID": "LLNgW9FfJP@tdispatch.com",
    "CLIENT_SECRET": "zvcDMpW9jR9APLmtYQ0rfhd9rQIB0AVw",
    "REDIRECT_URL": "",
    "API_ROOT_URL": "http://api.t-dispatch.co/fleet",
    "SCOPE": "",
    }
var ENV = LOCAL_ENV
//var CLIENT_SCOPES := []string
var AUTH_URI = ENV["API_ROOT_URL"] + "/oauth2/auth"
var TOKEN_URI = ENV["API_ROOT_URL"] + "/oauth2/token"
var REVOKE_URI = ENV["API_ROOT_URL"] + "/oauth2/revoke"
var SCOPE_URI = ENV["API_ROOT_URL"]


func getTokenRequest() (string) {
    var params = url.Values{"client_id":{ENV["CLIENT_ID"]}, "client_secret":{ENV["CLIENT_SECRET"]}, "key":{ENV["API_KEY"]},
        "scope":{ENV["SCOPE"]}, "redirect_uri":{ENV["REDIRECT_URL"]}, "response_type":{"code"}}

    resp, err := http.PostForm(AUTH_URI,params)
    if err != nil {} // TODO
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {} // TODO

    return string(body)
}

func getRefreshToken() (string) {
    var params = url.Values{"client_id":{ENV["CLIENT_ID"]}, "client_secret":{ENV["CLIENT_SECRET"]}, "code":{ENV["AUTH_CODE"]},
        "redirect_uri":{ENV["REDIRECT_URL"]}, "grant_type":{"authorization_code"}}

    resp, err := http.PostForm(TOKEN_URI,params)
    if err != nil {} // TODO
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {} // TODO

    return string(body)
}

func revokeRefreshToken() (string) {
    var params = url.Values{"client_id":{ENV["CLIENT_ID"]}, "client_secret":{ENV["CLIENT_SECRET"]}, "grant_type":{"refresh_token"},
        "refresh_token":{ENV["REFRESH_TOKEN"]}}

    resp, err := http.PostForm(REVOKE_URI,params)
    if err != nil {} // TODO
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {} // TODO

    return string(body)
}

func getAccessToken() (string) {
    var params = url.Values{"client_id":{ENV["CLIENT_ID"]}, "client_secret":{ENV["CLIENT_SECRET"]}, "refresh_token":{ENV["REFRESH_TOKEN"]},
        "redirect_uri":{ENV["REDIRECT_URL"]}, "grant_type":{"refresh_token"}}

    resp, err := http.PostForm(TOKEN_URI,params)
    if err != nil {} // TODO
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {} // TODO

    return string(body)
}

func revokeAccessToken() (string) {
    var params = url.Values{"client_id":{ENV["CLIENT_ID"]}, "client_secret":{ENV["CLIENT_SECRET"]}, "grant_type":{"access_token"},
        "refresh_token":{ENV["REFRESH_TOKEN"]}, "access_token":{ENV["ACCESS_TOKEN"]}}

    resp, err := http.PostForm(REVOKE_URI,params)
    if err != nil {} // TODO
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {} // TODO

    return string(body)
}

func makeApiUrl(path string) (string) {
    return ENV["API_ROOT_URL"] + "/v1/" + path
}

func requestGet(path string, params url.Values) (interface{}) {
    params.Add("access_token",ENV["ACCESS_TOKEN"])
    fmt.Println(path) // Printing URL path

    resp, err := http.Get(makeApiUrl(path) + "?" + params.Encode())
    if err != nil {} // TODO
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {} // TODO
    //fmt.Println(string(body)+"\n") // Printing the output

    var f interface{}
    err = json.Unmarshal(body,&f)

    return f
}

type Passenger struct {
    username string
    credit_per_month int64
    origin_id string
    creation string
    phone string
    account interface{}
    name string
    title string
    birth_date string
    department string
    pk string
    job_title string
}

type PassengersResponse struct {
    status string
    status_code string
    count int64
    passengers []Passenger
}

func main() {
    fmt.Println("Testing T Dispatch Fleet API in Go Lang")

    if ENV["ACCESS_TOKEN"] != "" {
        requestGet("api-info", url.Values{})
        requestGet("fleet", url.Values{})

        var output interface{}
        output = requestGet("passengers", url.Values{})
        //count := output.(map[string]interface{})["count"]
        passengers := output.(map[string]interface{})["passengers"].([]interface{})
        fmt.Println(passengers[0]) //.(Passenger))
        //requestGet("passengers/", url.Values{})
    } else if ENV["REFRESH_TOKEN"] != "" {
        fmt.Println(getAccessToken())
    } else if ENV["AUTH_CODE"] != "" {
        fmt.Println(getRefreshToken())
    } else {
        fmt.Println(getTokenRequest())
    }
}
