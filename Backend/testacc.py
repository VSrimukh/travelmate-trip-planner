import requests
import json
import time

API_URL = "http://localhost:5000"

INDIAN_TEST_CASES = [
    {
        "destination": "Goa",
        "prompt": "2-day trip visiting Goa. Beach, nightlife, seafood.",
        "expected_keywords": ["beach", "calangute", "baga", "fort", "seafood"],
        "expected_budget_range": (6000, 15000)
    },
    {
        "destination": "Jaipur",
        "prompt": "2-day trip visiting Jaipur. Heritage, local food.",
        "expected_keywords": ["hawa mahal", "amber", "palace", "market"],
        "expected_budget_range": (5000, 12000)
    },
    {
        "destination": "Kerala",
        "prompt": "2-day trip visiting Kerala. Backwaters, houseboat.",
        "expected_keywords": ["backwater", "houseboat", "alleppey", "boat"],
        "expected_budget_range": (8000, 18000)
    },
    {
        "destination": "Udaipur",
        "prompt": "2-day trip visiting Udaipur. Lakes, palaces.",
        "expected_keywords": ["lake", "palace", "pichola", "boat"],
        "expected_budget_range": (6000, 15000)
    }
]

def test_itinerary_accuracy(test_case):
    print(f"\n{'='*60}")
    print(f"Testing: {test_case['destination']}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/generate-itinerary",
            json={"prompt": test_case['prompt']},
            timeout=200
        )
        
        if response.status_code != 200:
            return {
                "destination": test_case['destination'],
                "status": "failed",
                "error": f"API returned {response.status_code}"
            }
        
        result = response.json()
        generated_text = result.get('response', '').lower()
        
        if not generated_text:
            return {
                "destination": test_case['destination'],
                "status": "failed",
                "error": "Empty response"
            }
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in test_case['expected_keywords']:
            if keyword.lower() in generated_text:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        keyword_accuracy = (len(found_keywords) / len(test_case['expected_keywords'])) * 100
        
        has_day_structure = "day 1" in generated_text and "day 2" in generated_text
        has_time_slots = any(slot in generated_text for slot in ["morning", "afternoon", "evening"])
        has_food_mention = any(word in generated_text for word in ["food", "cuisine", "restaurant", "eat", "lunch", "dinner"])
        has_transport = any(word in generated_text for word in ["taxi", "bus", "auto", "train", "walk", "cab"])
        
        structure_score = sum([has_day_structure, has_time_slots, has_food_mention, has_transport]) / 4 * 100
        
        overall_accuracy = (keyword_accuracy * 0.6) + (structure_score * 0.4)
        
        print(f"✓ Response Length: {len(generated_text)} characters")
        print(f"✓ Keyword Accuracy: {keyword_accuracy:.1f}%")
        print(f"✓ Structure Score: {structure_score:.1f}%")
        print(f"✓ Overall Accuracy: {overall_accuracy:.1f}%")
        print(f"\nFound Keywords ({len(found_keywords)}/{len(test_case['expected_keywords'])}): {', '.join(found_keywords)}")
        if missing_keywords:
            print(f"Missing Keywords: {', '.join(missing_keywords)}")
        
        return {
            "destination": test_case['destination'],
            "status": "success",
            "keyword_accuracy": round(keyword_accuracy, 1),
            "structure_score": round(structure_score, 1),
            "overall_accuracy": round(overall_accuracy, 1),
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "response_length": len(generated_text),
            "has_proper_structure": has_day_structure
        }
        
    except requests.exceptions.Timeout:
        return {
            "destination": test_case['destination'],
            "status": "timeout",
            "error": "Request timed out"
        }
    except Exception as e:
        return {
            "destination": test_case['destination'],
            "status": "error",
            "error": str(e)
        }

