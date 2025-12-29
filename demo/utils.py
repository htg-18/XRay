def format_price(price: float) -> str:
    return f"${price:.2f}"


def format_rating(rating: float) -> str:
    return f"{rating:.1f}★"


def format_number(num: int) -> str:
    return f"{num:,}"


def get_filter_summary(evaluations: list) -> dict:
    total = len(evaluations)
    passed = sum(1 for e in evaluations if e['qualified'])
    failed = total - passed
    
    failures_by_filter = {}
    for eval in evaluations:
        if not eval['qualified']:
            for check in eval['checks']:
                if not check['passed']:
                    filter_name = check['name']
                    failures_by_filter[filter_name] = failures_by_filter.get(filter_name, 0) + 1
    
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round((passed / total) * 100, 1) if total > 0 else 0,
        "failures_by_filter": failures_by_filter
    }


def print_filter_summary(evaluations: list):
    summary = get_filter_summary(evaluations)
    
    print(f"\n Filter Summary:")
    print(f"   Total evaluated: {summary['total']}")
    print(f"   ✓ Passed: {summary['passed']} ({summary['pass_rate']}%)")
    print(f"   ✗ Failed: {summary['failed']}")
    
    if summary['failures_by_filter']:
        print(f"\n   Common failure reasons:")
        for filter_name, count in sorted(summary['failures_by_filter'].items(), 
                                         key=lambda x: x[1], reverse=True):
            print(f"   • {filter_name}: {count} products")

