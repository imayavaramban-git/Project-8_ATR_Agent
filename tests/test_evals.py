import subprocess
import sys

def test_ai_eval_benchmark_suite():
    result = subprocess.run(
        [sys.executable, "evals/run_evals.py"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    assert result.returncode == 0
