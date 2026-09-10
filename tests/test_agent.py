import concurrent.futures, json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from service.agent import Agent, DemoError, ROOT, retrieve
class AgentTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.db=Path(self.temp.name)/'test.db';self.calls=[]
  def fixture(q,e):
   self.calls.append((q,e));return {'status':'supported','evidence_ids':['AI-01'],'queue':'SecurityReview'},{'provider':'TEST_FIXTURE','model':'not-a-live-llm'}
  self.agent=Agent(self.db,model_call=fixture)
 def tearDown(self):self.temp.cleanup()
 def proposal(self):
  r=self.agent.search({'request_id':'TEST-001','question':'May I upload customer statements to a public AI chatbot?'})
  return self.agent.propose({'retrieval_id':r['retrieval_id']})
 def decision(self,p,choice='Approve'):
  return {'proposal_id':p['proposal_id'],'decision':choice,'reviewer':'Test Reviewer','reason':'Fixture validation only'}
 def test_bm25_retrieves_relevant_policy(self):
  self.assertEqual(retrieve('Upload customer statements to public AI chatbot',self.agent.chunks)[0]['id'],'AI-01')
 def test_vendor_retrieval(self):
  self.assertEqual(retrieve('New analytics vendor missing SOC 2 Type II report',self.agent.chunks)[0]['id'],'VR-01')
 def test_exact_quotes_and_no_case_before_approval(self):
  p=self.proposal();self.assertEqual(len(self.calls),1);self.assertIn(p['citations'][0]['text'],p['answer']);self.assertEqual(self.agent.listing('cases'),[])
 def test_approve_persists_case_across_restart(self):
  self.assertEqual(self.agent.decide(self.decision(self.proposal()))['state'],'case_created');self.assertEqual(len(Agent(self.db).listing('cases')),1)
 def test_reject_creates_no_case(self):
  self.assertEqual(self.agent.decide(self.decision(self.proposal(),'Reject'))['state'],'rejected');self.assertEqual(self.agent.listing('cases'),[])
 def test_replay_does_not_duplicate_case(self):
  body=self.decision(self.proposal());a=self.agent.decide(body);b=self.agent.decide(body)
  self.assertEqual(a['case'],b['case']);self.assertTrue(b['replay']);self.assertEqual(len(self.agent.listing('cases')),1)
 def test_concurrent_approvals_create_one_case(self):
  body=self.decision(self.proposal())
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda _:self.agent.decide(body),range(4)))
  self.assertEqual(sum(not r['replay'] for r in results),1);self.assertEqual(len(self.agent.listing('cases')),1)
 def test_no_matches_skips_model_and_blocks_action(self):
  r=self.agent.search({'request_id':'U1','question':'xylophonic zebras'});p=self.agent.propose({'retrieval_id':r['retrieval_id']})
  self.assertEqual(p['status'],'insufficient');self.assertEqual(self.calls,[]);self.assertEqual(self.agent.decide(self.decision(p))['state'],'closed_no_action')
 def test_model_abstention_blocks_action(self):
  self.agent.model_call=lambda q,e:({'status':'insufficient','evidence_ids':[],'queue':None},{'provider':'TEST_FIXTURE'})
  p=self.proposal();self.assertIn('cannot determine',p['answer']);self.assertEqual(self.agent.decide(self.decision(p))['state'],'closed_no_action')
 def test_fabricated_citation_rejected(self):
  with self.assertRaises(DemoError):self.agent.validate({'status':'supported','evidence_ids':['MADE-UP'],'queue':'SecurityReview'},self.agent.chunks)
 def test_queue_mismatch_rejected(self):
  with self.assertRaises(DemoError):self.agent.validate({'status':'supported','evidence_ids':['AI-01'],'queue':'Procurement'},self.agent.chunks)
 def test_extra_model_prose_rejected(self):
  with self.assertRaises(DemoError):self.agent.validate({'status':'insufficient','evidence_ids':[],'queue':None,'answer':'Made up'},[])
 def test_insufficient_with_citation_rejected(self):
  with self.assertRaises(DemoError):self.agent.validate({'status':'insufficient','evidence_ids':['AI-01'],'queue':None},self.agent.chunks)
 def test_unknown_proposal_rejected(self):
  with self.assertRaises(DemoError):self.agent.decide(self.decision({'proposal_id':'missing'}))
 def test_reject_then_approve_cannot_reopen(self):
  p=self.proposal();self.agent.decide(self.decision(p,'Reject'));self.assertEqual(self.agent.decide(self.decision(p))['state'],'rejected')
 def test_expired_proposal(self):
  p=self.proposal()
  with patch('service.agent.time.time',return_value=p['created_at']+3601):
   with self.assertRaises(DemoError):self.agent.decide(self.decision(p))
 def test_policy_hash_change_blocks_action(self):
  p=self.proposal()
  with patch('service.agent.hashlib.sha256') as digest:
   digest.return_value.hexdigest.return_value='changed'
   with self.assertRaises(DemoError):self.agent.decide(self.decision(p))
 def test_missing_key_never_substitutes_fake_llm(self):
  with patch.dict(os.environ,{'OPENAI_API_KEY':''}):
   with self.assertRaises(DemoError) as c:Agent(self.db).call_llm('question',[])
  self.assertEqual(c.exception.status,503)
 def test_blank_inputs(self):
  with self.assertRaises(DemoError):self.agent.search({'request_id':'x','question':' '})
 def test_audit_records_human_and_action(self):
  self.agent.decide(self.decision(self.proposal()));self.assertEqual([r['event'] for r in self.agent.listing('audit')],['retrieval_completed','proposal_created','human_decision','case_created'])
 def test_workflow_graph_is_connected(self):
  w=json.loads((ROOT/'workflows/cedarbridge-policy-agent.json').read_text());names={n['name'] for n in w['nodes']}
  for source,outputs in w['connections'].items():
   self.assertIn(source,names)
   for branch in outputs['main']:
    for edge in branch:self.assertIn(edge['node'],names)
  self.assertEqual(sum(n['type']=='n8n-nodes-base.httpRequest' for n in w['nodes']),3);self.assertFalse(w['pinData'])
if __name__=='__main__':unittest.main(verbosity=2)
