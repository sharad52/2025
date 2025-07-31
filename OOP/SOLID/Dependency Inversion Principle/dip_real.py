# Dependency Inversion Principle: Real-World Examples

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol, Union
from datetime import datetime
from enum import Enum
import json
import hashlib
import uuid

# ============================================
# EXAMPLE 1: NETFLIX/YOUTUBE - VIDEO STREAMING PLATFORM
# Critical Insight: High-level streaming logic shouldn't depend on specific CDNs
# ============================================

"""
REAL-WORLD CONTEXT: Netflix uses multiple CDNs (Akamai, Amazon CloudFront, etc.)
BUSINESS PROBLEM: Need to switch CDNs based on geography, cost, performance
CRITICAL INSIGHT: Video streaming logic shouldn't break when switching CDN providers
"""

# VIOLATION: Direct dependency on specific CDN
class BadVideoStreamer:
    """
    PROBLEMS:
    1. Tightly coupled to Akamai CDN
    2. Can't switch CDNs without code changes
    3. Impossible to test without Akamai credentials
    4. Can't implement failover to backup CDNs
    """
    def __init__(self):
        self.akamai_api_key = "akamai_secret_key"
        self.akamai_endpoint = "https://akamai-cdn.com/api"
    
    def stream_video(self, video_id: str, user_location: str) -> str:
        # Tightly coupled to Akamai-specific implementation
        akamai_url = f"{self.akamai_endpoint}/stream/{video_id}"
        print(f"Streaming from Akamai: {akamai_url}")
        return akamai_url
    
    def get_video_quality_options(self, video_id: str) -> List[str]:
        # Hardcoded to Akamai's quality format
        return ["480p_akamai", "720p_akamai", "1080p_akamai", "4k_akamai"]

# CORRECT: Dependency Inversion Applied
class CDNProvider(ABC):
    """Abstraction owned by high-level streaming service"""
    @abstractmethod
    def get_stream_url(self, video_id: str, quality: str, user_location: str) -> str:
        pass
    
    @abstractmethod
    def get_available_qualities(self, video_id: str) -> List[str]:
        pass
    
    @abstractmethod
    def get_bandwidth_cost(self, data_gb: float) -> float:
        pass
    
    @abstractmethod
    def is_available_in_region(self, region: str) -> bool:
        pass

class VideoAnalytics(ABC):
    """Abstraction for video analytics"""
    @abstractmethod
    def track_stream_start(self, user_id: str, video_id: str, quality: str) -> None:
        pass
    
    @abstractmethod
    def track_buffering_event(self, user_id: str, video_id: str, buffer_time: float) -> None:
        pass

# LOW-LEVEL IMPLEMENTATIONS (Details)
class AkamaiCDN(CDNProvider):
    """Akamai CDN implementation"""
    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.region = region
    
    def get_stream_url(self, video_id: str, quality: str, user_location: str) -> str:
        return f"https://akamai-{self.region}.com/video/{video_id}/{quality}"
    
    def get_available_qualities(self, video_id: str) -> List[str]:
        return ["480p", "720p", "1080p", "4K"]
    
    def get_bandwidth_cost(self, data_gb: float) -> float:
        return data_gb * 0.085  # $0.085 per GB
    
    def is_available_in_region(self, region: str) -> bool:
        return region in ["US", "EU", "ASIA"]

class CloudFrontCDN(CDNProvider):
    """Amazon CloudFront implementation"""
    def __init__(self, aws_access_key: str, aws_secret: str, distribution_id: str):
        self.aws_access_key = aws_access_key
        self.aws_secret = aws_secret
        self.distribution_id = distribution_id
    
    def get_stream_url(self, video_id: str, quality: str, user_location: str) -> str:
        return f"https://{self.distribution_id}.cloudfront.net/{video_id}/{quality}.m3u8"
    
    def get_available_qualities(self, video_id: str) -> List[str]:
        return ["360p", "480p", "720p", "1080p", "4K", "8K"]
    
    def get_bandwidth_cost(self, data_gb: float) -> float:
        return data_gb * 0.075  # $0.075 per GB
    
    def is_available_in_region(self, region: str) -> bool:
        return True  # Global coverage

