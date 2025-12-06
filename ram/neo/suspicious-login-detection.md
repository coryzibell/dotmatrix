# Suspicious Login Detection System

A behavioral analysis system that detects suspicious login attempts by establishing per-user baselines and scoring deviations from normal patterns.

## Core Concept

Rather than one-size-fits-all rules, this system:

1. **Baselines first** - Captures the first N logins to understand each user's patterns
2. **Adapts to user type** - Distinguishes travelers from stationary users
3. **Accumulates risk** - Scores multiple signals rather than binary pass/fail
4. **Builds trust** - Successful logins from new locations gradually reduce their risk

## Risk Signals

| Signal | Points | Notes |
|--------|--------|-------|
| Impossible travel | +50-100 | SF to London in 1 hour = physically impossible |
| New country | +40-60 | Lower for known travelers |
| New city (same country) | +15-40 | Scaled by user type |
| New ASN/ISP | +15 | Network fingerprint changed |
| Datacenter IP | +30 | Residential user on VPS/VPN |
| Unusual hour | +15-25 | Login at 3am when user is 9-5 |

### Score Thresholds

| Score | Action |
|-------|--------|
| 0-19 | Allow, update profile |
| 20-39 | Allow with notification |
| 40-69 | Require MFA challenge |
| 70+ | Block, alert security team |

## Key Detection Methods

### Impossible Travel

Calculate if the user could physically travel between two login locations:

- Max human speed: ~900 km/h (commercial flight)
- If required speed exceeds this, flag as impossible
- Also catches VPN hopping, credential sharing, account compromise

### Per-User Behavioral Baseline

- Location clusters (home, work, frequent travel spots)
- Typical login hours (histogram)
- Known ASNs/ISPs
- Device fingerprints (if available)

### Traveler vs Stationary Classification

After baseline period:
- **Stationary**: 1-2 locations, consistent patterns → strict thresholds
- **Traveler**: 3+ locations, varied patterns → relaxed location scoring, but impossible travel still applies

---

## Implementation

