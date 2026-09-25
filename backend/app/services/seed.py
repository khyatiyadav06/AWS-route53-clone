from app.models import User, HostedZone, DNSRecord

def seed(db):
    if db.query(User).count() == 0:
        db.add(User(email="demo@route53.local", name="Demo User"))
    if db.query(HostedZone).count() > 0:
        db.commit(); return
    zones = [
        HostedZone(name="example.com", zone_id="ZEXAMPLE01", description="Main fictional website", zone_type="Public"),
        HostedZone(name="myapp.com", zone_id="ZMYAPP02", description="Demo application environment", zone_type="Public"),
        HostedZone(name="company.internal", zone_id="ZINTERNAL03", description="Internal fictional services", zone_type="Private"),
    ]
    db.add_all(zones); db.flush()
    records = [
        DNSRecord(hosted_zone_id=zones[0].id, name="example.com", type="A", ttl=300, value="192.0.2.10"),
        DNSRecord(hosted_zone_id=zones[0].id, name="www.example.com", type="CNAME", ttl=300, value="example.com"),
        DNSRecord(hosted_zone_id=zones[0].id, name="example.com", type="MX", ttl=3600, value="10 mail.example.com"),
        DNSRecord(hosted_zone_id=zones[0].id, name="example.com", type="TXT", ttl=300, value='"v=spf1 include:example.invalid ~all"'),
        DNSRecord(hosted_zone_id=zones[1].id, name="myapp.com", type="A", ttl=300, value="192.0.2.20"),
        DNSRecord(hosted_zone_id=zones[1].id, name="api.myapp.com", type="AAAA", ttl=300, value="2001:db8::20"),
        DNSRecord(hosted_zone_id=zones[2].id, name="company.internal", type="NS", ttl=900, value="ns-1.company.internal"),
    ]
    db.add_all(records); db.commit()
