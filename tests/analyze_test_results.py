"""
Testing Results Analyzer
Analyzes test results and generates comprehensive reports
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ResultsAnalyzer:
    """Analyzes testing results and generates reports"""
    
    def __init__(self, results_file: str):
        self.results_file = Path(results_file)
        
        if not self.results_file.exists():
            print(f"❌ Results file not found: {results_file}")
            return
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.stats = self.data.get('stats', {})
        self.results = self.data.get('results', [])
    
    def generate_report(self):
        """Generate comprehensive testing report"""
        report = []
        report.append("="*80)
        report.append("📊 COMPREHENSIVE TESTING REPORT")
        report.append("="*80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Session: {self.results_file.name}")
        report.append(f"\n{'='*80}\n")
        
        # Overall stats
        report.append("📈 OVERALL STATISTICS")
        report.append("-"*80)
        report.append(f"Total Resumes Tested: {self.stats.get('total_tested', 0)}")
        report.append("")
        
        # Component performance
        report.append("📋 COMPONENT PERFORMANCE")
        report.append("-"*80)
        
        components = self.stats.get('components', {})
        
        for component, data in components.items():
            total = data.get('total', 0)
            if total == 0:
                continue
            
            success = data.get('correct', data.get('success', data.get('acceptable', 0)))
            success_rate = (success / total) * 100
            
            status = "🟢 PASS" if success_rate >= 90 else "🟡 NEEDS WORK" if success_rate >= 75 else "🔴 CRITICAL"
            
            report.append(f"\n{component.replace('_', ' ').title()}")
            report.append(f"  Status: {status}")
            report.append(f"  Success Rate: {success_rate:.1f}% ({success}/{total})")
        
        report.append(f"\n{'='*80}\n")
        
        # Issue analysis
        report.append("🔍 ISSUE ANALYSIS")
        report.append("-"*80)
        
        issues = self.analyze_issues()
        
        if issues:
            for issue_type, count in issues.items():
                report.append(f"  {issue_type}: {count} occurrences")
        else:
            report.append("  No major issues found!")
        
        report.append(f"\n{'='*80}\n")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-"*80)
        
        recommendations = self.generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report.append(f"  {i}. {rec}")
        
        report.append(f"\n{'='*80}\n")
        
        # Detailed resume results
        report.append("📄 DETAILED RESULTS")
        report.append("-"*80)
        
        for i, result in enumerate(self.results, 1):
            report.append(f"\n{i}. {result.get('filename', 'Unknown')}")
            report.append(f"   Overall Rating: {result.get('overall_rating', 'N/A')}/5")
            
            if result.get('notes'):
                report.append(f"   Notes: {result['notes']}")
        
        report.append(f"\n{'='*80}")
        
        return "\n".join(report)
    
    def analyze_issues(self):
        """Analyze common issues across resumes"""
        issues = defaultdict(int)
        
        for result in self.results:
            components = result.get('components', {})
            
            # Check parsing issues
            parsing = components.get('parsing', {})
            if not parsing.get('success'):
                issues['Parsing failures'] += 1
            
            # Check personal info issues
            personal = components.get('personal_info', {})
            checks = personal.get('checks', {})
            for field, status in checks.items():
                if status == 'n':
                    issues[f'{field.title()} extraction errors'] += 1
            
            # Check skill quality
            skills = components.get('skills', {})
            if skills.get('quality_rating') in ['1', '2']:
                issues['Poor skill extraction'] += 1
            
            # Check experience quality
            experience = components.get('experience', {})
            if experience.get('quality_rating') in ['1', '2']:
                issues['Poor experience extraction'] += 1
            
            # Check education quality
            education = components.get('education', {})
            if education.get('quality_rating') in ['1', '2']:
                issues['Poor education extraction'] += 1
        
        return dict(sorted(issues.items(), key=lambda x: x[1], reverse=True))
    
    def generate_recommendations(self):
        """Generate improvement recommendations"""
        recommendations = []
        
        components = self.stats.get('components', {})
        
        for component, data in components.items():
            total = data.get('total', 0)
            if total == 0:
                continue
            
            success = data.get('correct', data.get('success', data.get('acceptable', 0)))
            success_rate = (success / total) * 100
            
            if success_rate < 75:
                recommendations.append(
                    f"🔴 CRITICAL: {component.replace('_', ' ').title()} needs major improvement ({success_rate:.1f}%)"
                )
            elif success_rate < 90:
                recommendations.append(
                    f"🟡 Review and improve {component.replace('_', ' ')} logic ({success_rate:.1f}%)"
                )
        
        if not recommendations:
            recommendations.append("✅ All components performing well! System is production-ready.")
        else:
            recommendations.append("⚠️ Address critical issues before proceeding to Phase 1C")
        
        return recommendations
    
    def save_report(self, output_file: str = None):
        """Save report to file"""
        if output_file is None:
            output_file = self.results_file.parent / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Report saved to: {output_file}")
        return output_file


def main():
    """Main entry point"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   📊 TESTING RESULTS ANALYZER                              ║
    ║   Generate reports from test results                       ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Find latest results file
    results_dir = Path("test_results/manual_testing")
    
    if results_dir.exists():
        result_files = sorted(results_dir.glob("test_log_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if result_files:
            print(f"\n📂 Found {len(result_files)} test result files:")
            for i, file in enumerate(result_files[:5], 1):
                print(f"  {i}. {file.name} ({datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})")
            
            choice = input("\nAnalyze which file? (1-5 or enter path): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(result_files):
                    results_file = result_files[idx]
                else:
                    results_file = Path(choice)
            except ValueError:
                results_file = Path(choice)
        else:
            results_file = input("\nEnter results file path: ").strip()
    else:
        results_file = input("\nEnter results file path: ").strip()
    
    # Analyze
    analyzer = ResultsAnalyzer(results_file)
    
    # Show report
    report = analyzer.generate_report()
    print("\n" + report)
    
    # Save report
    save = input("\n\nSave report to file? (y/n): ").strip().lower()
    if save == 'y':
        analyzer.save_report()


if __name__ == "__main__":
    main()
