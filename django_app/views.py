from django.shortcuts import render
from django.conf import settings
import requests
from django.views import View
from google_auth_oauthlib.flow import InstalledAppFlow
from django.urls import reverse
from django.shortcuts import redirect


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def list_events(access_token, request):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    # Make a GET request to the Google Calendar API to list events
    response = requests.get(
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        headers=headers)

    if response.status_code == 200:
        # Parse the response JSON to extract the events
        events = response.json().get('items', [])
        context = {'events': events}
        # return events[0]
        return render(request, 'events_list.html', context)
    else:
        # Handle the error response
        error = response.json().get('error', {})
        error_message = error.get('message', 'Unknown error')
        raise Exception(f'Error listing events: {error_message}')


class GoogleCalendarInitView(View):
    def get(self, request):

        # create the OAuth 2.0 client
        redirect_uri = 'https://' + request.get_host() + reverse('redirect')
        flow = InstalledAppFlow.from_client_config(
            settings.GOOGLE_OAUTH_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=redirect_uri)

        # build the authorization URL and redirect the user
        auth_url, state = flow.authorization_url(access_type='offline',
                                                 include_granted_scopes='true')

        # Store the state token in the session so we can use it later
        request.session['state'] = state

        return redirect(auth_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        if 'code' not in request.GET:
            # If the code is not present in the request, redirect the user to the login page
            return redirect(
                'https://calenderly.nishthasrivast2.repl.co/rest/v1/calendar/init/'
            )
        # If the code is present, use it to fetch the access token
        # Get the authorization code from the request
        code = request.GET.get('code')
        redirect_uri = 'https://' + request.get_host() + reverse('redirect')
        flow = InstalledAppFlow.from_client_config(
            settings.GOOGLE_OAUTH_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=redirect_uri)

        flow.fetch_token(code=code)
        # Save the access token in the session
        credentials = flow.credentials
        request.session['google_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        access_token = (request.session['google_credentials']['token'])
        return list_events(access_token, request)
        # print("hi")
        # print(events)
        # return render(request, 'privacy_policy.html')
