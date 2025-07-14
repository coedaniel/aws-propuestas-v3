"""
Sistema de Monitoreo y Métricas para AWS Propuestas v3.2.1
Tracking de performance, errores y uso del sistema
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from functools import wraps
import boto3
from collections import defaultdict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SystemMonitor:
    def __init__(self):
        """Initialize monitoring system"""
        self.metrics = defaultdict(list)
        self.start_time = datetime.now()
        self.cloudwatch = None
        
        try:
            self.cloudwatch = boto3.client('cloudwatch')
            logger.info("✅ CLOUDWATCH CLIENT INITIALIZED")
        except Exception as e:
            logger.warning(f"⚠️ CLOUDWATCH NOT AVAILABLE: {str(e)}")
    
    def track_request(self, request_type: str, duration: float, success: bool, metadata: Dict[str, Any] = None):
        """Track request metrics"""
        try:
            metric_data = {
                'timestamp': datetime.now().isoformat(),
                'request_type': request_type,
                'duration': duration,
                'success': success,
                'metadata': metadata or {}
            }
            
            self.metrics[request_type].append(metric_data)
            
            # Log important metrics
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"📊 METRIC: {request_type} - {status} - {duration:.2f}s")
            
            # Send to CloudWatch if available
            if self.cloudwatch:
                self._send_to_cloudwatch(request_type, duration, success)
                
        except Exception as e:
            logger.error(f"❌ ERROR TRACKING METRIC: {str(e)}")
    
    def _send_to_cloudwatch(self, request_type: str, duration: float, success: bool):
        """Send metrics to CloudWatch"""
        try:
            namespace = 'AWS-Propuestas-v3'
            
            # Duration metric
            self.cloudwatch.put_metric_data(
                Namespace=namespace,
                MetricData=[
                    {
                        'MetricName': 'RequestDuration',
                        'Dimensions': [
                            {
                                'Name': 'RequestType',
                                'Value': request_type
                            }
                        ],
                        'Value': duration,
                        'Unit': 'Seconds',
                        'Timestamp': datetime.now()
                    }
                ]
            )
            
            # Success/failure metric
            self.cloudwatch.put_metric_data(
                Namespace=namespace,
                MetricData=[
                    {
                        'MetricName': 'RequestCount',
                        'Dimensions': [
                            {
                                'Name': 'RequestType',
                                'Value': request_type
                            },
                            {
                                'Name': 'Status',
                                'Value': 'Success' if success else 'Failure'
                            }
                        ],
                        'Value': 1,
                        'Unit': 'Count',
                        'Timestamp': datetime.now()
                    }
                ]
            )
            
        except Exception as e:
            logger.warning(f"⚠️ CLOUDWATCH METRIC FAILED: {str(e)}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        try:
            summary = {
                'system_uptime': str(datetime.now() - self.start_time),
                'total_requests': sum(len(requests) for requests in self.metrics.values()),
                'request_types': {},
                'overall_stats': {
                    'success_rate': 0,
                    'avg_duration': 0,
                    'total_errors': 0
                }
            }
            
            total_requests = 0
            total_successes = 0
            total_duration = 0
            total_errors = 0
            
            for request_type, requests in self.metrics.items():
                if not requests:
                    continue
                
                successes = sum(1 for r in requests if r['success'])
                failures = len(requests) - successes
                avg_duration = sum(r['duration'] for r in requests) / len(requests)
                
                summary['request_types'][request_type] = {
                    'total_requests': len(requests),
                    'successes': successes,
                    'failures': failures,
                    'success_rate': successes / len(requests) if requests else 0,
                    'avg_duration': avg_duration,
                    'last_request': requests[-1]['timestamp'] if requests else None
                }
                
                total_requests += len(requests)
                total_successes += successes
                total_duration += sum(r['duration'] for r in requests)
                total_errors += failures
            
            # Overall stats
            if total_requests > 0:
                summary['overall_stats'] = {
                    'success_rate': total_successes / total_requests,
                    'avg_duration': total_duration / total_requests,
                    'total_errors': total_errors,
                    'requests_per_minute': total_requests / max(1, (datetime.now() - self.start_time).total_seconds() / 60)
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ ERROR GETTING METRICS SUMMARY: {str(e)}")
            return {'error': str(e)}
    
    def track_document_generation(self, service: str, document_count: int, success: bool, duration: float):
        """Track document generation metrics"""
        metadata = {
            'service': service,
            'document_count': document_count
        }
        self.track_request('document_generation', duration, success, metadata)
    
    def track_s3_upload(self, service: str, file_count: int, success_count: int, duration: float):
        """Track S3 upload metrics"""
        metadata = {
            'service': service,
            'file_count': file_count,
            'success_count': success_count,
            'success_rate': success_count / file_count if file_count > 0 else 0
        }
        success = success_count == file_count
        self.track_request('s3_upload', duration, success, metadata)
    
    def track_ai_response(self, model: str, tokens: int, duration: float, success: bool):
        """Track AI response metrics"""
        metadata = {
            'model': model,
            'tokens': tokens,
            'tokens_per_second': tokens / duration if duration > 0 else 0
        }
        self.track_request('ai_response', duration, success, metadata)
    
    def get_health_check(self) -> Dict[str, Any]:
        """Get system health check"""
        try:
            metrics_summary = self.get_metrics_summary()
            
            # Determine health status
            overall_success_rate = metrics_summary.get('overall_stats', {}).get('success_rate', 0)
            total_errors = metrics_summary.get('overall_stats', {}).get('total_errors', 0)
            
            if overall_success_rate >= 0.95:
                health_status = 'healthy'
            elif overall_success_rate >= 0.8:
                health_status = 'warning'
            else:
                health_status = 'critical'
            
            health_check = {
                'status': health_status,
                'timestamp': datetime.now().isoformat(),
                'uptime': str(datetime.now() - self.start_time),
                'success_rate': overall_success_rate,
                'total_errors': total_errors,
                'version': '3.2.1',
                'cloudwatch_enabled': self.cloudwatch is not None
            }
            
            return health_check
            
        except Exception as e:
            logger.error(f"❌ ERROR IN HEALTH CHECK: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Global monitor instance
monitor = SystemMonitor()

def track_performance(request_type: str):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            result = None
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                logger.error(f"❌ ERROR IN {request_type}: {str(e)}")
                raise
            finally:
                duration = time.time() - start_time
                monitor.track_request(request_type, duration, success)
                
        return wrapper
    return decorator

def log_system_stats():
    """Log current system statistics"""
    try:
        stats = monitor.get_metrics_summary()
        logger.info(f"📊 SYSTEM STATS: {json.dumps(stats, indent=2)}")
    except Exception as e:
        logger.error(f"❌ ERROR LOGGING STATS: {str(e)}")

def get_monitoring_dashboard() -> Dict[str, Any]:
    """Get comprehensive monitoring dashboard data"""
    try:
        return {
            'health_check': monitor.get_health_check(),
            'metrics_summary': monitor.get_metrics_summary(),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ ERROR GETTING DASHBOARD: {str(e)}")
        return {'error': str(e)}