```python
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

@dataclass
class LoginEvent:
    email: str
    ip: str
    timestamp: datetime
    lat: float = 0.0
    lon: float = 0.0
    city: str = ""
    country: str = ""
    asn: str = ""
    isp_type: str = ""  # residential, datacenter, mobile, etc.

@dataclass
class UserProfile:
    email: str
    locations: list = field(default_factory=list)  # [{lat, lon, city, country, count}]
    asns: set = field(default_factory=set)
    login_hours: list = field(default_factory=lambda: [0] * 24)  # histogram
    is_traveler: bool = False
    baseline_complete: bool = False


class SuspiciousLoginDetector:
    EARTH_RADIUS_KM = 6371
    MAX_HUMAN_SPEED_KMH = 900  # commercial flight
    BASELINE_LOGINS = 5

    def __init__(self, geo_provider=None):
        self.profiles: dict[str, UserProfile] = {}
        self.login_history: dict[str, list[LoginEvent]] = defaultdict(list)
        self.geo_provider = geo_provider  # Inject geolocation service

    def haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points on Earth using Haversine formula."""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return 2 * self.EARTH_RADIUS_KM * math.asin(math.sqrt(a))

    def geolocate_ip(self, ip: str) -> dict:
        """
        Geolocate an IP address.

        In production, use self.geo_provider which should implement:
        - MaxMind GeoIP2 (local DB)
        - ipinfo.io API
        - ip-api.com
        """
        if self.geo_provider:
            return self.geo_provider.lookup(ip)

        # Fallback placeholder for development
        return {
            "lat": 0.0,
            "lon": 0.0,
            "city": "Unknown",
            "country": "XX",
            "asn": "",
            "isp_type": "unknown"
        }

    def check_impossible_travel(
        self,
        event: LoginEvent,
        last_event: LoginEvent
    ) -> tuple[bool, float]:
        """
        Check if travel between two logins is physically possible.

        Returns:
            (is_impossible, severity_score)
        """
        distance_km = self.haversine_km(
            last_event.lat, last_event.lon,
            event.lat, event.lon
        )
        time_diff_hours = (event.timestamp - last_event.timestamp).total_seconds() / 3600

        if time_diff_hours <= 0:
            # Same timestamp or time travel - suspicious if distance > 50km
            return (True, 100.0) if distance_km > 50 else (False, 0.0)

        required_speed = distance_km / time_diff_hours

        if required_speed > self.MAX_HUMAN_SPEED_KMH:
            # Impossible - severity scales with how impossible
            severity = min(100, (required_speed / self.MAX_HUMAN_SPEED_KMH) * 50)
            return True, severity

        return False, 0.0

    def calculate_location_score(self, event: LoginEvent, profile: UserProfile) -> float:
        """Score based on how unusual this location is for the user."""
        if not profile.locations:
            return 0.0

        # Find closest known location
        min_distance = float('inf')
        for loc in profile.locations:
            dist = self.haversine_km(event.lat, event.lon, loc['lat'], loc['lon'])
            min_distance = min(min_distance, dist)

        # Score based on distance from known locations
        # Travelers get lower scores for the same distances
        if min_distance < 50:  # Same metro area
            return 0.0
        elif min_distance < 200:  # Same region
            return 10.0 if profile.is_traveler else 20.0
        elif min_distance < 500:  # Different region
            return 20.0 if profile.is_traveler else 40.0
        else:  # Far away / different country
            return 30.0 if profile.is_traveler else 60.0

    def calculate_time_score(self, event: LoginEvent, profile: UserProfile) -> float:
        """Score based on unusual login time for this user."""
        hour = event.timestamp.hour
        total_logins = sum(profile.login_hours)

        if total_logins < self.BASELINE_LOGINS:
            return 0.0

        hour_frequency = profile.login_hours[hour] / total_logins

        if hour_frequency == 0:
            return 25.0  # Never logged in at this hour
        elif hour_frequency < 0.05:
            return 15.0  # Rare hour

        return 0.0

    def calculate_asn_score(self, event: LoginEvent, profile: UserProfile) -> float:
        """Score based on network characteristics."""
        score = 0.0

        # New ASN they've never used
        if event.asn and event.asn not in profile.asns:
            score += 15.0

        # Datacenter/VPN IP for a user who normally uses residential
        if event.isp_type == "datacenter" and profile.asns:
            score += 30.0

        return score

    def update_profile(self, event: LoginEvent, profile: UserProfile):
        """Update user profile with new login data."""
        # Update location history
        found = False
        for loc in profile.locations:
            if self.haversine_km(event.lat, event.lon, loc['lat'], loc['lon']) < 50:
                loc['count'] += 1
                found = True
                break

        if not found:
            profile.locations.append({
                'lat': event.lat,
                'lon': event.lon,
                'city': event.city,
                'country': event.country,
                'count': 1
            })

        # Update ASN tracking
        if event.asn:
            profile.asns.add(event.asn)

        # Update login hour histogram
        profile.login_hours[event.timestamp.hour] += 1

        # Classify as traveler if 3+ distinct locations
        if len(profile.locations) >= 3:
            profile.is_traveler = True

        # Mark baseline complete after enough logins
        login_count = sum(loc['count'] for loc in profile.locations)
        if login_count >= self.BASELINE_LOGINS:
            profile.baseline_complete = True

    def evaluate_login(
        self,
        email: str,
        ip: str,
        timestamp: Optional[datetime] = None
    ) -> dict:
        """
        Main entry point - evaluate a login attempt.

        Args:
            email: User's email address
            ip: IP address of the login attempt
            timestamp: When the login occurred (defaults to now)

        Returns:
            dict with risk_score, action, factors, and metadata
        """
        timestamp = timestamp or datetime.utcnow()

        # Get or create profile
        if email not in self.profiles:
            self.profiles[email] = UserProfile(email=email)
        profile = self.profiles[email]

        # Geolocate the IP
        geo = self.geolocate_ip(ip)
        event = LoginEvent(
            email=email,
            ip=ip,
            timestamp=timestamp,
            **geo
        )

        # Build risk score
        risk_score = 0.0
        risk_factors = []

        # During baseline period, just collect data
        if not profile.baseline_complete:
            self.login_history[email].append(event)
            self.update_profile(event, profile)
            baseline_count = sum(loc['count'] for loc in profile.locations)
            return {
                "risk_score": 0,
                "action": "allow",
                "reason": f"Building baseline ({baseline_count}/{self.BASELINE_LOGINS})",
                "factors": [],
                "baseline_complete": False
            }

        # Check impossible travel against last login
        history = self.login_history[email]
        if history:
            last = history[-1]
            impossible, travel_score = self.check_impossible_travel(event, last)
            if impossible:
                risk_score += travel_score
                distance = self.haversine_km(last.lat, last.lon, event.lat, event.lon)
                time_diff = (event.timestamp - last.timestamp).total_seconds() / 3600
                risk_factors.append(
                    f"Impossible travel: {last.city} → {event.city} "
                    f"({distance:.0f}km in {time_diff:.1f}h)"
                )

        # Location score
        loc_score = self.calculate_location_score(event, profile)
        if loc_score > 0:
            risk_score += loc_score
            risk_factors.append(f"Unusual location: {event.city}, {event.country}")

        # Time score
        time_score = self.calculate_time_score(event, profile)
        if time_score > 0:
            risk_score += time_score
            risk_factors.append(f"Unusual login hour: {timestamp.hour}:00 UTC")

        # ASN/Network score
        asn_score = self.calculate_asn_score(event, profile)
        if asn_score > 0:
            risk_score += asn_score
            if event.isp_type == "datacenter":
                risk_factors.append(f"Datacenter/VPN IP detected: {event.asn}")
            else:
                risk_factors.append(f"New network: {event.asn}")

        # Record this login
        self.login_history[email].append(event)

        # Determine action based on score
        if risk_score >= 70:
            action = "block"
        elif risk_score >= 40:
            action = "mfa_challenge"
        elif risk_score >= 20:
            action = "allow_with_notification"
        else:
            action = "allow"
            # Only update profile on low-risk logins
            # (or call update_profile after successful MFA)
            self.update_profile(event, profile)

        return {
            "risk_score": round(risk_score, 1),
            "action": action,
            "factors": risk_factors,
            "user_type": "traveler" if profile.is_traveler else "stationary",
            "location": f"{event.city}, {event.country}",
            "ip": ip,
            "baseline_complete": True
        }

    def on_mfa_success(self, email: str):
        """
        Call this after successful MFA to update profile with the challenged login.
        This allows new legitimate locations to be learned.
        """
        if email in self.profiles and email in self.login_history:
            history = self.login_history[email]
            if history:
                self.update_profile(history[-1], self.profiles[email])
```

