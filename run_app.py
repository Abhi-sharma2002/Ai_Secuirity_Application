"""Start the local app; optional gated live answering, never automatic queries."""
import argparse
import importlib.util
import os
from pathlib import Path
import signal
import socket
import secrets
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def service_environments(parent, live_answers=False, paid_azure_test=False, local_access=False):
    if paid_azure_test:
        raise ValueError('Paid launch mode is disabled by the standing trial-credit-only project scope')
    backend = parent.copy()
    backend.pop('LOCAL_ACCESS_TOKEN', None)
    backend.update(PYTHONPATH=str(ROOT/'backend'), BACKEND_URL='http://127.0.0.1:8000',
                   LIVE_LLM_ENABLED='true' if live_answers else 'false', FREE_ONLY='true')
    frontend = backend.copy()
    if local_access:
        token = secrets.token_urlsafe(48)
        backend['LOCAL_ACCESS_TOKEN'] = token
        frontend['LOCAL_ACCESS_TOKEN'] = token
    frontend['LIVE_LLM_ENABLED'] = 'false'
    return backend, frontend



def existing_service_status():
    """Inspect local ports before spawning children; never stop their owners."""
    occupied=[]
    for port in (8000,8501):
        try:
            with socket.create_connection(('127.0.0.1',port),timeout=1):
                occupied.append(port)
        except ConnectionRefusedError:
            pass
        except OSError:
            # An ambiguous port check must not start a competing service.
            occupied.append(port)
    if not occupied:
        return None
    if occupied==[8000,8501]:
        import httpx
        try:
            with httpx.Client(trust_env=False,timeout=3,follow_redirects=False) as client:
                backend=client.get('http://127.0.0.1:8000/health')
                frontend=client.get('http://127.0.0.1:8501/_stcore/health')
                if (backend.status_code==200 and backend.json().get('scope')=='local-single-user-one-worker'
                        and frontend.status_code==200 and frontend.text.strip()=='ok'):
                    return (0,'Application is already running: http://127.0.0.1:8501\n'
                              'No duplicate services started. Existing answering mode is unchanged.')
        except (httpx.HTTPError,ValueError,AttributeError):
            pass
    return (1,'Cannot start: local port(s) '+', '.join(map(str,occupied))+' are already in use.\n'
              'No duplicate services started and no existing process was stopped.\n'
              'Stop the earlier launcher with Ctrl+C in its original terminal before starting again.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check local dependencies without starting services')
    parser.add_argument('--local-access', action='store_true', help='Enable single-user local access without Microsoft sign-in')
    parser.add_argument('--live-answers', action='store_true',
                        help='Enable backend answering only within its existing valid allowance; sends no query')
    parser.add_argument('--paid-azure-test', action='store_true',
                        help='Retired option; rejected under the standing trial-credit-only scope')
    args = parser.parse_args()
    if args.paid_azure_test:
        parser.error('--paid-azure-test is disabled: trial credits only, no out-of-pocket authorization')
    missing = [name for name in ('uvicorn', 'streamlit', 'fastapi', 'httpx', 'langchain_core', 'chromadb', 'sentence_transformers', 'jwt', 'authlib')
               if importlib.util.find_spec(name) is None]
    if missing:
        parser.exit(1, 'Missing dependencies: '+', '.join(missing)+'\nUse the existing .venv and backend/requirements.txt.\n')
    if not (ROOT/'.env').is_file():
        parser.exit(1, 'Create .env from .env.example and enter configuration locally first.\n')
    if args.check:
        print('Local app dependencies and .env present. No services or provider requests started.')
        return
    existing = existing_service_status()
    if existing is not None:
        code,message = existing
        print(message,flush=True)
        return code
    # Only these children are managed; never stop an unrelated existing service.
    backend_env, frontend_env = service_environments(os.environ, args.live_answers, args.paid_azure_test, args.local_access)
    commands = [
        [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--workers', '1'],
        [sys.executable, '-m', 'streamlit', 'run', str(ROOT/'frontend/streamlit_app.py'),
         '--server.address', '127.0.0.1', '--server.port', '8501', '--server.headless', 'true',
         '--browser.gatherUsageStats', 'false', '--server.runOnSave', 'true'],
    ]
    children = []
    def stop(_signal, _frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        for command, env in zip(commands, (backend_env, frontend_env)):
            children.append(subprocess.Popen(command, cwd=ROOT, env=env))
        status = 'Backend live answering requested; every call requires valid remaining allowance.' if args.live_answers else 'Live answering disabled.'
        print('Document Assistant: http://127.0.0.1:8501\n'+status+' Ctrl+C stops both services.', flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.5)
        failed = next(child.returncode for child in children if child.returncode is not None)
        return failed or 1
    except KeyboardInterrupt:
        return 0
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == '__main__':
    sys.exit(main())