def test_budget_accuracy(test_case):
    try:
        response = requests.post(
            f"{API_URL}/api/generate-budget",
            json={"prompt": test_case['prompt']},
            timeout=150
        )
        
        if response.status_code != 200:
            return None
        
        result = response.json()
        generated_text = result.get('response', '')
        
        import re
        prices = re.findall(r'₹\s*(\d+[,\d]*)', generated_text)
        
        if prices:
            prices = [int(p.replace(',', '')) for p in prices]
            total_budget = max(prices)
            
            min_expected, max_expected = test_case['expected_budget_range']
            
            if min_expected <= total_budget <= max_expected:
                budget_accuracy = 100
            elif total_budget < min_expected:
                budget_accuracy = (total_budget / min_expected) * 100
            else:
                budget_accuracy = (max_expected / total_budget) * 100
            
            return {
                "budget_accuracy": round(budget_accuracy, 1),
                "estimated_budget": total_budget,
                "expected_range": test_case['expected_budget_range']
            }
        
        return None
        
    except Exception as e:
        return None

def run_all_tests():
    print("\n" + "="*60)
    print("INDIAN DESTINATIONS ACCURACY TEST")
    print("="*60)
    
    print("\nChecking API connection...")
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✓ API is running")
        else:
            print("✗ API returned error")
            return
    except:
        print("✗ Cannot connect to API. Make sure Flask app is running on port 5000")
        return
    
    results = []
    
    for i, test_case in enumerate(INDIAN_TEST_CASES, 1):
        print(f"\n[Test {i}/{len(INDIAN_TEST_CASES)}]")
        
        itinerary_result = test_itinerary_accuracy(test_case)
        results.append(itinerary_result)
        
        time.sleep(2)
    
    print("\n\n" + "="*60)
    print("FINAL ACCURACY REPORT")
    print("="*60)
    
    successful_tests = [r for r in results if r['status'] == 'success']
    
    if successful_tests:
        avg_keyword_accuracy = sum(r['keyword_accuracy'] for r in successful_tests) / len(successful_tests)
        avg_structure_score = sum(r['structure_score'] for r in successful_tests) / len(successful_tests)
        avg_overall_accuracy = sum(r['overall_accuracy'] for r in successful_tests) / len(successful_tests)
        
        print(f"\nTests Completed: {len(successful_tests)}/{len(INDIAN_TEST_CASES)}")
        print(f"Average Keyword Accuracy: {avg_keyword_accuracy:.1f}%")
        print(f"Average Structure Score: {avg_structure_score:.1f}%")
        print(f"Average Overall Accuracy: {avg_overall_accuracy:.1f}%")
        
        print("\n\nDetailed Results:")
        print("-" * 60)
        for r in results:
            if r['status'] == 'success':
                print(f"\n{r['destination']}: {r['overall_accuracy']:.1f}% accuracy")
                print(f"  Keywords: {r['keyword_accuracy']:.1f}% | Structure: {r['structure_score']:.1f}%")
            else:
                print(f"\n{r['destination']}: {r['status'].upper()} - {r.get('error', 'Unknown error')}")
        
        accuracy_grade = "Excellent" if avg_overall_accuracy >= 80 else "Good" if avg_overall_accuracy >= 60 else "Needs Improvement"
        print(f"\n\nFinal Grade: {accuracy_grade}")
        print("="*60)
        
        with open('accuracy_report.json', 'w') as f:
            json.dump({
                "summary": {
                    "avg_keyword_accuracy": round(avg_keyword_accuracy, 1),
                    "avg_structure_score": round(avg_structure_score, 1),
                    "avg_overall_accuracy": round(avg_overall_accuracy, 1),
                    "grade": accuracy_grade,
                    "total_tests": len(INDIAN_TEST_CASES),
                    "successful_tests": len(successful_tests)
                },
                "detailed_results": results
            }, f, indent=2)
        
        print("\n✓ Report saved to accuracy_report.json")
    else:
        print("\n✗ No successful tests completed")

if __name__ == "__main__":
    run_all_tests()