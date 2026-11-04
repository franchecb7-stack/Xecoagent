import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from supabase_history import SupabaseHistory, HistoryError, HistoryConflict


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.token = 'a'*64
        self.service = SupabaseHistory('https://test.supabase.co', 'sb_publishable_test', self.token)
        self.id = str(uuid4())
        self.messages = [{'role': 'user', 'content': 'Inflación Guatemala'},
                         {'role': 'assistant', 'content': 'Respuesta', 'mostrar_grafica': False}]

    @staticmethod
    def response(data=None, status=200):
        r = requests.Response()
        r.status_code = status
        r._content = json.dumps(data).encode() if data is not None else b''
        return r

    @patch('requests.request')
    def test_create_sends_browser_credential_and_hash(self, http):
        http.return_value = self.response([{'version': 1}])
        self.assertEqual(self.service.save(self.id, 0, self.messages), 1)
        args = http.call_args.kwargs
        self.assertEqual(args['headers']['x-xeco-browser-token'], self.token)
        self.assertNotIn('Authorization', args['headers'])
        self.assertEqual(args['headers']['apikey'], 'sb_publishable_test')
        self.assertEqual(args['json']['owner_hash'], self.service.owner_hash)
        self.assertNotEqual(args['json']['owner_hash'], self.token)
        self.assertEqual(args['json']['messages'], self.messages)
        self.assertFalse(args['allow_redirects'])

    @patch('requests.request')
    def test_update_has_version_and_owner_filters(self, http):
        http.return_value = self.response([{'version': 3}])
        self.assertEqual(self.service.save(self.id, 2, self.messages), 3)
        self.assertEqual(http.call_args.args[0], 'PATCH')
        self.assertEqual(http.call_args.kwargs['params']['version'], 'eq.2')
        self.assertEqual(http.call_args.kwargs['params']['owner_hash'], 'eq.'+self.service.owner_hash)

    @patch('requests.request')
    def test_idempotent_retry_after_lost_ack(self, http):
        http.side_effect = [self.response([]), self.response([{'version': 1, 'messages': self.messages}])]
        self.assertEqual(self.service.save(self.id, 0, self.messages), 1)

    @patch('requests.request')
    def test_concurrent_change_does_not_overwrite(self, http):
        http.side_effect = [self.response([]), self.response([{'version': 3, 'messages': []}])]
        with self.assertRaises(HistoryConflict):
            self.service.save(self.id, 2, self.messages)
        self.assertEqual(http.call_count, 2)

    @patch('requests.request')
    def test_load_inaccessible_id_fails(self, http):
        http.return_value = self.response([])
        with self.assertRaises(HistoryError):
            self.service.load(self.id)

    @patch('requests.request')
    def test_pagination(self, http):
        http.side_effect = [self.response([{'id': str(i)} for i in range(100)]), self.response([{'id': 'last'}])]
        self.assertEqual(len(self.service.list_conversations()), 101)
        self.assertEqual(http.call_args.kwargs['params']['offset'], 100)

    @patch('requests.request')
    def test_same_browser_new_session_same_owner(self, http):
        restored = SupabaseHistory('https://test.supabase.co', 'sb_publishable_test', self.token)
        other = SupabaseHistory('https://test.supabase.co', 'sb_publishable_test', 'b'*64)
        self.assertEqual(restored.owner_hash, self.service.owner_hash)
        self.assertNotEqual(other.owner_hash, self.service.owner_hash)
        http.return_value = self.response([])
        restored.list_conversations()
        self.assertEqual(http.call_args.kwargs['headers']['x-xeco-browser-token'], self.token)

    def test_rejects_missing_or_malformed_browser_credential(self):
        for token in [None, '', 'predictable-id', 'g'*64, 'a'*63]:
            with self.assertRaises(HistoryError):
                SupabaseHistory('https://test.supabase.co', 'sb_publishable_test', token)

    @patch('requests.request')
    def test_network_failure_does_not_include_internals(self, http):
        http.side_effect = requests.ConnectionError('PRIVATE_INTERNAL_DATA')
        with self.assertRaises(HistoryError) as caught:
            self.service.list_conversations()
        self.assertNotIn('PRIVATE_INTERNAL_DATA', str(caught.exception))

    def test_rejects_admin_key(self):
        with self.assertRaises(HistoryError):
            SupabaseHistory('https://test.supabase.co', 'sb_secret_test', self.token)
        import base64
        payload = base64.urlsafe_b64encode(b'{"role":"service_role"}').decode().rstrip('=')
        with self.assertRaises(HistoryError):
            SupabaseHistory('https://test.supabase.co', 'x.'+payload+'.x', self.token)



if __name__ == '__main__':
    unittest.main()