class FastlyCDN(CDNProvider):
    """Fastly CDN implementation"""
    def __init__(self, service_id: str, api_token: str):
        self.service_id = service_id
        self.api_token = api_token
    
    def get_stream_url(self, video_id: str, quality: str, user_location: str) -> str:
        return f"https://fastly-global.com/{self.service_id}/stream/{video_id}?q={quality}"
    
    def get_available_qualities(self, video_id: str) -> List[str]:
        return ["240p", "480p", "720p", "1080p"]
    
    def get_bandwidth_cost(self, data_gb: float) -> float:
        return data_gb * 0.095  # $0.095 per GB
    
    def is_available_in_region(self, region: str) -> bool:
        return region in ["US", "EU", "CA"]

class GoogleAnalytics(VideoAnalytics):
    """Google Analytics implementation"""
    def __init__(self, tracking_id: str):
        self.tracking_id = tracking_id
    
    def track_stream_start(self, user_id: str, video_id: str, quality: str) -> None:
        print(f"GA: Stream started - User: {user_id}, Video: {video_id}, Quality: {quality}")
    
    def track_buffering_event(self, user_id: str, video_id: str, buffer_time: float) -> None:
        print(f"GA: Buffering - User: {user_id}, Video: {video_id}, Time: {buffer_time}s")

class MixpanelAnalytics(VideoAnalytics):
    """Mixpanel implementation"""
    def __init__(self, project_token: str):
        self.project_token = project_token
    
    def track_stream_start(self, user_id: str, video_id: str, quality: str) -> None:
        print(f"Mixpanel: Video Play - {user_id} watched {video_id} in {quality}")
    
    def track_buffering_event(self, user_id: str, video_id: str, buffer_time: float) -> None:
        print(f"Mixpanel: Buffer Event - {user_id} buffered {buffer_time}s on {video_id}")

# HIGH-LEVEL MODULE (Business Logic)
class VideoStreamingService:
    """
    HIGH-LEVEL MODULE following DIP
    CRITICAL INSIGHTS:
    1. Business logic owns the abstractions (CDNProvider, VideoAnalytics)
    2. Can switch CDNs without changing streaming logic
    3. Can implement intelligent failover between CDNs
    4. Easy to test with mock implementations
    5. Can optimize costs by choosing cheapest CDN per region
    """
    def __init__(self, primary_cdn: CDNProvider, backup_cdn: CDNProvider, 
                 analytics: VideoAnalytics):
        self._primary_cdn = primary_cdn
        self._backup_cdn = backup_cdn
        self._analytics = analytics
    
    def stream_video(self, user_id: str, video_id: str, user_location: str, 
                    preferred_quality: str = "1080p") -> Dict[str, Any]:
        """Smart streaming with CDN failover and cost optimization"""
        
        # Try primary CDN first
        if self._primary_cdn.is_available_in_region(user_location):
            try:
                available_qualities = self._primary_cdn.get_available_qualities(video_id)
                quality = preferred_quality if preferred_quality in available_qualities else available_qualities[-1]
                stream_url = self._primary_cdn.get_stream_url(video_id, quality, user_location)
                
                self._analytics.track_stream_start(user_id, video_id, quality)
                
                return {
                    "success": True,
                    "stream_url": stream_url,
                    "quality": quality,
                    "cdn_provider": self._primary_cdn.__class__.__name__,
                    "backup_available": True
                }
            except Exception as e:
                print(f"Primary CDN failed: {e}")
        
        # Fallback to backup CDN
        if self._backup_cdn.is_available_in_region(user_location):
            available_qualities = self._backup_cdn.get_available_qualities(video_id)
            quality = preferred_quality if preferred_quality in available_qualities else available_qualities[-1]
            stream_url = self._backup_cdn.get_stream_url(video_id, quality, user_location)
            
            self._analytics.track_stream_start(user_id, video_id, quality)
            
            return {
                "success": True,
                "stream_url": stream_url,
                "quality": quality,
                "cdn_provider": self._backup_cdn.__class__.__name__,
                "using_backup": True
            }
        
        return {"success": False, "error": "No CDN available in region"}
    
    def get_cost_optimized_streaming(self, video_id: str, estimated_gb: float) -> Dict[str, Any]:
        """Choose CDN based on cost optimization"""
        primary_cost = self._primary_cdn.get_bandwidth_cost(estimated_gb)
        backup_cost = self._backup_cdn.get_bandwidth_cost(estimated_gb)
        
        cheaper_cdn = self._primary_cdn if primary_cost <= backup_cost else self._backup_cdn
        savings = abs(primary_cost - backup_cost)
        
        return {
            "recommended_cdn": cheaper_cdn.__class__.__name__,
            "cost": min(primary_cost, backup_cost),
            "savings": savings,
            "comparison": {
                "primary": {"provider": self._primary_cdn.__class__.__name__, "cost": primary_cost},
                "backup": {"provider": self._backup_cdn.__class__.__name__, "cost": backup_cost}
            }
        }