---

## Production Adaptations

The reference implementation above works for demonstration but needs several adaptations for production use:

1. **Replace in-memory storage** - The `profiles` and `login_history` dicts live in memory and vanish on restart. Swap these for Redis (fast lookups) backed by PostgreSQL (durability). See the `RedisProfileStore` example below.

2. **Inject a real geo provider** - The placeholder `geolocate_ip()` returns dummy data. Wire up MaxMind GeoIP2 for high-volume local lookups or ipinfo.io for a simpler API-based approach.

3. **Add ISP type detection** - The code scores datacenter IPs but can't detect them without a service like IPQualityScore or Spur.us. This is critical for catching VPN/proxy abuse.

4. **Make it async** - The synchronous `evaluate_login()` blocks on geo lookups and DB calls. For web frameworks (FastAPI, etc.), convert to `async def` and use async Redis/HTTP clients.

5. **Add circuit breakers** - If the geo API or Redis goes down, fail open (allow login, log for later analysis) rather than blocking all users.

6. **Emit structured logs** - Every evaluation should log `{email, ip, risk_score, action, factors, latency_ms}` for audit trails and threshold tuning.

7. **Rate limit the detector itself** - An attacker could DoS by hammering logins. Add per-IP rate limiting before the detector runs.

---

## Production Requirements

### 1. Geolocation Provider

Choose one:

| Provider | Type | Accuracy | Cost | Notes |
|----------|------|----------|------|-------|
| **MaxMind GeoIP2** | Local DB | City-level | $$$  | Best for high volume, update DB monthly |
| **ipinfo.io** | API | City-level | Free tier available | Good accuracy, 50k/mo free |
| **ip-api.com** | API | City-level | Free tier available | Rate limited, no commercial use on free |

```python
# MaxMind GeoIP2 integration
import geoip2.database

class MaxMindProvider:
    def __init__(self, db_path: str):
        self.city_reader = geoip2.database.Reader(f"{db_path}/GeoLite2-City.mmdb")
        self.asn_reader = geoip2.database.Reader(f"{db_path}/GeoLite2-ASN.mmdb")

    def lookup(self, ip: str) -> dict:
        try:
            city = self.city_reader.city(ip)
            asn = self.asn_reader.asn(ip)
            return {
                "lat": city.location.latitude,
                "lon": city.location.longitude,
                "city": city.city.name or "Unknown",
                "country": city.country.iso_code or "XX",
                "asn": f"AS{asn.autonomous_system_number}",
                "isp_type": "unknown"  # MaxMind doesn't provide this directly
            }
        except Exception:
            return {"lat": 0, "lon": 0, "city": "Unknown", "country": "XX", "asn": "", "isp_type": "unknown"}
```

