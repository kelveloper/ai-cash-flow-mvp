import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import json
import os

class EnhancedCategorizationAnalytics:
    """
    Analytics service for tracking enhanced categorization performance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = defaultdict(list)
        self.daily_stats = defaultdict(dict)
        
        # Ensure analytics directory exists
        os.makedirs('analytics', exist_ok=True)
        
    def track_categorization_request(
        self, 
        description: str,
        source: str,
        category: str,
        confidence: float,
        response_time_ms: float,
        success: bool = True,
        error: str = None
    ):
        """Track a single categorization request"""
        
        timestamp = datetime.now().isoformat()
        
        metric = {
            'timestamp': timestamp,
            'description_length': len(description),
            'source': source,  # 'genify_api', 'local_ml', 'fallback'
            'category': category,
            'confidence': confidence,
            'response_time_ms': response_time_ms,
            'success': success,
            'error': error
        }
        
        self.metrics['categorizations'].append(metric)
        self._update_daily_stats(metric)
        
        # Log significant events
        if not success:
            self.logger.warning(f"Categorization failed: {error}")
        elif source == 'genify_api' and confidence > 0.95:
            self.logger.info(f"High-confidence enhanced categorization: {category} ({confidence:.2f})")
        elif source == 'fallback':
            self.logger.warning(f"Fallback categorization used for: {description[:50]}...")

    def track_user_correction(
        self,
        original_description: str,
        ai_prediction: str,
        user_correction: str,
        confidence: float,
        source: str
    ):
        """Track when a user corrects an AI categorization"""
        
        correction = {
            'timestamp': datetime.now().isoformat(),
            'description': original_description,
            'ai_prediction': ai_prediction,
            'user_correction': user_correction,
            'was_correct': ai_prediction.lower() == user_correction.lower(),
            'confidence': confidence,
            'source': source
        }
        
        self.metrics['corrections'].append(correction)
        
        # Log correction for learning
        self.logger.info(f"User correction: {ai_prediction} → {user_correction} (confidence: {confidence})")

    def track_api_performance(
        self,
        api_name: str,
        endpoint: str,
        response_time_ms: float,
        status_code: int,
        success: bool
    ):
        """Track API performance metrics"""
        
        performance = {
            'timestamp': datetime.now().isoformat(),
            'api_name': api_name,
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'status_code': status_code,
            'success': success
        }
        
        self.metrics['api_performance'].append(performance)

    def get_accuracy_report(self, days: int = 7) -> Dict:
        """Generate accuracy report for the last N days"""
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_corrections = [
            c for c in self.metrics['corrections']
            if datetime.fromisoformat(c['timestamp']) > cutoff
        ]
        
        if not recent_corrections:
            return {'error': 'No correction data available'}
        
        total_corrections = len(recent_corrections)
        correct_predictions = sum(1 for c in recent_corrections if c['was_correct'])
        
        # Accuracy by source
        source_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
        for correction in recent_corrections:
            source = correction['source']
            source_stats[source]['total'] += 1
            if correction['was_correct']:
                source_stats[source]['correct'] += 1
        
        # Calculate accuracy percentages
        for source in source_stats:
            total = source_stats[source]['total']
            correct = source_stats[source]['correct']
            source_stats[source]['accuracy'] = (correct / total * 100) if total > 0 else 0
        
        return {
            'period_days': days,
            'total_corrections': total_corrections,
            'overall_accuracy': (correct_predictions / total_corrections * 100) if total_corrections > 0 else 0,
            'accuracy_by_source': dict(source_stats),
            'improvement_opportunities': self._get_improvement_opportunities(recent_corrections)
        }

    def get_performance_report(self, days: int = 7) -> Dict:
        """Generate API performance report"""
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_categorizations = [
            c for c in self.metrics['categorizations']
            if datetime.fromisoformat(c['timestamp']) > cutoff
        ]
        
        if not recent_categorizations:
            return {'error': 'No categorization data available'}
        
        # Response time statistics
        response_times = [c['response_time_ms'] for c in recent_categorizations if c['success']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Success rate by source
        source_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'avg_response_time': 0})
        for cat in recent_categorizations:
            source = cat['source']
            source_stats[source]['total'] += 1
            if cat['success']:
                source_stats[source]['success'] += 1
                source_stats[source]['avg_response_time'] += cat['response_time_ms']
        
        # Calculate averages
        for source in source_stats:
            if source_stats[source]['success'] > 0:
                source_stats[source]['avg_response_time'] /= source_stats[source]['success']
            source_stats[source]['success_rate'] = (
                source_stats[source]['success'] / source_stats[source]['total'] * 100
                if source_stats[source]['total'] > 0 else 0
            )
        
        return {
            'period_days': days,
            'total_requests': len(recent_categorizations),
            'avg_response_time_ms': avg_response_time,
            'performance_by_source': dict(source_stats),
            'uptime_percentage': self._calculate_uptime(recent_categorizations)
        }

    def get_business_impact_report(self, days: int = 30) -> Dict:
        """Generate business impact metrics"""
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_categorizations = [
            c for c in self.metrics['categorizations']
            if datetime.fromisoformat(c['timestamp']) > cutoff
        ]
        
        if not recent_categorizations:
            return {'error': 'No data available for business impact analysis'}
        
        # Calculate enhanced AI usage
        enhanced_count = sum(1 for c in recent_categorizations if c['source'] == 'genify_api')
        total_count = len(recent_categorizations)
        enhanced_percentage = (enhanced_count / total_count * 100) if total_count > 0 else 0
        
        # Estimate cost savings (based on support query reduction)
        estimated_support_queries_prevented = enhanced_count * 0.35  # 35% reduction rate
        cost_savings_estimate = estimated_support_queries_prevented * 15  # $15 per support query
        
        # API costs estimate
        api_cost_estimate = enhanced_count * 0.025  # $0.025 per enhanced categorization
        
        return {
            'period_days': days,
            'total_categorizations': total_count,
            'enhanced_categorizations': enhanced_count,
            'enhanced_usage_percentage': enhanced_percentage,
            'estimated_support_queries_prevented': estimated_support_queries_prevented,
            'estimated_cost_savings': cost_savings_estimate,
            'estimated_api_costs': api_cost_estimate,
            'estimated_net_benefit': cost_savings_estimate - api_cost_estimate,
            'roi_percentage': ((cost_savings_estimate - api_cost_estimate) / api_cost_estimate * 100) 
                           if api_cost_estimate > 0 else 0
        }

    def export_analytics_data(self, output_file: str = None) -> str:
        """Export all analytics data to JSON file"""
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'analytics/categorization_analytics_{timestamp}.json'
        
        analytics_data = {
            'export_timestamp': datetime.now().isoformat(),
            'metrics': dict(self.metrics),
            'daily_stats': dict(self.daily_stats),
            'summary': {
                'total_categorizations': len(self.metrics['categorizations']),
                'total_corrections': len(self.metrics['corrections']),
                'data_retention_days': 30
            }
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(analytics_data, f, indent=2)
        
        self.logger.info(f"Analytics data exported to: {output_file}")
        return output_file

    def _update_daily_stats(self, metric: Dict):
        """Update daily aggregated statistics"""
        
        date_key = metric['timestamp'][:10]  # YYYY-MM-DD
        
        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = {
                'total_requests': 0,
                'successful_requests': 0,
                'enhanced_requests': 0,
                'avg_confidence': 0,
                'avg_response_time': 0,
                'source_breakdown': defaultdict(int)
            }
        
        day_stats = self.daily_stats[date_key]
        day_stats['total_requests'] += 1
        
        if metric['success']:
            day_stats['successful_requests'] += 1
        
        if metric['source'] == 'genify_api':
            day_stats['enhanced_requests'] += 1
        
        day_stats['source_breakdown'][metric['source']] += 1
        
        # Update running averages
        total = day_stats['total_requests']
        day_stats['avg_confidence'] = (
            (day_stats['avg_confidence'] * (total - 1) + metric['confidence']) / total
        )
        day_stats['avg_response_time'] = (
            (day_stats['avg_response_time'] * (total - 1) + metric['response_time_ms']) / total
        )

    def _get_improvement_opportunities(self, corrections: List[Dict]) -> List[str]:
        """Identify areas for improvement based on correction patterns"""
        
        opportunities = []
        
        # Find categories with high correction rates
        category_corrections = defaultdict(int)
        category_totals = defaultdict(int)
        
        for correction in corrections:
            category = correction['ai_prediction']
            category_totals[category] += 1
            if not correction['was_correct']:
                category_corrections[category] += 1
        
        # Identify problematic categories
        for category, total in category_totals.items():
            if total >= 5:  # Only consider categories with enough data
                error_rate = category_corrections[category] / total
                if error_rate > 0.3:  # 30% error rate threshold
                    opportunities.append(
                        f"High error rate in '{category}' category ({error_rate:.1%} - {category_corrections[category]}/{total})"
                    )
        
        # Find low-confidence predictions that were wrong
        low_confidence_errors = [
            c for c in corrections 
            if not c['was_correct'] and c['confidence'] < 0.7
        ]
        
        if len(low_confidence_errors) > len(corrections) * 0.2:
            opportunities.append(
                f"Many low-confidence predictions are incorrect ({len(low_confidence_errors)} cases)"
            )
        
        return opportunities

    def _calculate_uptime(self, categorizations: List[Dict]) -> float:
        """Calculate system uptime percentage"""
        
        if not categorizations:
            return 0.0
        
        successful = sum(1 for c in categorizations if c['success'])
        return (successful / len(categorizations)) * 100

# Global analytics instance
analytics = EnhancedCategorizationAnalytics() 