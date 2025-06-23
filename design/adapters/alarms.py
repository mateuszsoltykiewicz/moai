from typing import Optional, Dict, Any
import requests
from opsgenie_sdk import AlertApi, Configuration, ApiClient, CreateAlertPayload
import os
from slack_sdk import WebClient
import smtplib
from email.message import EmailMessage


class AlarmAdapter:
    def raise_alarm(self, title: str, description: str, severity: str = "critical", details: Optional[Dict[str, Any]] = None) -> str:
        """Raise a new alarm. Returns alarm/incident ID."""
        raise NotImplementedError

    def resolve_alarm(self, alarm_id: str, note: Optional[str] = None) -> None:
        """Resolve/close an alarm by ID."""
        raise NotImplementedError

    def acknowledge_alarm(self, alarm_id: str, note: Optional[str] = None) -> None:
        """Acknowledge an alarm (if supported)."""
        raise NotImplementedError


class PagerDutyAdapter(AlarmAdapter):
    def __init__(self, api_key: str, service_id: str):
        self.api_key = api_key
        self.service_id = service_id
        self.base_url = "https://api.pagerduty.com"
        self.headers = {
            "Authorization": f"Token token={self.api_key}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json"
        }

    def raise_alarm(self, title, description, severity="critical", details=None):
        payload = {
            "incident": {
                "type": "incident",
                "title": title,
                "service": {"id": self.service_id, "type": "service_reference"},
                "body": {"type": "incident_body", "details": description},
                "severity": severity
            }
        }
        if details:
            payload["incident"]["body"]["details"] += f"\n\nDetails: {details}"
        resp = requests.post(f"{self.base_url}/incidents", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()["incident"]["id"]

    def resolve_alarm(self, alarm_id, note=None):
        payload = {"incident": {"type": "incident", "status": "resolved"}}
        if note:
            payload["incident"]["body"] = {"type": "incident_body", "details": note}
        resp = requests.put(f"{self.base_url}/incidents/{alarm_id}", json=payload, headers=self.headers)
        resp.raise_for_status()

    def acknowledge_alarm(self, alarm_id, note=None):
        payload = {"incident": {"type": "incident", "status": "acknowledged"}}
        if note:
            payload["incident"]["body"] = {"type": "incident_body", "details": note}
        resp = requests.put(f"{self.base_url}/incidents/{alarm_id}", json=payload, headers=self.headers)
        resp.raise_for_status()

class OpsgenieAdapter(AlarmAdapter):
    def __init__(self, api_key: str):
        config = Configuration(api_key=api_key)
        self.client = AlertApi(ApiClient(config))

    def raise_alarm(self, title, description, severity="critical", details=None):
        payload = CreateAlertPayload(
            message=title,
            description=description,
            priority=severity.upper()[0],  # Opsgenie: P1, P2, etc.
            details=details or {}
        )
        resp = self.client.create_alert(payload)
        return resp.alert_id

    def resolve_alarm(self, alarm_id, note=None):
        self.client.close_alert(identifier=alarm_id, identifier_type="id", note=note)

    def acknowledge_alarm(self, alarm_id, note=None):
        self.client.acknowledge_alert(identifier=alarm_id, identifier_type="id", note=note)

class SlackAdapter(AlarmAdapter):
    def __init__(self, token: str, channel: str):
        self.client = WebClient(token=token)
        self.channel = channel

    def raise_alarm(self, title, description, severity="critical", details=None):
        message = f"*{severity.upper()}* - {title}\n{description}"
        if details:
            message += f"\nDetails: {details}"
        resp = self.client.chat_postMessage(channel=self.channel, text=message)
        return resp["ts"]  # Slack message timestamp as ID

    def resolve_alarm(self, alarm_id, note=None):
        # Optionally send a follow-up message or update the original
        self.client.chat_postMessage(channel=self.channel, text=f":white_check_mark: Alarm resolved: {note or alarm_id}")

    def acknowledge_alarm(self, alarm_id, note=None):
        self.client.chat_postMessage(channel=self.channel, text=f":eyes: Alarm acknowledged: {note or alarm_id}")

class EmailAdapter(AlarmAdapter):
    def __init__(self, smtp_host, smtp_port, username, password, from_addr, to_addrs):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs

    def raise_alarm(self, title, description, severity="critical", details=None):
        msg = EmailMessage()
        msg["Subject"] = f"[{severity.upper()}] {title}"
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(self.to_addrs)
        msg.set_content(f"{description}\n\nDetails: {details or ''}")
        with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
            server.login(self.username, self.password)
            server.send_message(msg)
        return msg["Subject"]

    def resolve_alarm(self, alarm_id, note=None):
        # Optionally send a follow-up email
        pass

    def acknowledge_alarm(self, alarm_id, note=None):
        # Optionally send a follow-up email
        pass

class WebhookAdapter(AlarmAdapter):
    def __init__(self, url: str, headers=None):
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}

    def raise_alarm(self, title, description, severity="critical", details=None):
        payload = {
            "title": title,
            "description": description,
            "severity": severity,
            "details": details or {}
        }
        resp = requests.post(self.url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.text

    def resolve_alarm(self, alarm_id, note=None):
        # Optionally send a resolve event
        pass

    def acknowledge_alarm(self, alarm_id, note=None):
        # Optionally send an acknowledge event
        pass

class AlarmAdapterRegistry:
    def __init__(self, config):
        self.adapters = {}
        if config.pagerduty.enabled:
            self.adapters["pagerduty"] = PagerDutyAdapter(config.pagerduty.api_key, config.pagerduty.service_id)
        if config.opsgenie.enabled:
            self.adapters["opsgenie"] = OpsgenieAdapter(config.opsgenie.api_key)
        if config.slack.enabled:
            self.adapters["slack"] = SlackAdapter(config.slack.token, config.slack.channel)
        if config.email.enabled:
            self.adapters["email"] = EmailAdapter(
                config.email.smtp_host, config.email.smtp_port,
                config.email.username, config.email.password,
                config.email.from_addr, config.email.to_addrs
            )
        if config.webhook.enabled:
            self.adapters["webhook"] = WebhookAdapter(config.webhook.url, config.webhook.headers)

    def get(self, name):
        return self.adapters[name]

