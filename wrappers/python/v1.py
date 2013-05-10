# -*- coding: utf-8 -*-
"""
Requires requests package (for Python 2.5 or older, use "simplejson" instead of "json"
"""
import os
import urllib
import json
import requests
import sys

ENVIRONMENTS = {
    'local': {
        'API_KEY': '6cc57fbdb46add230d3fd02c772e9ff4', # Must be copied from https://tdispatch.com/preferences/fleet-api/
        'AUTH_CODE': '518267d3b6c1211aeadce33b', # Must be requested to /fleet/v1/oauth2/auth/
        'REFRESH_TOKEN': 'BBNtnoOA9gZWMzmGxVszWNUZApe6ASAV', # Must be copied from token code URL after authorization
        'ACCESS_TOKEN': '518267d3b6c1211aeadce33a', # Must be copied from token code URL after authorization

        'CLIENT_ID': 'eiWZgrp41H@tdispatch.com',
        'CLIENT_SECRET': 'vTxLDqHSCVdxZtFk24MKytDHAmjkFLOX',
        'REDIRECT_URL': '',
        'API_ROOT_URL': 'http://localhost:9500/fleet',
        },
    'sandbox': {
        'API_KEY': '1406c6d7adc7ba7d1507802a7205929c', # Must be copied from https://tdispatch.com/preferences/fleet-api/
        'AUTH_CODE': '', # Must be requested to /fleet/v1/oauth2/auth/
        'REFRESH_TOKEN': '', # Must be copied from token code URL after authorization
        'ACCESS_TOKEN': '', # Must be copied from token code URL after authorization

        'CLIENT_ID': 'QEQtjlXPem@tdispatch.com',
        'CLIENT_SECRET': 'MdEoLIZIc2WWNs8qC0raEyFaMFsh3xeP',
        'REDIRECT_URL': '',
        'API_ROOT_URL': 'https://api.t-dispatch.co/fleet',
        },
    }
ENV = ENVIRONMENTS.get(sys.argv[1] if len(sys.argv) > 1 else 'staging')
if not ENV:
    sys.exit('Environment "%s" not found.' % sys.argv[1])

CLIENT_SCOPES = []
AUTH_URI = ENV['API_ROOT_URL'] + '/oauth2/auth'
TOKEN_URI = ENV['API_ROOT_URL'] + '/oauth2/token'
REVOKE_URI = ENV['API_ROOT_URL'] + '/oauth2/revoke'
SCOPE_URI = ENV['API_ROOT_URL']


class RequestFailed(BaseException): pass


class FleetAPIClient(object):
    auth_uri = AUTH_URI
    token_uri = TOKEN_URI
    scope_uri = SCOPE_URI
    revoke_uri = REVOKE_URI
    base_url = None
    client_id = None
    client_secret = None
    api_key = None
    auth_code = None # Must be informed manually
    refresh_token = None # Must be informed manually
    access_token = None # Must be informed manually

    def __init__(self, client_id, client_secret, redirect_url, base_url=ENV['API_ROOT_URL']+"/v1/"):
        """Parameters:
        - client_id: supplied by TDispatch app's registration
        - client_secret: supplied by TDispatch app's registration"""

        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

    def get_token_request_url(self):
        resp = requests.post(self.auth_uri, {
            'key':self.api_key,
            'response_type':'code',
            'client_id':self.client_id,
            'redirect_uri':self.redirect_url,
            'scope':' '.join(CLIENT_SCOPES),
            #'state':,
            }, verify=False)
        return resp.content
    
    def get_refresh_token(self):
        resp = requests.post(self.token_uri, {
            'code':self.auth_code,
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'redirect_uri':'',
            'grant_type':'authorization_code',
            }, verify=False)
        return resp.content

    def get_access_token(self):
        resp = requests.post(self.token_uri, {
            'refresh_token':self.refresh_token,
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'grant_type':'refresh_token',
            }, verify=False)
        return resp.content

    def revoke_access_token(self):
        resp = requests.post(self.revoke_uri, {
            'grant_type':'access_token',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'refresh_token':self.refresh_token,
            'access_token':self.access_token,
            }, verify=False)
        return resp.content
    
    def revoke_refresh_token(self):
        resp = requests.post(self.revoke_uri, {
            'grant_type':'refresh_token',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'refresh_token':self.refresh_token,
            }, verify=False)
        return resp.content

    def request(self, method, url, data=None):
        print '\n', '-'*40
        print '/%s' % url
        url = self.base_url + url
        url += '&' if '?' in url else '?'
        url += 'access_token=' + self.access_token
        body = json.dumps(data) if data else ''

        if method.upper() == 'POST':
            resp = requests.post(url, body, verify=False)
        elif method.upper() == 'PUT':
            resp = requests.put(url, body, verify=False)
        elif method.upper() == 'DELETE':
            resp = requests.delete(url, verify=False)
        else:
            resp = requests.get(url + ('&' + urllib.urlencode(body) if body else ''), verify=False)

        if resp.headers['content-type'].startswith('application/json'):
            print resp.content, '\n'
            return json.loads(resp.content)
        else:
            raise RequestFailed('Method "%s" returned: %s (%s)' % (url,resp.content,resp.status_code))

    # Method for API

    def api_info(self):
        return self.request('GET','api-info')

    # Methods for the Fleet

    def fleet_info(self):
        return self.request('GET','fleet')

    # Methods for Accounts

    def account_create(self, **kwargs):
        return self.request('POST','accounts', kwargs)

    def accounts_list(self, **kwargs):
        return self.request('GET','accounts?'+urllib.urlencode(kwargs))

    def account_update(self, pk, **kwargs):
        return self.request('POST','accounts/%s' % pk,kwargs)

    def account_delete(self, pk, **kwargs):
        return self.request('DELETE','accounts/%s' % pk,kwargs)

    # Methods for Account groups

    def group_create(self, **kwargs):
        return self.request('POST','groups', kwargs)

    def groups_list(self, **kwargs):
        return self.request('GET','groups?'+urllib.urlencode(kwargs))

    def group_update(self, pk, **kwargs):
        return self.request('POST','groups/%s' % pk,kwargs)

    def group_delete(self, pk, **kwargs):
        return self.request('DELETE','groups/%s' % pk,kwargs)

    # Methods for Passengers

    def passenger_create(self, **kwargs):
        return self.request('POST','passengers', kwargs)

    def passengers_list(self, **kwargs):
        return self.request('GET','passengers?'+urllib.urlencode(kwargs))

    def passenger_info(self, pk):
        return self.request('GET','passengers/%s' % pk)

    def passenger_update(self, pk, **kwargs):
        return self.request('POST','passengers/%s' % pk,kwargs)

    def passenger_delete(self, pk, **kwargs):
        return self.request('DELETE','passengers/%s' % pk,kwargs)

    # Methods for Bookings

    def bookings_list(self, **kwargs):
        return self.request('GET','bookings?'+urllib.urlencode(kwargs))

    def booking_create(self, **kwargs):
        return self.request('POST','bookings',kwargs)

    def booking_update(self, pk, **kwargs):
        return self.request('POST','bookings/%s' % pk,kwargs)

    def booking_status(self, pk):
        return self.request('GET','bookings/%s/status' % pk)

    # Locations search

    def locations_search(self, **kwargs):
        return self.request('GET','locations?'+urllib.urlencode(kwargs))


