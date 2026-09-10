"""Paid live-model evaluation. Run explicitly after configuring a key. Creates no cases."""
import json, tempfile, time
from pathlib import Path
from service.agent import Agent, ROOT, DemoError

def main():
 results=[]
 with tempfile.TemporaryDirectory() as folder:
  agent=Agent(Path(folder)/'evaluation.db')
  for case in json.loads((ROOT/'docs/evaluation_cases.json').read_text()):
   start=time.monotonic()
   try:
    r=agent.search({'request_id':case['id'],'question':case['question']})
    p=agent.propose({'retrieval_id':r['retrieval_id']})
    correct=p['status']==case['status'] and p['queue']==case['queue']
    if case.get('required_citation'):correct=correct and case['required_citation'] in [c['id'] for c in p['citations']]
    if case.get('allow_abstention') and p['status']=='insufficient':correct=True
    results.append({'id':case['id'],'passed':correct,'seconds':round(time.monotonic()-start,2),'proposal':p})
   except DemoError as e:results.append({'id':case['id'],'passed':False,'error':e.message})
 report={'run_at_unix':time.time(),'evaluation_type':'live_model','cases_created':0,'passed':sum(r['passed'] for r in results),'total':len(results),'results':results}
 output=ROOT/'evidence/live-evaluation.json';output.write_text(json.dumps(report,indent=2))
 print(f"Live checks passed: {report['passed']}/{report['total']}. Review {output} and inspect evidence relevance manually.")
 if report['passed']!=report['total']:raise SystemExit(1)
if __name__=='__main__':main()
