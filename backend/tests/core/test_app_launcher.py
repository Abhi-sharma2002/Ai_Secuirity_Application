"""Launcher environment routing only; no services, sockets or provider calls."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('launcher',Path(__file__).resolve().parents[3]/'run_app.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def test_retired_paid_launch_flag_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'trial-credit-only'):
            launcher.service_environments({}, True, True)

    def test_default_stays_disabled_even_with_inherited_enablement(self):
        parent={'LIVE_LLM_ENABLED':'true','FREE_ONLY':'false'}
        backend,frontend=launcher.service_environments(parent)
        self.assertEqual(backend['LIVE_LLM_ENABLED'],'false')
        self.assertEqual(frontend['LIVE_LLM_ENABLED'],'false')
        self.assertEqual(backend['FREE_ONLY'],'true')
        self.assertEqual(parent,{'LIVE_LLM_ENABLED':'true','FREE_ONLY':'false'})

    def test_explicit_live_enables_only_backend_and_preserves_settings(self):
        parent={'LLM_BACKEND':'azure_openai','AZURE_OPENAI_DEPLOYMENT':'synthetic-deployment','AZURE_OPENAI_API_KEY':'synthetic-only'}
        backend,frontend=launcher.service_environments(parent,True)
        self.assertEqual(backend['LIVE_LLM_ENABLED'],'true')
        self.assertEqual(frontend['LIVE_LLM_ENABLED'],'false')
        self.assertEqual((backend['FREE_ONLY'],frontend['FREE_ONLY']),('true','true'))
        self.assertTrue(all(backend[k]==v for k,v in parent.items()))


from unittest.mock import patch,MagicMock


def test_existing_healthy_application_is_reused_without_starting_children():
    connection=MagicMock()
    backend=MagicMock(status_code=200);backend.json.return_value={'scope':'local-single-user-one-worker'}
    frontend=MagicMock(status_code=200,text='ok')
    client=MagicMock();client.__enter__.return_value.get.side_effect=[backend,frontend]
    with patch.object(launcher.socket,'create_connection',return_value=connection),patch('httpx.Client',return_value=client),patch.object(launcher.subprocess,'Popen',side_effect=AssertionError('Must not spawn')):
        code,message=launcher.existing_service_status()
    assert code==0 and 'already running' in message


def test_partial_or_unrelated_ports_do_not_start_or_stop_services():
    with patch.object(launcher.socket,'create_connection',side_effect=[ConnectionRefusedError(),MagicMock()]):
        code,message=launcher.existing_service_status()
    assert code==1 and '8501' in message and 'no existing process was stopped' in message


def test_free_ports_allow_normal_startup():
    with patch.object(launcher.socket,'create_connection',side_effect=ConnectionRefusedError()):
        assert launcher.existing_service_status() is None