api = FleetAPIClient(ENV['CLIENT_ID'], ENV['CLIENT_SECRET'], ENV['REDIRECT_URL'])
api.api_key = ENV.get('API_KEY')
api.auth_code = ENV.get('AUTH_CODE')
api.refresh_token = ENV.get('REFRESH_TOKEN')
api.access_token = ENV.get('ACCESS_TOKEN')

print '-'*40
if api.access_token:
    print 'Testing the API methods'

    #api.revoke_access_token()
    #api.revoke_refresh_token()
    #sys.exit(0)

    # API info
    api.api_info()

    # Fleet
    api.fleet_info()

    # Locations
    api.locations_search(q='ab10', limit=3)

    # Accounts
    new_account = api.account_create(name='Aldi', credit_per_month=350, origin_id='888')
    api.accounts_list(limit=1, origin_id='888')
    api.account_update(pk=new_account['account']['pk'], name='Aldi New')
    api.accounts_list(limit=1, origin_id='888')

    # Account groups
    new_group = api.group_create(name='Aldi', credit_per_month=350, origin_id='777', account=new_account['account']['pk'])
    api.groups_list(limit=1, origin_id='888')
    api.group_update(pk=new_group['group']['pk'], name='Aldi New')
    api.groups_list(limit=1, origin_id='888')
    api.group_delete(pk=new_group['group']['pk'])

    # Passengers
    new_passenger = api.passenger_create(name='Mario', birth_date='1982-07-15', origin_id='999',
            account=new_account['account']['pk'])
    api.passengers_list(limit=1, origin_id='999')
    api.passenger_update(pk=new_passenger['passenger']['pk'], name='Mario New')
    api.passengers_list(limit=1, origin_id='999')
    api.passenger_delete(pk=new_passenger['passenger']['pk'])

    api.account_delete(pk=new_account['account']['pk'])

    passengers = api.passengers_list(limit=1)
    passenger = api.passenger_info(passengers['passengers'][0]['pk'])['passenger']

    # Bookings
    api.bookings_list(limit=1)
    api.bookings_list(step=1,limit=1)
    api.bookings_list(pickup_time='2012-11-08T17:56:46Z')
    api.bookings_list(customer=passenger['pk'], limit=1)
    
    booking = api.booking_create(
        passenger=passenger['pk'],
        customer_name='Pablo Picasso',
        customer_phone='+49123470416',
        customer_email='pablo@tdispatch.com',
        distance=2500,
        duration=900,
        pickup_time='2013-05-07T10:30:00-02:00',
        return_time='2013-05-09T10:30:00-02:00',
        pickup_location={'address':u'Grüntaler strasse 11', 'location':{'lat':52.552037,'lng':13.387291}, 'postcode':'13357'},
        dropoff_location={'address':u'Wöhlertstraße 10', 'location':{'lat':52.53673,'lng':13.379416}, 'postcode':'10115'},
        way_points=[{'address':u'Voltastraße 100', 'location':{'lat':52.542381,'lng':13.392463}, 'postcode':'13355'}],
        extra_instructions='The three guys in blue.',
        luggage=5,
        passengers=3,
        payment_method='cash',
        pre_paid=False,
        status='incoming',
        )['booking']

    api.booking_update(pk=booking['pk'], luggage=3)

    api.booking_status(pk=booking['pk'])
elif api.refresh_token:
    print 'Getting new access token'
    print api.get_access_token()
elif api.auth_code:
    print 'Getting refresh token with auth code'
    print api.get_refresh_token()
else:
    print 'Requesting Fleet authorization'
    print api.get_token_request_url()
print '-'*40

