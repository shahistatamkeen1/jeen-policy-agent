import json,os,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from service.agent import Agent,Handler
class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.env=patch.dict(os.environ,{'DEMO_API_TOKEN':'test-only-token','OPENAI_API_KEY':''});self.env.start()
  class TestHandler(Handler):pass
  TestHandler.agent=Agent(Path(self.temp.name)/'test.db',model_call=lambda q,e:({'status':'supported','evidence_ids':['AI-01'],'queue':'SecurityReview'},{'provider':'TEST_FIXTURE'}))
  self.server=ThreadingHTTPServer(('127.0.0.1',0),TestHandler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
  self.base='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.env.stop();self.temp.cleanup()
 def request(self,path,body=None,auth=True):
  headers={'Content-Type':'application/json'}
  if auth:headers['X-Demo-Token']='test-only-token'
  req=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
  with urllib.request.urlopen(req,timeout=5) as res:return json.load(res)
 def test_unauthorized_request_is_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as c:self.request('/cases',auth=False)
  self.assertEqual(c.exception.code,401)
 def test_health_reports_missing_live_key(self):
  self.assertFalse(self.request('/health',auth=False)['llm_configured'])
 def test_http_end_to_end_with_labeled_model_fixture(self):
  r=self.request('/retrieve',{'request_id':'HTTP-001','question':'May I upload customer statements to a public AI chatbot?'})
  p=self.request('/propose',{'retrieval_id':r['retrieval_id']});self.assertEqual(p['model']['provider'],'TEST_FIXTURE');self.assertEqual(self.request('/cases'),[])
  result=self.request('/decisions',{'proposal_id':p['proposal_id'],'decision':'Approve','reviewer':'Test Reviewer','reason':'HTTP fixture test'})
  self.assertEqual(result['state'],'case_created');self.assertEqual(len(self.request('/cases')),1)
 def test_invalid_request_does_not_create_case(self):
  with self.assertRaises(urllib.error.HTTPError) as c:self.request('/decisions',{'proposal_id':'unknown'})
  self.assertEqual(c.exception.code,400);self.assertEqual(self.request('/cases'),[])
