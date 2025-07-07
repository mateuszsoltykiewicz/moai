# /Python/libraries/core/ntp_sync/__init__.py
import ntplib

async def check_ntp_sync(ntp_server='pool.ntp.org', max_drift=1):
    c = ntplib.NTPClient()
    response = c.request(ntp_server, version=3)
    drift = abs(response.offset)
    if drift > max_drift:
        raise Exception(f"NTP drift too high: {drift}s")
    return drift