### 2. ASN/ISP Type Detection

For detecting datacenter vs residential IPs:

| Service | What it provides |
|---------|-----------------|
| **IPQualityScore** | Fraud scores, VPN/proxy/datacenter detection |
| **Spur.us** | Residential proxy detection, VPN fingerprinting |
| **ipinfo.io Privacy** | VPN, proxy, Tor, relay detection |

### 3. Persistence Layer

Store profiles and history in a database:

```python
# Redis for fast lookups + PostgreSQL for durability

import redis
import json

class RedisProfileStore:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.profile_ttl = 86400 * 90  # 90 days

    def get_profile(self, email: str) -> Optional[UserProfile]:
        data = self.redis.get(f"login_profile:{email}")
        if data:
            return UserProfile(**json.loads(data))
        return None

    def save_profile(self, profile: UserProfile):
        self.redis.setex(
            f"login_profile:{profile.email}",
            self.profile_ttl,
            json.dumps(asdict(profile), default=list)
        )

    def get_recent_logins(self, email: str, limit: int = 10) -> list[LoginEvent]:
        data = self.redis.lrange(f"login_history:{email}", 0, limit - 1)
        return [LoginEvent(**json.loads(d)) for d in data]

    def add_login(self, event: LoginEvent):
        self.redis.lpush(
            f"login_history:{event.email}",
            json.dumps(asdict(event), default=str)
        )
        self.redis.ltrim(f"login_history:{event.email}", 0, 99)  # Keep last 100
```

### 4. Device Fingerprinting (Optional Enhancement)

Layer in device/browser fingerprints for stronger signals:

- **FingerprintJS** - Browser fingerprinting
- **Device ID from mobile SDKs** - iOS/Android device identifiers

A login from a known device + new location is less suspicious than unknown device + new location.

### 5. Alerting Integration

```python
# Webhook for security team alerts
import httpx

async def alert_security_team(event: LoginEvent, result: dict):
    if result["action"] == "block":
        await httpx.post(
            "https://your-webhook.com/security-alerts",
            json={
                "type": "blocked_login",
                "email": event.email,
                "ip": event.ip,
                "risk_score": result["risk_score"],
                "factors": result["factors"],
                "location": result["location"],
                "timestamp": event.timestamp.isoformat()
            }
        )
```

---

## Usage Example

```python
from datetime import datetime, timedelta

# Initialize with geo provider
geo = MaxMindProvider("/path/to/geodb")
detector = SuspiciousLoginDetector(geo_provider=geo)

# Baseline period - first 5 logins build the profile
for i in range(5):
    result = detector.evaluate_login(
        email="user@example.com",
        ip="73.162.45.100",  # Home IP
        timestamp=datetime(2024, 1, 15, 9, 0) + timedelta(days=i)
    )
    print(f"Baseline login {i+1}: {result['action']}")

# Now test various scenarios
# Normal login from home
result = detector.evaluate_login("user@example.com", "73.162.45.100")
# -> action: "allow", risk_score: 0

# Login from coffee shop in same city
result = detector.evaluate_login("user@example.com", "67.180.12.44")
# -> action: "allow" or "allow_with_notification"

# Impossible travel - SF to London in 1 hour
result = detector.evaluate_login(
    "user@example.com",
    "185.220.101.42",  # London IP
    timestamp=datetime.utcnow()
)
# -> action: "block", risk_score: 80+, factors: ["Impossible travel..."]
```

---

## Tuning Recommendations

1. **Start conservative** - Lower thresholds, more MFA challenges. Gather data.
2. **Monitor false positive rate** - Track how often legitimate users hit MFA
3. **A/B test thresholds** - Gradually adjust based on real-world data
4. **Whitelist corporate IPs** - Reduce noise for known office locations
5. **Consider time-of-day** - Business hours vs off-hours may need different weights

## Future Enhancements

- [ ] Device fingerprint integration
- [ ] Machine learning model trained on historical data
- [ ] Peer group analysis (flag if user's behavior differs from similar users)
- [ ] Integration with threat intelligence feeds (known malicious IPs)
- [ ] Session behavior analysis (post-login actions)
