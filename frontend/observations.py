"""Per-answer measurements, independent of cached presentation helpers."""

def observation_metrics(value):
    """Describe one actual response without treating an unknown answer as graded."""
    import math
    status = value.get('status', 'unknown')
    latency = value.get('latency_ms')
    seconds = (f'{latency/1000:.3f} s' if isinstance(latency, (int, float))
               and math.isfinite(latency) and latency >= 0 else 'N/A')
    references = [] if status == 'insufficient_evidence' else value.get('references', [])
    citation_check = 'N/A — no supported answer' if status == 'insufficient_evidence' else value.get('citation_check', 'N/A — no validated answer')
    screening = value.get('screening')
    mode = value.get('mode')
    if isinstance(screening, dict):
        flagged = str(screening.get('question_flagged')) if type(screening.get('question_flagged')) is bool else 'N/A'
    else:
        flagged = 'N/A' if mode == 'C' else 'N/A (C only)'
    return [
        {'Measure': 'Response status', 'Value': status},
        {'Measure': 'Elapsed time', 'Value': seconds},
        {'Measure': 'Supporting references', 'Value': str(len(references))},
        {'Measure': 'Citation ID check', 'Value': citation_check},
        {'Measure': 'Question flagged by C', 'Value': flagged},
        {'Measure': 'Task correctness', 'Value': 'N/A — expected outcome and review needed'},
        {'Measure': 'Attack success', 'Value': 'N/A — declared attack and review needed'},
        {'Measure': 'False positive', 'Value': 'N/A — benign expected outcome and review needed' if mode == 'C' else 'N/A (C only)'},
        {'Measure': 'Human answer quality', 'Value': 'N/A — human rating needed'},
    ]
