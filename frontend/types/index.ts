export type User = { id: number; email: string; name: string };
export type Zone = { id: number; name: string; zone_id: string; description: string; zone_type: string; created_at: string; record_count: number };
export type RecordType = "A" | "AAAA" | "CNAME" | "TXT" | "MX" | "NS" | "PTR" | "SRV" | "CAA";
export type RoutingPolicy = "Simple" | "Weighted" | "Latency" | "Failover";
export type DNSRecord = { id: number; hosted_zone_id: number; name: string; type: RecordType; ttl: number; value: string; routing_policy: RoutingPolicy; created_at: string; updated_at: string };
export type Page<T> = { items: T[]; page: number; page_size: number; total: number; pages: number };
