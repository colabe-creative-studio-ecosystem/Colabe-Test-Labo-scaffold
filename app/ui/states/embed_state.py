import reflex as rx
import jwt
import datetime
from app.core.settings import settings
from app.ui.states.auth_state import AuthState


class EmbedState(AuthState):
    show_embed_modal: bool = False
    embed_token: str = ""
    embed_url: str = ""
    resource_id: str = ""
    widget_type: str = ""

    def _generate_view_token(self) -> str:
        """Generates a secure JWT for embed views."""
        if not self.user:
            return ""
        payload = {
            "tenant_id": self.user.tenant_id,
            "scopes": ["embed.read"],
            "resource": f"{self.widget_type}:{self.resource_id}",
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=settings.EMBED_TOKEN_TTL_MIN),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "nonce": rx.State.get_current_time_millis(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @rx.event
    def open_embed_modal(self, resource_id: str, widget_type: str):
        self.resource_id = resource_id
        self.widget_type = widget_type
        self.embed_token = self._generate_view_token()
        self.embed_url = (
            f"/embed/{widget_type}?resource_id={resource_id}&token={self.embed_token}"
        )
        self.show_embed_modal = True

    @rx.event
    def close_embed_modal(self):
        self.show_embed_modal = False
        self.embed_token = ""
        self.embed_url = ""