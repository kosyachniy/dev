from datetime import datetime, timedelta, timezone

from libdev.cfg import cfg
import google_auth_oauthlib.flow
import google.oauth2.credentials
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build


CREDS = cfg("google.credentials")
SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.activity.write",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.body.write",
]
DATA_SOURCE = (
    "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
)


class Fit:
    @staticmethod
    def auth():
        flow = google_auth_oauthlib.flow.Flow.from_client_config(CREDS, scopes=SCOPES)
        flow.redirect_uri = f"{cfg('api')}steps/callback"
        return flow

    @staticmethod
    def user_auth(creds):
        return google.oauth2.credentials.Credentials(
            **{
                "token": creds.get("token"),
                "refresh_token": creds.get("refresh_token"),
                "expiry": datetime.fromtimestamp(creds.get("expiry", 0)),
                "token_uri": CREDS.get("web", {}).get("token_uri"),
                "client_id": CREDS.get("web", {}).get("client_id"),
                "client_secret": CREDS.get("web", {}).get("client_secret"),
                "scopes": SCOPES,
                "universe_domain": "googleapis.com",
                "account": "",
            }
        )

    def __init__(self, creds=None):
        if not creds:
            self.flow = self.auth()
            return

        self.creds = self.user_auth(creds)
        self.service = build("fitness", "v1", credentials=self.creds)

    def oauth(self, state):
        auth_url, _ = self.flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state=str(state),
        )
        return auth_url

    def get_creds(self, code):
        self.flow.fetch_token(code=code)
        creds = self.flow.credentials
        return {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "expiry": creds.expiry.timestamp(),
        }

    @staticmethod
    def _get_period():
        now = datetime.now(timezone(timedelta(hours=cfg("timezone"))))
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        start_timestamp = int(start.timestamp() * 1000000000)
        end_timestamp = int(end.timestamp() * 1000000000)
        return f"{start_timestamp}-{end_timestamp}"

    @staticmethod
    def _count_steps(data):
        steps = 0
        for point in data["point"]:
            if "user_input" in point["originDataSourceId"]:
                continue
            steps += point["value"][0]["intVal"]
        return steps

    def get_steps(self):
        data = (
            self.service.users()
            .dataSources()
            .datasets()
            .get(userId="me", dataSourceId=DATA_SOURCE, datasetId=self._get_period())
            .execute()
        )
        return self._count_steps(data)
