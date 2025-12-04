import os
import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from app.db.database import get_db_connection


class CacheService:
    def __init__(self):
        self.ttl_seconds = int(os.getenv('CACHE_TTL_SECONDS', '604800'))
        print(f"[Cache] TTL configured: {self.ttl_seconds}s ({self.ttl_seconds / 86400:.1f} days)")

    def _generate_cache_key(self, first_name: str, last_name: str, company: str) -> str:
        normalized = f"{first_name.lower().strip()}:{last_name.lower().strip()}:{company.lower().strip()}"
        return hashlib.md5(normalized.encode()).hexdigest()

    def get(self, first_name: str, last_name: str, company: str, force_refresh: bool = False) -> Optional[Dict]:
        if force_refresh:
            print(f"[Cache] Force refresh requested, skipping cache")
            return None

        cache_key = self._generate_cache_key(first_name, last_name, company)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    scraped_data,
                    profile_data,
                    created_at,
                    access_count
                FROM profile_cache
                WHERE cache_key = ?
            """, (cache_key,))

            row = cursor.fetchone()

            if not row:
                print(f"[Cache] ✗ Miss: {first_name} {last_name} @ {company}")
                conn.close()
                return None

            created_at = datetime.fromisoformat(row['created_at']).replace(tzinfo=timezone.utc)
            age_seconds = (datetime.now(timezone.utc) - created_at).total_seconds()

            if age_seconds > self.ttl_seconds:
                print(f"[Cache] ✗ Expired: {age_seconds:.0f}s > {self.ttl_seconds}s (age > TTL)")
                conn.close()
                return None

            cursor.execute("""
                UPDATE profile_cache
                SET accessed_at = CURRENT_TIMESTAMP,
                    access_count = access_count + 1
                WHERE cache_key = ?
            """, (cache_key,))
            conn.commit()

            scraped_data = json.loads(row['scraped_data'])
            profile_data = json.loads(row['profile_data'])

            print(f"[Cache] ✓ Hit: {first_name} {last_name} @ {company} (age: {age_seconds:.0f}s, accessed: {row['access_count'] + 1}x)")

            conn.close()

            return {
                'scraped_data': scraped_data,
                'profile_data': profile_data,
                'cached': True,
                'cache_age_seconds': int(age_seconds),
                'cache_created_at': row['created_at']
            }

        except Exception as e:
            print(f"[Cache] Error reading cache: {e}")
            return None

    def set(self, first_name: str, last_name: str, company: str, scraped_data: Dict, profile_data: Dict) -> bool:
        cache_key = self._generate_cache_key(first_name, last_name, company)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            scraped_json = json.dumps(scraped_data)
            profile_json = json.dumps(profile_data)

            cursor.execute("""
                INSERT INTO profile_cache
                    (cache_key, first_name, last_name, company, scraped_data, profile_data)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    scraped_data = excluded.scraped_data,
                    profile_data = excluded.profile_data,
                    created_at = CURRENT_TIMESTAMP,
                    accessed_at = CURRENT_TIMESTAMP,
                    access_count = 0
            """, (cache_key, first_name, last_name, company, scraped_json, profile_json))

            conn.commit()
            conn.close()

            print(f"[Cache] ✓ Stored: {first_name} {last_name} @ {company}")
            return True

        except Exception as e:
            print(f"[Cache] ✗ Error storing cache: {e}")
            return False

    def delete(self, first_name: str, last_name: str, company: str) -> bool:
        cache_key = self._generate_cache_key(first_name, last_name, company)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM profile_cache WHERE cache_key = ?", (cache_key,))
            deleted = cursor.rowcount > 0

            conn.commit()
            conn.close()

            if deleted:
                print(f"[Cache] ✓ Deleted: {first_name} {last_name} @ {company}")
            else:
                print(f"[Cache] ✗ Not found: {first_name} {last_name} @ {company}")

            return deleted

        except Exception as e:
            print(f"[Cache] ✗ Error deleting cache: {e}")
            return False

    def clear_expired(self) -> int:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            expiration_date = datetime.now(timezone.utc) - timedelta(seconds=self.ttl_seconds)

            cursor.execute("""
                DELETE FROM profile_cache
                WHERE created_at > ?
            """, (expiration_date.isoformat(),))

            deleted_count = cursor.rowcount

            conn.commit()
            conn.close()

            print(f"[Cache] ✓ Cleared {deleted_count} expired entries")
            return deleted_count

        except Exception as e:
            print(f"[Cache] ✗ Error clearing expired: {e}")
            return 0

    def get_stats(self) -> Dict:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total_entries,
                    MIN(created_at) as oldest_entry,
                    MAX(created_at) as newest_entry,
                    SUM(access_count) as total_access_count
                FROM profile_cache
            """)

            row = cursor.fetchone()
            conn.close()

            return {
                'total_entries': row['total_entries'],
                'oldest_entry': row['oldest_entry'],
                'newest_entry': row['newest_entry'],
                'total_access_count': row['total_access_count'] or 0,
                'ttl_seconds': self.ttl_seconds
            }

        except Exception as e:
            print(f"[Cache] ✗ Error getting stats: {e}")
            return {
                'total_entries': 0,
                'oldest_entry': None,
                'newest_entry': None,
                'total_access_count': 0,
                'ttl_seconds': self.ttl_seconds
            }