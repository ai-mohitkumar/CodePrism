import httpx
import json

def run_e2e_tests():
    client = httpx.Client(base_url='http://127.0.0.1:8001', timeout=20.0)

    # 1. Languages
    print('=== 1. LANGUAGES API ===')
    langs = client.get('/api/languages').json()
    print('Supported engines:', [l['name'] for l in langs['languages']])

    # 2. Python Find Max Analysis
    print('\n=== 2. PYTHON FIND MAX ANALYSIS ===')
    code_py = '''def find_max(arr):
    maximum = arr[0]
    for x in arr:
        if x > maximum:
            maximum = x
    return maximum

numbers = [10, 20, 5, 30]
print(find_max(numbers))
'''
    res_py = client.post('/api/analyze', json={'language': 'python', 'code': code_py}).json()
    print('Execution Status:', res_py['execution']['status'])
    print('Output (stdout):', res_py['execution']['stdout'].strip())
    print('Static Time Complexity:', res_py['complexity']['time_complexity'])
    print('Static Space Complexity:', res_py['complexity']['space_complexity'])
    print('Execution Time:', res_py['execution']['execution_time_sec'], 's')
    print('Peak Memory:', res_py['execution']['peak_memory_mb'], 'MB')
    print('Maintainability Score:', res_py['quality']['maintainability_score'], '/ 10')
    print('Line Analysis count:', len(res_py['line_analysis']))
    if res_py.get('benchmark'):
        print('Empirical Benchmark Fit:', res_py['benchmark']['empirical_big_o'])
        print('Benchmark Points:', len(res_py['benchmark']['points']))

    # 3. Python Syntax Error Diagnosis
    print('\n=== 3. SYNTAX ERROR DIAGNOSTIC POINTER ===')
    code_err = '''def calculate(a, b):
    result = a + b
    print(result

calculate(10, 20)'''
    res_err = client.post('/api/analyze', json={'language': 'python', 'code': code_err}).json()
    print('Status:', res_err['execution']['status'])
    print('Error Line:', res_err['execution']['error_line'])
    print('ASCII Pointer:\n' + str(res_err['execution']['error_pointer']))
    print('Suggested Fix:', res_err['execution']['suggested_fix'])

    # 4. Security Audit
    print('\n=== 4. SECURITY AUDIT ===')
    code_sec = '''user_data = input()
eval(user_data)
api_key = "sk_live_12345678abcdef"
'''
    res_sec = client.post('/api/analyze', json={'language': 'python', 'code': code_sec}).json()
    print('Issues detected:', len(res_sec['security']))
    for issue in res_sec['security']:
        print(f" - [{issue['severity']}] Line {issue['line']}: {issue['title']}")

    # 5. C++ Compilation and Execution
    print('\n=== 5. C++ ENGINE COMPILATION & EXECUTION ===')
    code_cpp = '''#include <iostream>
#include <vector>

int main() {
    std::vector<int> nums = {10, 20, 30};
    int sum = 0;
    for (int x : nums) sum += x;
    std::cout << "C++ Sum: " << sum << std::endl;
    return 0;
}
'''
    res_cpp = client.post('/api/analyze', json={'language': 'cpp', 'code': code_cpp}).json()
    print('C++ Status:', res_cpp['execution']['status'])
    print('C++ Output:', res_cpp['execution']['stdout'].strip())
    print('C++ Complexity:', res_cpp['complexity']['time_complexity'])

if __name__ == '__main__':
    run_e2e_tests()