# ============================================
# EXAMPLE 2: UBER/LYFT - PAYMENT PROCESSING
# Critical Insight: Ride business logic shouldn't depend on specific payment providers
# ============================================

"""
REAL-WORLD CONTEXT: Uber accepts credit cards, PayPal, Apple Pay, Google Pay, etc.
BUSINESS PROBLEM: Need to support multiple payment methods and processors
CRITICAL INSIGHT: Ride completion logic shouldn't change when adding new payment methods
"""

class PaymentMethod(ABC):
    """Abstraction for different payment methods"""
    @abstractmethod
    def process_payment(self, amount: float, metadata: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def is_available_in_country(self, country_code: str) -> bool:
        pass
    
    @abstractmethod
    def get_processing_fee(self, amount: float) -> float:
        pass

class FraudDetection(ABC):
    """Abstraction for fraud detection"""
    @abstractmethod
    def check_transaction(self, user_id: str, amount: float, location: str) -> Dict[str, Any]:
        pass

# LOW-LEVEL IMPLEMENTATIONS
class StripePayment(PaymentMethod):
    """Stripe payment processor"""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def process_payment(self, amount: float, metadata: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Stripe: Processing ${amount} payment")
        return {
            "success": True,
            "transaction_id": f"stripe_{uuid.uuid4()}",
            "amount": amount,
            "fee": self.get_processing_fee(amount)
        }
    
    def refund_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        print(f"Stripe: Refunding ${amount} for {transaction_id}")
        return {"success": True, "refund_id": f"refund_{uuid.uuid4()}"}
    
    def is_available_in_country(self, country_code: str) -> bool:
        return country_code in ["US", "CA", "GB", "AU", "DE", "FR"]
    
    def get_processing_fee(self, amount: float) -> float:
        return amount * 0.029 + 0.30  # 2.9% + $0.30

class PayPalPayment(PaymentMethod):
    """PayPal payment processor"""
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
    
    def process_payment(self, amount: float, metadata: Dict[str, Any]) -> Dict[str, Any]:
        print(f"PayPal: Processing ${amount} payment")
        return {
            "success": True,
            "transaction_id": f"paypal_{uuid.uuid4()}",
            "amount": amount,
            "fee": self.get_processing_fee(amount)
        }
    
    def refund_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        print(f"PayPal: Refunding ${amount} for {transaction_id}")
        return {"success": True, "refund_id": f"pp_refund_{uuid.uuid4()}"}
    
    def is_available_in_country(self, country_code: str) -> bool:
        return True  # PayPal available globally
    
    def get_processing_fee(self, amount: float) -> float:
        return amount * 0.0349  # 3.49% for PayPal

class ApplePayment(PaymentMethod):
    """Apple Pay processor"""
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
    
    def process_payment(self, amount: float, metadata: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Apple Pay: Processing ${amount} payment")
        return {
            "success": True,
            "transaction_id": f"apple_{uuid.uuid4()}",
            "amount": amount,
            "fee": self.get_processing_fee(amount)
        }
    
    def refund_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        print(f"Apple Pay: Refunding ${amount} for {transaction_id}")
        return {"success": True, "refund_id": f"apple_refund_{uuid.uuid4()}"}
    
    def is_available_in_country(self, country_code: str) -> bool:
        return country_code in ["US", "CA", "GB", "AU", "JP", "CN"]
    
    def get_processing_fee(self, amount: float) -> float:
        return amount * 0.025  # 2.5% for Apple Pay

class SiftFraudDetection(FraudDetection):
    """Sift fraud detection service"""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def check_transaction(self, user_id: str, amount: float, location: str) -> Dict[str, Any]:
        print(f"Sift: Checking fraud for user {user_id}, amount ${amount}")
        # Simulate fraud check
        risk_score = 0.15 if amount < 100 else 0.35
        return {
            "risk_score": risk_score,
            "is_safe": risk_score < 0.5,
            "recommendations": ["verify_location"] if risk_score > 0.3 else []
        }

# HIGH-LEVEL MODULE
class RidePaymentService:
    """
    HIGH-LEVEL MODULE following DIP
    CRITICAL INSIGHTS:
    1. Ride completion logic doesn't depend on specific payment processors
    2. Can easily add new payment methods (Venmo, Bitcoin, etc.)
    3. Can implement payment method selection based on fees
    4. Easy to test with mock payment processors
    5. Can handle payment failures gracefully with alternatives
    """
    def __init__(self, payment_methods: List[PaymentMethod], fraud_detector: FraudDetection):
        self._payment_methods = payment_methods
        self._fraud_detector = fraud_detector
    
    def complete_ride_payment(self, user_id: str, ride_amount: float, user_country: str,
                            user_location: str, preferred_method_index: int = 0) -> Dict[str, Any]:
        """Process ride payment with fraud detection and fallback methods"""
        
        # Fraud check first
        fraud_check = self._fraud_detector.check_transaction(user_id, ride_amount, user_location)
        if not fraud_check["is_safe"]:
            return {
                "success": False,
                "error": "Transaction flagged as high risk",
                "risk_score": fraud_check["risk_score"]
            }
        
        # Find available payment methods for user's country
        available_methods = [
            method for method in self._payment_methods 
            if method.is_available_in_country(user_country)
        ]
        
        if not available_methods:
            return {"success": False, "error": "No payment methods available in country"}
        
        # Try preferred method first, then fallback to others
        methods_to_try = available_methods[preferred_method_index:] + available_methods[:preferred_method_index]
        
        for method in methods_to_try:
            try:
                result = method.process_payment(ride_amount, {
                    "user_id": user_id,
                    "ride_type": "standard",
                    "location": user_location
                })
                
                if result["success"]:
                    return {
                        "success": True,
                        "transaction_id": result["transaction_id"],
                        "amount_charged": ride_amount,
                        "processing_fee": result["fee"],
                        "payment_method": method.__class__.__name__,
                        "fraud_check_passed": True
                    }
            except Exception as e:
                print(f"Payment failed with {method.__class__.__name__}: {e}")
                continue
        
        return {"success": False, "error": "All payment methods failed"}
    
    def get_cheapest_payment_method(self, amount: float, country: str) -> Dict[str, Any]:
        """Find the payment method with lowest fees"""
        available_methods = [
            method for method in self._payment_methods 
            if method.is_available_in_country(country)
        ]
        
        if not available_methods:
            return {"error": "No payment methods available"}
        
        costs = []
        for method in available_methods:
            fee = method.get_processing_fee(amount)
            costs.append({
                "method": method.__class__.__name__,
                "fee": fee,
                "total_cost": amount + fee,
                "percentage": (fee / amount) * 100
            })
        
        cheapest = min(costs, key=lambda x: x["fee"])
        
        return {
            "recommended_method": cheapest["method"],
            "savings_breakdown": costs,
            "potential_savings": max(costs, key=lambda x: x["fee"])["fee"] - cheapest["fee"]
        }

# ============================================
# EXAMPLE 3: GITHUB/GITLAB - SOURCE CODE HOSTING
# Critical Insight: Git operations shouldn't depend on specific storage backends
# ============================================

"""
REAL-WORLD CONTEXT: GitHub stores repositories in various backends (filesystem, AWS S3, etc.)
BUSINESS PROBLEM: Need to migrate between storage systems without breaking Git operations
CRITICAL INSIGHT: Repository operations should work regardless of storage implementation
"""

class RepositoryStorage(ABC):
    """Abstraction for repository storage"""
    @abstractmethod
    def store_repository(self, repo_id: str, repo_data: bytes) -> bool:
        pass
    
    @abstractmethod
    def retrieve_repository(self, repo_id: str) -> Optional[bytes]:
        pass
    
    @abstractmethod
    def delete_repository(self, repo_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_storage_stats(self, repo_id: str) -> Dict[str, Any]:
        pass

class BackupStrategy(ABC):
    """Abstraction for backup strategies"""
    @abstractmethod
    def backup_repository(self, repo_id: str, repo_data: bytes) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def restore_repository(self, repo_id: str, backup_id: str) -> Optional[bytes]:
        pass

# LOW-LEVEL IMPLEMENTATIONS
class FilesystemStorage(RepositoryStorage):
    """Local filesystem storage"""
    def __init__(self, base_path: str):
        self.base_path = base_path
    
    def store_repository(self, repo_id: str, repo_data: bytes) -> bool:
        print(f"Filesystem: Storing repo {repo_id} to {self.base_path}")
        return True
    
    def retrieve_repository(self, repo_id: str) -> Optional[bytes]:
        print(f"Filesystem: Retrieving repo {repo_id}")
        return b"mock_repo_data"
    
    def delete_repository(self, repo_id: str) -> bool:
        print(f"Filesystem: Deleting repo {repo_id}")
        return True
    
    def get_storage_stats(self, repo_id: str) -> Dict[str, Any]:
        return {"size_mb": 150, "last_accessed": datetime.now().isoformat()}

class S3Storage(RepositoryStorage):
    """AWS S3 storage"""
    def __init__(self, bucket_name: str, aws_access_key: str, aws_secret: str):
        self.bucket_name = bucket_name
        self.aws_access_key = aws_access_key
        self.aws_secret = aws_secret
    
    def store_repository(self, repo_id: str, repo_data: bytes) -> bool:
        print(f"S3: Storing repo {repo_id} to bucket {self.bucket_name}")
        return True
    
    def retrieve_repository(self, repo_id: str) -> Optional[bytes]:
        print(f"S3: Retrieving repo {repo_id} from bucket {self.bucket_name}")
        return b"s3_repo_data"
    
    def delete_repository(self, repo_id: str) -> bool:
        print(f"S3: Deleting repo {repo_id} from bucket {self.bucket_name}")
        return True
    
    def get_storage_stats(self, repo_id: str) -> Dict[str, Any]:
        return {"size_mb": 150, "storage_class": "STANDARD", "cost_per_month": 3.45}

class GitHubRepositoryService:
    """
    HIGH-LEVEL MODULE following DIP
    CRITICAL INSIGHTS:
    1. Repository management logic independent of storage backend
    2. Can migrate from filesystem to S3 without changing business logic
    3. Can implement hybrid storage strategies
    4. Easy to test with in-memory storage
    5. Can optimize storage costs by choosing appropriate backends
    """
    def __init__(self, primary_storage: RepositoryStorage, backup_storage: RepositoryStorage,
                 backup_strategy: BackupStrategy):
        self._primary_storage = primary_storage
        self._backup_storage = backup_storage
        self._backup_strategy = backup_strategy
    
    def create_repository(self, repo_id: str, initial_data: bytes) -> Dict[str, Any]:
        """Create repository with automatic backup"""
        
        # Store in primary storage
        primary_success = self._primary_storage.store_repository(repo_id, initial_data)
        if not primary_success:
            return {"success": False, "error": "Failed to store in primary storage"}
        
        # Create backup
        backup_result = self._backup_strategy.backup_repository(repo_id, initial_data)
        
        # Store in backup storage
        backup_success = self._backup_storage.store_repository(repo_id, initial_data)
        
        return {
            "success": True,
            "repo_id": repo_id,
            "primary_storage": self._primary_storage.__class__.__name__,
            "backup_storage": self._backup_storage.__class__.__name__,
            "backup_created": backup_success,
            "backup_id": backup_result.get("backup_id")
        }
    
    def migrate_repository_storage(self, repo_id: str, target_storage: RepositoryStorage) -> Dict[str, Any]:
        """Migrate repository between storage backends"""
        
        # Retrieve from current storage
        repo_data = self._primary_storage.retrieve_repository(repo_id)
        if not repo_data:
            return {"success": False, "error": "Repository not found"}
        
        # Store in target storage
        migration_success = target_storage.store_repository(repo_id, repo_data)
        if not migration_success:
            return {"success": False, "error": "Failed to migrate to target storage"}
        
        # Update primary storage reference
        old_storage = self._primary_storage.__class__.__name__
        self._primary_storage = target_storage
        
        return {
            "success": True,
            "repo_id": repo_id,
            "migrated_from": old_storage,
            "migrated_to": target_storage.__class__.__name__,
            "data_size": len(repo_data)
        }

# ============================================
# DEMONSTRATION AND CRITICAL INSIGHTS
# ============================================

def demonstrate_real_world_dip():
    """Demonstrate real-world DIP examples"""
    print("=== REAL-WORLD DEPENDENCY INVERSION PRINCIPLE ===\n")
    
    # EXAMPLE 1: Video Streaming (Netflix-style)
    print("1. VIDEO STREAMING PLATFORM (Netflix/YouTube style)")
    print("-" * 60)
    
    # Different CDN configurations for different regions
    akamai = AkamaiCDN("akamai_key", "us-east")
    cloudfront = CloudFrontCDN("aws_key", "aws_secret", "distribution123")
    analytics = GoogleAnalytics("GA-12345")
    
    streaming_service = VideoStreamingService(akamai, cloudfront, analytics)
    
    # Same business logic works with different CDN providers
    result = streaming_service.stream_video("user123", "video456", "US", "1080p")
    print(f"Streaming result: {result}\n")
    
    # Cost optimization across CDNs
    cost_analysis = streaming_service.get_cost_optimized_streaming("video456", 2.5)
    print(f"Cost optimization: {cost_analysis}\n")
    
    # EXAMPLE 2: Ride Payment Processing (Uber-style)
    print("2. RIDE PAYMENT PROCESSING (Uber/Lyft style)")
    print("-" * 55)
    
    # Multiple payment methods
    stripe = StripePayment("stripe_key")
    paypal = PayPalPayment("paypal_client", "paypal_secret")
    apple_pay = ApplePayment("merchant123")
    fraud_detector = SiftFraudDetection("sift_key")
    
    payment_service = RidePaymentService([stripe, paypal, apple_pay], fraud_detector)
    
    # Process ride payment with automatic fallback
    payment_result = payment_service.complete_ride_payment(
        "rider123", 25.50, "US", "San Francisco", preferred_method_index=0
    )
    print(f"Payment result: {payment_result}\n")
    
    # Find cheapest payment method
    cheapest = payment_service.get_cheapest_payment_method(25.50, "US")
    print(f"Cheapest payment method: {cheapest}\n")
    
    # EXAMPLE 3: Repository Storage (GitHub-style)
    print("3. SOURCE CODE REPOSITORY (GitHub/GitLab style)")
    print("-" * 52)
    
    # Different storage backends
    filesystem = FilesystemStorage("/repos")
    s3_storage = S3Storage("github-repos", "aws_key", "aws_secret")
    
    # Mock backup strategy
    class SimpleBackup(BackupStrategy):
        def backup_repository(self, repo_id: str, repo_data: bytes) -> Dict[str, Any]:
            return {"backup_id": f"backup_{uuid.uuid4()}", "timestamp": datetime.now().isoformat()}
        
        def restore_repository(self, repo_id: str, backup_id: str) -> Optional[bytes]:
            return b"restored_repo_data"
    
    backup_strategy = SimpleBackup()
    repo_service = GitHubRepositoryService(filesystem, s3_storage, backup_strategy)
    
    # Create repository
    create_result = repo_service.create_repository("my-awesome-project", b"initial_commit_data")
    print(f"Repository creation: {create_result}\n")
    
    # Migrate storage
    migration_result = repo_service.migrate_repository_storage("my-awesome-project", s3_storage)
    print(f"Storage migration: {migration_result}\n")

if __name__ == "__main__":
    demonstrate_real_world_dip()