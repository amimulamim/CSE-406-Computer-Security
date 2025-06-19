"""
Advanced Data Converter for Sophisticated Side-Channel Attacks
Converts complex multi-channel attack data into ML-ready format
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
import argparse
import sys
import os

class AdvancedDataConverter:
    def __init__(self, input_size: int = 1000):
        self.input_size = input_size
        
    def extract_prime_probe_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from Prime+Probe attack data"""
        if not data:
            return np.zeros(100)
            
        features = []
        
        # Statistical features
        probe_times = [item.get('probeTime', 0) for item in data]
        prime_times = [item.get('primeTime', 0) for item in data]
        timing_seeds = [item.get('timingSeed', 0) for item in data]
        
        if probe_times:
            features.extend([
                np.mean(probe_times),
                np.std(probe_times),
                np.median(probe_times),
                np.min(probe_times),
                np.max(probe_times),
                np.percentile(probe_times, 25),
                np.percentile(probe_times, 75),
            ])
        else:
            features.extend([0] * 7)
        
        # Prime timing features (new)
        if prime_times:
            features.extend([
                np.mean(prime_times),
                np.std(prime_times),
                np.median(prime_times),
            ])
        else:
            features.extend([0] * 3)
        
        # Timing seed variation (indicates browser activity correlation)
        if timing_seeds:
            features.extend([
                np.mean(timing_seeds),
                np.std(timing_seeds),
                np.var(timing_seeds),
            ])
        else:
            features.extend([0] * 3)
            
        # Access pattern features (fallback for old format)
        access_counts = [item.get('accessCount', 0) for item in data]
        if access_counts:
            features.extend([
                np.mean(access_counts),
                np.var(access_counts),
            ])
        else:
            features.extend([0, 0])
            
        # Temporal features (rate of change)
        if len(probe_times) > 1:
            diff = np.diff(probe_times)
            features.extend([
                np.mean(diff),
                np.std(diff),
                np.mean(np.abs(diff)),
            ])
        else:
            features.extend([0, 0, 0])
            
        # Frequency domain features (FFT coefficients)
        if len(probe_times) >= 8:
            fft = np.fft.fft(probe_times[:min(64, len(probe_times))])
            fft_magnitudes = np.abs(fft)[:10]  # First 10 frequency components
            features.extend(fft_magnitudes.tolist())
        else:
            features.extend([0] * 10)
            
        # Pad or truncate to fixed size
        if len(features) < 100:
            features.extend([0] * (100 - len(features)))
        else:
            features = features[:100]
            
        return np.array(features, dtype=np.float32)
    
    def extract_bus_contention_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from memory bus contention attack"""
        if not data:
            return np.zeros(50)
            
        features = []
        
        # Group by pattern type
        patterns = {0: [], 1: [], 2: []}
        for item in data:
            pattern = item.get('pattern', 0)
            time_val = item.get('time', 0)
            if pattern in patterns:
                patterns[pattern].append(time_val)
        
        # Extract pattern-specific features
        for pattern_id in [0, 1, 2]:
            times = patterns[pattern_id]
            if times:
                features.extend([
                    np.mean(times),
                    np.std(times),
                    np.median(times),
                    len(times),
                ])
            else:
                features.extend([0, 0, 0, 0])
        
        # Cross-pattern features
        all_times = [item.get('time', 0) for item in data]
        if all_times:
            features.extend([
                np.var(all_times),
                np.ptp(all_times),  # Peak-to-peak
                np.mean(np.abs(np.diff(all_times))) if len(all_times) > 1 else 0,
            ])
        else:
            features.extend([0, 0, 0])
        
        # Round-based consistency
        rounds = set(item.get('round', 0) for item in data)
        features.append(len(rounds))
        
        # Checksum entropy (as a measure of randomness)
        checksums = [item.get('checksum', 0) for item in data]
        if checksums:
            unique_checksums = len(set(checksums))
            features.append(unique_checksums / len(checksums) if checksums else 0)
        else:
            features.append(0)
            
        # Pad or truncate
        if len(features) < 50:
            features.extend([0] * (50 - len(features)))
        else:
            features = features[:50]
            
        return np.array(features, dtype=np.float32)
    
    def extract_cache_conflict_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from cache line conflict attack"""
        if not data:
            return np.zeros(75)
            
        features = []
        
        all_conflicts = []
        for round_data in data:
            conflicts = round_data.get('conflicts', [])
            all_conflicts.extend(conflicts)
        
        if all_conflicts:
            # Conflict timing features
            conflict_times = [c.get('conflictTime', 0) for c in all_conflicts]
            features.extend([
                np.mean(conflict_times),
                np.std(conflict_times),
                np.median(conflict_times),
                np.min(conflict_times),
                np.max(conflict_times),
            ])
            
            # Set distribution features
            sets = [c.get('set', 0) for c in all_conflicts]
            unique_sets = len(set(sets))
            features.extend([
                unique_sets,
                np.std(sets) if sets else 0,
            ])
            
            # Address count features
            addr_counts = [c.get('addressCount', 0) for c in all_conflicts]
            features.extend([
                np.mean(addr_counts),
                np.std(addr_counts),
            ])
            
            # Conflict intensity (conflicts per round)
            rounds_with_conflicts = len([r for r in data if r.get('conflicts')])
            features.append(len(all_conflicts) / max(1, rounds_with_conflicts))
            
        else:
            features.extend([0] * 10)
        
        # Temporal consistency
        round_conflict_counts = [len(r.get('conflicts', [])) for r in data]
        if round_conflict_counts:
            features.extend([
                np.mean(round_conflict_counts),
                np.std(round_conflict_counts),
                np.max(round_conflict_counts),
            ])
        else:
            features.extend([0, 0, 0])
            
        # Pad or truncate
        while len(features) < 75:
            features.append(0)
        features = features[:75]
            
        return np.array(features, dtype=np.float32)
    
    def extract_timing_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from microarchitectural timing attack"""
        if not data:
            return np.zeros(60)
            
        features = []
        
        # Collect all timing data
        all_timings = []
        for round_data in data:
            timings = round_data.get('timings', [])
            for timing_set in timings:
                for op_timing in timing_set:
                    all_timings.append(op_timing.get('time', 0))
        
        if all_timings:
            # Basic statistical features
            features.extend([
                np.mean(all_timings),
                np.std(all_timings),
                np.median(all_timings),
                np.min(all_timings),
                np.max(all_timings),
                np.percentile(all_timings, 95),
                np.percentile(all_timings, 5),
            ])
            
            # Distribution shape
            features.extend([
                np.var(all_timings),
                np.ptp(all_timings),
                len(set(np.round(all_timings, 3))),  # Unique timing values
            ])
            
            # Temporal patterns
            if len(all_timings) > 1:
                autocorr = np.correlate(all_timings, all_timings, mode='full')
                features.append(np.max(autocorr))
            else:
                features.append(0)
                
        else:
            features.extend([0] * 11)
        
        # Operation-specific analysis
        op_types = [0, 1, 2]  # FPU, ALU, Memory
        for op_type in op_types:
            op_timings = []
            for round_data in data:
                timings = round_data.get('timings', [])
                for timing_set in timings:
                    if op_type < len(timing_set):
                        op_timings.append(timing_set[op_type].get('time', 0))
            
            if op_timings:
                features.extend([
                    np.mean(op_timings),
                    np.std(op_timings),
                    np.median(op_timings),
                ])
            else:
                features.extend([0, 0, 0])
        
        # Cross-operation correlations
        if len(data) > 0:
            round_means = []
            for round_data in data:
                timings = round_data.get('timings', [])
                if timings:
                    round_total = sum(sum(op.get('time', 0) for op in timing_set) 
                                    for timing_set in timings)
                    round_means.append(round_total)
            
            if len(round_means) > 1:
                features.extend([
                    np.std(round_means),
                    np.mean(round_means),
                ])
            else:
                features.extend([0, 0])
        else:
            features.extend([0, 0])
            
        # Pad or truncate
        while len(features) < 60:
            features.append(0)
        features = features[:60]
            
        return np.array(features, dtype=np.float32)
    
    def extract_branch_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from branch predictor attack"""
        if not data:
            return np.zeros(40)
            
        features = []
        
        # Pattern-specific features
        pattern_features = {0: [], 1: [], 2: []}
        
        for round_data in data:
            branches = round_data.get('branches', [])
            for branch in branches:
                pattern = branch.get('pattern', 0)
                time_val = branch.get('time', 0)
                if pattern in pattern_features:
                    pattern_features[pattern].append(time_val)
        
        # Extract features for each pattern
        for pattern_id in [0, 1, 2]:
            times = pattern_features[pattern_id]
            if times:
                features.extend([
                    np.mean(times),
                    np.std(times),
                    np.min(times),
                    np.max(times),
                ])
            else:
                features.extend([0, 0, 0, 0])
        
        # Cross-pattern analysis
        all_times = []
        for times_list in pattern_features.values():
            all_times.extend(times_list)
        
        if all_times:
            features.extend([
                np.var(all_times),
                np.mean(all_times),
                len(set(np.round(all_times, 3))),  # Timing precision
            ])
        else:
            features.extend([0, 0, 0])
        
        # Branch count analysis
        all_branch_counts = []
        for round_data in data:
            branches = round_data.get('branches', [])
            for branch in branches:
                all_branch_counts.append(branch.get('branchCount', 0))
        
        if all_branch_counts:
            features.extend([
                np.mean(all_branch_counts),
                np.std(all_branch_counts),
                np.sum(all_branch_counts),
            ])
        else:
            features.extend([0, 0, 0])
        
        # Predictability metrics
        if len(all_times) > 2:
            # Coefficient of variation as predictability measure
            cv = np.std(all_times) / np.mean(all_times) if np.mean(all_times) > 0 else 0
            features.append(cv)
        else:
            features.append(0)
            
        # Pad or truncate
        while len(features) < 40:
            features.append(0)
        features = features[:40]
            
        return np.array(features, dtype=np.float32)
    
    def extract_tlb_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from TLB attack"""
        if not data:
            return np.zeros(45)
            
        features = []
        
        # Pattern-specific analysis
        pattern_stats = {'sequential': [], 'strided': [], 'random': []}
        
        for round_data in data:
            tlb_data = round_data.get('tlb', [])
            for tlb_measurement in tlb_data:
                pattern = tlb_measurement.get('pattern', '')
                time_val = tlb_measurement.get('time', 0)
                if pattern in pattern_stats:
                    pattern_stats[pattern].append(time_val)
        
        # Extract features for each pattern
        for pattern_name in ['sequential', 'strided', 'random']:
            times = pattern_stats[pattern_name]
            if times:
                features.extend([
                    np.mean(times),
                    np.std(times),
                    np.median(times),
                    np.min(times),
                    np.max(times),
                ])
            else:
                features.extend([0, 0, 0, 0, 0])
        
        # Cross-pattern relationships
        all_pattern_times = []
        for times_list in pattern_stats.values():
            all_pattern_times.extend(times_list)
        
        if all_pattern_times:
            features.extend([
                np.var(all_pattern_times),
                np.ptp(all_pattern_times),
                len(all_pattern_times),
            ])
        else:
            features.extend([0, 0, 0])
        
        # Access count analysis
        all_access_counts = []
        for round_data in data:
            tlb_data = round_data.get('tlb', [])
            for tlb_measurement in tlb_data:
                all_access_counts.append(tlb_measurement.get('accessCount', 0))
        
        if all_access_counts:
            features.extend([
                np.mean(all_access_counts),
                np.std(all_access_counts),
                np.sum(all_access_counts),
            ])
        else:
            features.extend([0, 0, 0])
        
        # TLB pressure metric (time per access)
        for pattern_name in ['sequential', 'strided', 'random']:
            times = pattern_stats[pattern_name]
            if times:
                # Assuming roughly equal access counts, time variance indicates TLB pressure
                features.append(np.std(times) / np.mean(times) if np.mean(times) > 0 else 0)
            else:
                features.append(0)
                
        # Pad or truncate
        while len(features) < 45:
            features.append(0)
        features = features[:45]
            
        return np.array(features, dtype=np.float32)
    
    def extract_legacy_features(self, data: List[float]) -> np.ndarray:
        """Extract features from legacy sweep attack for compatibility"""
        if not data:
            return np.zeros(100)
            
        # Convert to numpy array
        sweep_data = np.array(data, dtype=np.float32)
        
        # Basic statistical features
        features = [
            np.mean(sweep_data),
            np.std(sweep_data),
            np.median(sweep_data),
            np.min(sweep_data),
            np.max(sweep_data),
            np.percentile(sweep_data, 25),
            np.percentile(sweep_data, 75),
            np.var(sweep_data),
            np.ptp(sweep_data),
        ]
        
        # Temporal features
        if len(sweep_data) > 1:
            diff = np.diff(sweep_data)
            features.extend([
                np.mean(diff),
                np.std(diff),
                np.mean(np.abs(diff)),
                np.max(np.abs(diff)),
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # Frequency domain features
        if len(sweep_data) >= 8:
            # Use first power of 2 <= length for FFT
            n = 2 ** int(np.log2(len(sweep_data)))
            fft = np.fft.fft(sweep_data[:n])
            fft_magnitudes = np.abs(fft)[:min(20, n//2)]
            features.extend(fft_magnitudes.tolist())
        else:
            features.extend([0] * 20)
        
        # Statistical moments
        if len(sweep_data) > 0:
            # Skewness approximation
            mean_val = np.mean(sweep_data)
            std_val = np.std(sweep_data)
            if std_val > 0:
                skewness = np.mean(((sweep_data - mean_val) / std_val) ** 3)
                kurtosis = np.mean(((sweep_data - mean_val) / std_val) ** 4)
            else:
                skewness = 0
                kurtosis = 0
            features.extend([skewness, kurtosis])
        else:
            features.extend([0, 0])
        
        # Trend features
        if len(sweep_data) > 2:
            # Simple linear trend
            x = np.arange(len(sweep_data))
            slope = np.polyfit(x, sweep_data, 1)[0]
            features.append(slope)
        else:
            features.append(0)
        
        # Autocorrelation
        if len(sweep_data) > 4:
            autocorr = np.correlate(sweep_data, sweep_data, mode='full')
            features.append(np.max(autocorr))
        else:
            features.append(0)
            
        # Pad or truncate to fixed size
        while len(features) < 100:
            features.append(0)
        features = features[:100]
        
        return np.array(features, dtype=np.float32)
    
    def extract_browser_activity_features(self, data: List[Dict]) -> np.ndarray:
        """Extract features from browser activity correlation measurements"""
        if not data:
            return np.zeros(70)
            
        features = []
        
        # Memory allocation timing features
        mem_alloc_times = [item.get('memAlloc', 0) for item in data]
        if mem_alloc_times:
            features.extend([
                np.mean(mem_alloc_times),
                np.std(mem_alloc_times),
                np.median(mem_alloc_times),
                np.min(mem_alloc_times),
                np.max(mem_alloc_times),
            ])
        else:
            features.extend([0] * 5)
        
        # DOM complexity features
        dom_elements = [item.get('domQuery', {}).get('elements', 0) for item in data]
        dom_links = [item.get('domQuery', {}).get('links', 0) for item in data]
        dom_scripts = [item.get('domQuery', {}).get('scripts', 0) for item in data]
        dom_times = [item.get('domQuery', {}).get('queryTime', 0) for item in data]
        
        features.extend([
            np.mean(dom_elements) if dom_elements else 0,
            np.mean(dom_links) if dom_links else 0,
            np.mean(dom_scripts) if dom_scripts else 0,
            np.mean(dom_times) if dom_times else 0,
            np.std(dom_times) if dom_times else 0,
        ])
        
        # JavaScript execution timing
        js_exec_times = [item.get('jsExec', {}).get('execTime', 0) for item in data]
        if js_exec_times:
            features.extend([
                np.mean(js_exec_times),
                np.std(js_exec_times),
                np.var(js_exec_times),
            ])
        else:
            features.extend([0] * 3)
        
        # Resource timing features
        resource_counts = [item.get('resourceTiming', {}).get('count', 0) for item in data]
        resource_times = [item.get('resourceTiming', {}).get('avgLoadTime', 0) for item in data]
        
        features.extend([
            np.mean(resource_counts) if resource_counts else 0,
            np.std(resource_counts) if resource_counts else 0,
            np.mean(resource_times) if resource_times else 0,
            np.std(resource_times) if resource_times else 0,
        ])
        
        # Total timing correlations
        total_times = [item.get('totalTime', 0) for item in data]
        if total_times:
            features.extend([
                np.mean(total_times),
                np.std(total_times),
                np.median(total_times),
                np.percentile(total_times, 25),
                np.percentile(total_times, 75),
            ])
        else:
            features.extend([0] * 5)
        
        # Temporal correlations
        timestamps = [item.get('timestamp', 0) for item in data]
        if len(timestamps) > 1:
            # Rate of change in measurements
            time_diffs = np.diff(timestamps)
            features.extend([
                np.mean(time_diffs),
                np.std(time_diffs),
                np.min(time_diffs),
                np.max(time_diffs),
            ])
        else:
            features.extend([0] * 4)
        
        # Cross-correlation features between different timing measurements
        if len(mem_alloc_times) > 1 and len(js_exec_times) > 1:
            correlation = np.corrcoef(mem_alloc_times[:len(js_exec_times)], js_exec_times[:len(mem_alloc_times)])[0, 1]
            features.append(correlation if not np.isnan(correlation) else 0)
        else:
            features.append(0)
        
        # Variability indicators
        all_timing_data = mem_alloc_times + js_exec_times + dom_times + total_times
        if all_timing_data:
            features.extend([
                np.var(all_timing_data),
                len(set(all_timing_data[:10])),  # Unique value count
            ])
        else:
            features.extend([0, 0])
        
        # Pad or truncate to 70 features
        if len(features) < 70:
            features.extend([0] * (70 - len(features)))
        else:
            features = features[:70]
        
        return np.array(features, dtype=np.float32)
    
    def convert_advanced_trace(self, trace_data: Dict[str, Any]) -> np.ndarray:
        """Convert a single advanced trace to feature vector"""
        features = []
        
        attacks = trace_data.get('attacks', {})
        
        # Extract features from each attack type
        features.extend(self.extract_prime_probe_features(attacks.get('primeProbe', [])))
        features.extend(self.extract_bus_contention_features(attacks.get('busContention', [])))
        features.extend(self.extract_cache_conflict_features(attacks.get('cacheConflict', [])))
        features.extend(self.extract_timing_features(attacks.get('timing', [])))
        features.extend(self.extract_branch_features(attacks.get('branch', [])))
        features.extend(self.extract_tlb_features(attacks.get('tlb', [])))
        features.extend(self.extract_legacy_features(attacks.get('legacy', [])))
        features.extend(self.extract_browser_activity_features(attacks.get('browserActivity', [])))
        
        # Total feature vector size: 100+50+75+60+40+45+100+70 = 540
        # We'll standardize to 1000 features to match INPUT_SIZE
        
        # Add system-level features if available
        system_info = trace_data.get('systemInfo', {})
        system_features = [
            system_info.get('hardwareConcurrency', 0),
            len(system_info.get('userAgent', '')),
            hash(system_info.get('userAgent', '')) % 1000,  # Browser fingerprint
        ]
        features.extend(system_features)
        
        # Add temporal features (normalized)
        timestamp = trace_data.get('timestamp', 0)
        if timestamp:
            # Time-based features (hour of day, etc.) - normalized to 0-1 range
            import datetime
            dt = datetime.datetime.fromtimestamp(timestamp / 1000)
            time_features = [
                dt.hour / 24.0,        # Normalize hour to 0-1
                dt.minute / 60.0,      # Normalize minute to 0-1  
                dt.second / 60.0,      # Normalize second to 0-1
                dt.weekday() / 7.0,    # Normalize weekday to 0-1
            ]
            features.extend(time_features)
        else:
            features.extend([0, 0, 0, 0])
        
        # Convert to numpy and pad/truncate to target size
        feature_vector = np.array(features, dtype=np.float32)
        
        # Apply more selective normalization instead of global scaling
        # Only normalize specific problematic features while preserving variation
        
        # Handle very large timestamp-like values by using modulo instead of full scaling
        large_value_threshold = 10000
        for i in range(len(feature_vector)):
            if abs(feature_vector[i]) > large_value_threshold:
                # Keep the variation but reduce the magnitude
                feature_vector[i] = feature_vector[i] % 1000
        
        # Apply gentle clipping to extreme outliers only
        feature_vector = np.clip(feature_vector, -10000, 10000)
        
        if len(feature_vector) < self.input_size:
            # Pad with zeros
            padding = np.zeros(self.input_size - len(feature_vector))
            feature_vector = np.concatenate([feature_vector, padding])
        elif len(feature_vector) > self.input_size:
            # Truncate
            feature_vector = feature_vector[:self.input_size]
        
        return feature_vector
    
    def convert_dataset(self, input_file: str, output_file: str):
        """Convert a dataset file with advanced traces"""
        print(f"Converting advanced dataset from {input_file} to {output_file}")
        
        # Load raw data
        with open(input_file, 'r') as f:
            raw_data = json.load(f)
        
        converted_data = []
        
        for item in raw_data:
            website = item.get('website', 'unknown')
            trace_data = item.get('trace_data', {})
            
            # Check if this is advanced trace data (dict) or legacy (list)
            if isinstance(trace_data, dict) and 'attacks' in trace_data:
                # Advanced multi-channel trace
                feature_vector = self.convert_advanced_trace(trace_data)
            elif isinstance(trace_data, list):
                # Legacy trace data - convert using legacy features
                feature_vector = self.extract_legacy_features(trace_data)
                # Pad to full size
                if len(feature_vector) < self.input_size:
                    padding = np.zeros(self.input_size - len(feature_vector))
                    feature_vector = np.concatenate([feature_vector, padding])
                elif len(feature_vector) > self.input_size:
                    feature_vector = feature_vector[:self.input_size]
            else:
                print(f"Warning: Unknown trace format for website {website}, skipping")
                continue
            
            converted_data.append({
                'website': website,
                'trace_data': feature_vector.tolist()
            })
        
        # Save converted data
        with open(output_file, 'w') as f:
            json.dump(converted_data, f, indent=2)
        
        print(f"Converted {len(converted_data)} traces")
        print(f"Feature vector size: {self.input_size}")
        
        # Print statistics
        if converted_data:
            websites = [item['website'] for item in converted_data]
            unique_websites = set(websites)
            print(f"Websites: {len(unique_websites)}")
            for website in unique_websites:
                count = websites.count(website)
                print(f"  - {website}: {count} traces")

def main():
    parser = argparse.ArgumentParser(description='Convert advanced side-channel attack data')
    parser.add_argument('input_file', help='Input JSON file with raw traces')
    parser.add_argument('output_file', help='Output JSON file with converted features')
    parser.add_argument('--input-size', type=int, default=1000, 
                       help='Target feature vector size (default: 1000)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} not found")
        sys.exit(1)
    
    converter = AdvancedDataConverter(input_size=args.input_size)
    converter.convert_dataset(args.input_file, args.output_file)
    
    print("Conversion complete!")

if __name__ == "__main__":
    main()
