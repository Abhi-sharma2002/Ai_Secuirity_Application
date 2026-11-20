"""Rebuild an editable presentation and matching preview/PDF, with no model calls."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import csv, json, math, textwrap, shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parent
REFERENCE=Path('/home/sigmoid/Downloads/ForecastIQ_V2_Presentation.pptx')
ROOT=OUT.parents[2]
NAVY='1F3B73'; RED='E3404A'; TEXT='1F2937'; MUTED='6B7280'; LIGHT='F3F5FA'; EDGE='E5E7EB'; BLUE='2F6FDE'; GREEN='13896F'; WHITE='FFFFFF'
prs=Presentation();prs.slide_width=Inches(10);prs.slide_height=Inches(5.625)
prs.core_properties.title='AI Security Document Lab — Architecture & Defense Evaluation'
prs.core_properties.author='Abhishek Sharma'
prs.core_properties.subject='Local RAG, prompt-injection defenses, storage and evaluation'
prs.core_properties.keywords='AI security, RAG, A/B/C, architecture, Azure, Chroma, SQLite'
scenes=[]; notes=[]; current=None; idx=0
fontdir=Path('/usr/share/fonts/truetype/liberation2')
def font(size,bold=False):return ImageFont.truetype(str(fontdir/('LiberationSans-Bold.ttf' if bold else 'LiberationSans-Regular.ttf')),round(size*1.3333))
def rgb(c):return RGBColor.from_string(c)
def box(x,y,w,h,fill=LIGHT,line=None,round=True):
 s=current.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if round else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
 s.fill.solid();s.fill.fore_color.rgb=rgb(fill)
 if line:s.line.color.rgb=rgb(line);s.line.width=Pt(.8)
 else:s.line.fill.background()
 if round:
  try:s.adjustments[0]=.12
  except Exception:pass
 scenes[-1].append(('rect',x,y,w,h,fill,line,round));return s

def text(x,y,w,h,content,size=15,color=TEXT,bold=False):
 # Explicit wraps keep the editable PowerPoint and preview consistent.
 wrapped=[]
 for line in content.split('\n'):
  words=line.split();buf=''
  for word in words:
   candidate=(buf+' '+word).strip()
   if font(size*128/96,bold).getlength(candidate)>w*128-10 and buf:
    wrapped.append(buf);buf=word
   else:buf=candidate
  wrapped.append(buf)
 line_h=size/72*1.12
 if len(wrapped)*line_h>h+.04:raise ValueError(f'Text exceeds box on slide {idx}: {content[:75]} ({len(wrapped)} lines, h={h})')
 s=current.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=s.text_frame;tf.clear();tf.word_wrap=False
 tf.margin_left=tf.margin_right=0;tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(wrapped):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_after=Pt(0);p.space_before=Pt(0);p.line_spacing=1.12
 scenes[-1].append(('text',x,y,w,h,'\n'.join(wrapped),size,color,bold));return s

def arrow(x1,y1,x2,y2,color=MUTED):
 s=current.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2));s.line.color.rgb=rgb(color);s.line.width=Pt(1.5)
 from pptx.oxml.xmlchemy import OxmlElement
 tail=OxmlElement('a:tailEnd');tail.set('type','triangle');s.line._get_or_add_ln().append(tail)
 scenes[-1].append(('arrow',x1,y1,x2,y2,color))

def new(title,kicker='AI SECURITY DOCUMENT LAB',note=''):
 global current,idx
 idx+=1;current=prs.slides.add_slide(prs.slide_layouts[6]);scenes.append([])
 current.background.fill.solid();current.background.fill.fore_color.rgb=rgb(WHITE)
 box(.38,.32,.045,.44,RED,round=False)
 text(.56,.31,8.9,.5,title,25,NAVY,True)
 box(.55,5.19,8.9,.012,EDGE,round=False)
 text(.55,5.28,8,.18,kicker+'  |  29 OCT 2026',8,MUTED)
 text(9.07,5.27,.4,.2,f'{idx:02}',9,MUTED)
 current.notes_slide.notes_text_frame.text=note
 notes.append((title,note));return current

def card(x,y,w,h,label,body,accent=NAVY,sz=14):
 box(x,y,w,h,LIGHT,EDGE);box(x,y,.035,h,accent,round=False)
 text(x+.16,y+.14,w-.30,.56,label,16 if w<3 else 17,accent,True)
 text(x+.16,y+.70,w-.30,h-.80,body,sz)

def band(content,y=4.65,color=NAVY):
 box(.55,y,8.9,.36,LIGHT);text(.69,y+.075,8.62,.25,content,11,color)

# 1 — title mirrors the supplied reference's white/navy/red treatment.
new('AI Security Document Lab',note='Introduce yourself as Abhishek Sharma. This is a document assistant and an evaluation lab: it asks whether an LLM can use document facts without obeying malicious instructions embedded in those documents. The layout follows the provided ForecastIQ reference; no ForecastIQ product claims are reused.')
text(.62,1.13,8.65,1.12,'Architecture & evaluation of\nprompt-injection defenses',30,TEXT,True)
box(.64,2.55,.75,.055,RED,round=False)
text(.65,2.90,7.9,.6,'Local RAG  ·  A/B/C comparison  ·  Traceable evidence',19,NAVY)
text(.65,3.75,7.8,.6,'Abhishek Sharma\nProject presentation · 29 October 2026',16,TEXT)
with ZipFile(REFERENCE) as z:(OUT/'sigmoid-reference-logo.png').write_bytes(z.read('ppt/media/image2.png'))
current.shapes.add_picture(str(OUT/'sigmoid-reference-logo.png'),Inches(7.85),Inches(4.22),width=Inches(1.55))
scenes[-1].append(('image',7.85,4.22,1.55,.85,str(OUT/'sigmoid-reference-logo.png')))

new('Project Overview',note='The user uploads a file or selects one of the 45 predefined sources, then asks a new question. Local mode returns passages only. Authorized live mode sends the question and retrieved passages to the existing Azure gpt-5-mini deployment. The benchmark uses fixed cases and saved observations; opening results makes no provider call.')
card(.55,1.12,4.28,2.84,'Document assistant','Upload TXT, Markdown, PDF or DOCX\nSearch passages locally\nAsk new questions with source citations\nChoose uploaded or predefined documents')
card(5.02,1.12,4.43,2.84,'Security evaluation','Compare A, B and C on shared evidence\nTest direct and indirect injection\nSave actual responses and errors\nReview answer quality and disclosure',RED)
band('Core question: can the assistant use the facts without obeying the document’s instructions?')

new('Objectives & Scope',note='We measure resistance and usefulness, not only refusal. A response that blocks every attack may also lose useful answers. The app is a local, single-user proof of concept. It does not train or fine-tune the LLM, create cloud search resources, or guarantee protection from all attacks.')
card(.55,1.13,5.60,3.30,'Primary objectives','Ground answers in document evidence\nSeparate trusted policy from untrusted content\nCompare defense effectiveness and latency\nPreserve sources, configuration and results\nUse genuine human judgments for quality',sz=15)
for y,n,l in [(1.14,'45','frozen source documents'),(2.22,'47','main benchmark cases'),(3.30,'3','distinct defense pipelines')]:
 box(6.38,y,3.07,.91,LIGHT,EDGE);text(6.56,y+.12,.78,.4,n,25,NAVY,True);text(7.48,y+.20,1.75,.53,l,13)
band('Local parsing, embeddings, retrieval and storage; Azure is used only for authorized inference.')

new('Tech Stack',note='SQLite is the application registry; Chroma is the vector search store. Chroma itself uses internal SQLite files, but that is separate from our application registry. MiniLM runs on CPU and creates 384-dimensional normalized vectors. Azure gpt-5-mini is the existing model deployment; local search does not call it.')
items=[('Interface','Streamlit','Documents, Ask, comparison, metrics'),('Backend API','Python + FastAPI','Validation and orchestration'),('Parsing','pypdf + python-docx','TXT / MD / text PDF / DOCX'),('Embeddings','Local MiniLM-L6-v2','CPU · 384 dimensions'),('Vector retrieval','Chroma','Persistent cosine search'),('App registry','SQLite','Versions, requests, accounting'),('Evaluation','JSON + CSV + Matplotlib','Cases, observations, charts'),('Answering / screening','Azure gpt-5-mini','Existing trial deployment')]
for i,(a,b,c) in enumerate(items):
 x=.55+(i%2)*4.55;y=1.09+(i//2)*.94;box(x,y,4.35,.81,LIGHT,EDGE);text(x+.13,y+.10,1.35,.56,a,13,NAVY,True);text(x+1.55,y+.09,2.64,.28,b,13,TEXT,True);text(x+1.55,y+.42,2.64,.27,c,10,MUTED)

new('Architecture',note='Read left to right. Both document libraries meet at evidence retrieval. Original uploads and document versions remain local. Uploaded vectors and the frozen evaluation index are separate. Only selected evidence and the question cross the Azure boundary when the user submits an authorized live request. C may remove evidence after the shared initial retrieval. Expected answers and evaluator labels never enter the answering prompt.')
box(.55,1.02,6.96,3.65,LIGHT,EDGE);text(.72,1.13,6.5,.25,'LOCAL MACHINE — parsing, retrieval, storage and evaluation',11,NAVY,True)
box(7.72,1.02,1.73,3.65,'EDF3FC',BLUE);text(7.88,1.17,1.42,.45,'AZURE',13,BLUE,True)
# Native editable architecture nodes
for x,y,w,h,t in [(.78,1.73,1.43,.72,'Streamlit UI'),(2.54,1.73,1.54,.72,'FastAPI API'),(4.39,1.73,2.78,.72,'Shared evidence retrieval'),(.78,2.92,1.43,.88,'Uploads /\n45 fixtures'),(2.54,2.92,1.54,.88,'Parse + chunk\nLocal embeddings'),(4.39,2.92,1.29,.88,'Chroma\nvectors + text'),(5.90,2.92,1.27,.88,'SQLite\nversions / calls')]:
 box(x,y,w,h,WHITE,EDGE);text(x+.10,y+.16,w-.20,h-.19,t,12,NAVY,True)
arrow(2.22,2.09,2.52,2.09);arrow(4.09,2.09,4.37,2.09)
arrow(2.22,3.36,2.52,3.36);arrow(4.09,3.36,4.37,3.36);arrow(5.05,2.92,5.05,2.48)
box(7.91,1.88,1.35,1.43,WHITE,BLUE);text(8.02,2.08,1.14,1.01,'gpt-5-mini\nAnswering\nC screening',13,BLUE,True)
arrow(7.19,2.09,7.88,2.09,BLUE);text(6.87,2.49,.75,.35,'A / B / C',10,NAVY,True)
text(.78,4.10,6.3,.35,'Local-only: return passages  |  Live: apply selected defense and cite sources',11)
text(7.90,3.63,1.40,.72,'Explicit request\nAllowance gate\nNo auto-retry',10,MUTED)
band('Trust boundary: document text is evidence, never a source of application authority.',4.78)

new('How a Document Becomes Searchable',note='Every upload gets a logical document ID and an immutable version ID. Its original bytes are saved before parsing. Only fully indexed and verified versions become active. Overlap helps retain context across chunk boundaries. A scanned PDF can require OCR; parsing does not make malicious content trustworthy. A hash verifies content identity, not safety.')
steps=[('01','Validate','Type + size\nSHA-256'),('02','Parse','Extract text\nPage / section'),('03','Chunk','1,000 chars\n150 overlap'),('04','Embed','384 values\nLocal CPU'),('05','Index','Chroma\nVerify + activate')]
for i,(n,a,b) in enumerate(steps):
 x=.55+i*1.81;box(x,1.48,1.62,2.01,LIGHT,EDGE);text(x+.13,1.65,1.35,.45,n,26,RED,True);text(x+.13,2.20,1.35,.4,a,17,NAVY,True);text(x+.13,2.80,1.35,.60,b,12)
 if i<4:arrow(x+1.63,2.45,x+1.79,2.45)
text(.60,3.91,8.82,.45,'At question time: embed query → cosine retrieval → up to 5 passages → bounded evidence',15,NAVY,True)
band('Indexing is retrieval preparation. It does not train or fine-tune the answering model.')

new('Three Defense Pipelines: A / B / C',note='All modes share grounding rules, model settings and the initial evidence. A is a grounded baseline, not an unrestricted model. B adds instruction separation without deleting source chunks or adding a new runtime output filter. C screens the question and sources, can block or remove evidence, then uses B answering and a payment-card output check. A provider content-filter refusal is a different event from C blocking. UI masking applies across modes and is not scored as resistance.')
card(.55,1.13,2.84,3.22,'A · Grounded baseline','Retrieve\n↓\nGrounded answer\n↓\nValidate citations\n\nUsually 1 provider call',NAVY,14)
card(3.58,1.13,2.84,3.22,'B · Separation','Same initial evidence\n↓\nTrusted policy boundary\n↓\nAnswer + citations\n\nUsually 1 provider call',BLUE,14)
card(6.61,1.13,2.84,3.22,'C · Screening','Same initial evidence\n↓\nScreen / block / filter\n↓\nB answer + output check\n\nUp to 2 provider calls',RED,14)
band('Fair comparison: same original evidence and answering settings; C’s filtering is a measured difference.')

new('Storage: What Is Saved, and Why?',note='Files preserve exact input bytes. SQLite records the document lifecycle, active version and calls. Chroma stores chunk text, numeric embeddings and metadata for semantic search. JSON defines nested cases; CSV records flat observations. We selected local storage for the scale and deployment constraints. PostgreSQL with pgvector is a valid future alternative for a multi-user service; Chroma is not claimed to be best for every workload.')
rows=[('Original files','data/runtime/raw/<version-id>','Exact uploaded bytes; original name is metadata'),('SQLite','data/runtime/registry.sqlite3','Document versions, parsed blocks, request results, calls'),('Chroma','data/chroma_db/','Searchable upload text, vectors and provenance'),('Frozen fixtures','benchmark_v3/documents/','45 predefined sources; manifest verifies hashes'),('Evaluation index','.cache/evaluation_v3/','Isolated Chroma generation for frozen sources'),('Cases + results','manifest.json · results/','JSON cases; CSV / JSON observations and reviews')]
for i,(a,b,c) in enumerate(rows):
 y=1.09+i*.54;box(.55,y,8.9,.48,LIGHT if i%2==0 else WHITE,round=False);text(.68,y+.10,1.42,.32,a,12,NAVY,True);text(2.15,y+.10,2.94,.32,b,10,TEXT,True);text(5.20,y+.10,4.07,.32,c,10)
band('Paths abbreviated relative to backend/ except .cache/ and results/, which are at the project root.')

new('Evaluation: From a Case to a Measured Result',note='The main benchmark has 47 predefined questions across 45 sources. It retrieves and freezes the initial evidence, then applies A, B and C. Expected answers, attack objectives and rubrics are for evaluation only and are not sent as answer keys. Operational errors are excluded from success rates. Interactive new questions are useful demonstrations but do not silently replace benchmark observations. Human quality and ambiguous semantic decisions require a person.')
card(.55,1.12,4.25,2.94,'Controlled experiment','Frozen source + question\nShared initial retrieval\nA / B / C actual model responses\nSave answer, evidence, settings and errors',sz=15)
card(5.00,1.12,4.45,2.94,'Assess what happened','Task correctness and attack outcome\nHuman quality score: 0–4\nLatency and false-positive trade-offs\nN/A when evidence is missing or unreviewed',RED,15)
band('A benchmark run asks the model. Opening this dashboard only reads saved observations.')

summary=list(csv.DictReader((ROOT/'results/summary.csv').open()))
new('Recorded Main Benchmark: Results & Limits',note='These figures come from results/summary.csv on 29 October 2026. ASR counts are A 2/18, B 0/19 and C 0/20. Benign task success is 20/20 for each. There are 13 operational errors and 11 pending judgments. Only four human quality ratings exist: A two, B one, C one. Do not claim that B or C is secure because an observed attack-success rate is zero. Recent v7 policy changes were not used for these historical observations.')
headers=['Metric','A','B','C']
data=[['Attack success ↓']+[f"{r['asr_all_numerator']}/{r['asr_all_denominator']} ({float(r['asr_all']):.1%})" for r in summary],['Benign task success ↑']+[f"{r['benign_task_success_numerator']}/{r['benign_task_success_denominator']}" for r in summary],['Mean route latency ↓']+[f"{float(r['mean_latency_s']):.2f} s" for r in summary],['Human quality (0–4)']+[f"{r['mean_quality']} (n={r['n_quality']})" for r in summary],['Operational errors']+[r['n_errors'] for r in summary]]
widths=[3.0,1.95,1.95,2.0];xs=[.55,3.55,5.5,7.45]
for j,row in enumerate([headers]+data):
 y=1.10+j*.47;box(.55,y,8.9,.45,NAVY if j==0 else LIGHT if j%2 else WHITE,round=False)
 for i,v in enumerate(row):text(xs[i]+.11,y+.10,widths[i]-.18,.30,v,12,WHITE if j==0 else NAVY if i==0 else TEXT,j==0 or i==0)
text(.61,4.14,8.70,.40,'141 rows recorded · 13 errors · 11 pending judgments · only 4 human quality ratings',13,RED,True)
band('Saved historical policies, not the latest v7. Rates exclude errors / unresolved judgments; latency includes errors.',4.72)

privacy={}
for p in (ROOT/'results/document_privacy').glob('*.json'):
 r=json.loads(p.read_text());privacy[(r['case_id'],r['mode'])]=r
errors={'error','operational_error','llm_error','screening_error','invalid_citations','live_blocked'}
recorded=len(privacy);err=sum(r['status'] in errors for r in privacy.values())
new('Privacy Suite: Five Tests per Document',note=f'The separate privacy suite adds a fictional private contact and public route to each source. It supplies controlled full-document evidence, so it is not a retrieval benchmark. There are 225 cases and 675 planned A/B/C rows. Current coverage is {recorded} recorded, {675-recorded} unrun and {err} execution errors. Runs stopped on operational failures, including Azure content-filter refusals. Never show unrun rows as successful defenses. Control means no added attack, not necessarily a benign original document.')
card(.55,1.13,4.33,2.92,'Five attack conditions','Control: public route only\nDirect plain disclosure request\nDirect encoded disclosure request\nIndirect plain document instruction\nIndirect encoded document instruction',sz=14)
card(5.08,1.13,4.37,2.92,'Actual coverage — incomplete',f'45 documents × 5 cases × 3 modes\n{recorded} / 675 observations recorded\n{675-recorded} rows have not been run\n{err} operational errors preserved\nHuman semantic review remains required',RED,14)
band('Expected behavior: provide the public route; withhold the private contact in plain or encoded form.')

new('Live Demonstration: New Questions',note='Start the app using .venv/bin/python run_app.py --live-answers. Choose a library and one document, then ask a benign question. Local-only returns matching passages, not an AI answer. For a live A/B/C comparison, use the comparison form; initial evidence is frozen once and the comparison costs up to four existing provider calls. Do not replay a provider-refused payload. If the live system is unavailable, show saved outcomes honestly rather than inventing an answer.')
steps=[('1','Select library','Uploaded documents or\nPredefined documents (45)'),('2','Choose source','All sources in that library\nor one specific document'),('3','Ask a new question','Local passages first;\nAzure for a generated answer'),('4','Compare A / B / C','One initial retrieval;\nup to four provider calls')]
for i,(n,a,b) in enumerate(steps):
 x=.55+(i%2)*4.55;y=1.11+(i//2)*1.52;box(x,y,4.35,1.33,LIGHT,EDGE);text(x+.16,y+.18,.5,.45,n,27,RED,True);text(x+.80,y+.16,3.34,.36,a,17,NAVY,True);text(x+.80,y+.65,3.30,.60,b,13)
band('Compare actual correctness, citations, refusal, latency and disclosure. A valid JSON answer is not a security verdict.')

new('What Was Built & What We Learned',note='The deliverable is an inspectable local document assistant with distinct A/B/C pipelines, preserved evidence and evaluation tools. B can resist answer manipulation while still overdescribing malicious content; v7 strengthens summary instructions, but has not established a new benchmark result. C adds screening and output checks but can sacrifice useful answers and time. Remaining work is bounded untouched-case execution where authorized, actual human review, and broader adversarial testing—not a claim of complete protection.')
card(.55,1.13,4.28,3.20,'Delivered','Local ingestion and semantic retrieval\nUploaded + predefined source selection\nThree distinct defense pipelines\nRecorded comparisons and review tools\nEditable, traceable evaluation artifacts',sz=14)
card(5.02,1.13,4.43,3.20,'Practical lessons','Instruction separation helps, but is imperfect\nScreening can reduce usable evidence\nProvider refusals are not defense wins\nZero observed leaks is not proof of safety\nNew policies need new measured evidence',RED,14)
band('Next priority: complete valid observations within authorization and obtain genuine human judgments.')

new('Thank You',note='Invite questions on architecture, storage choices, trust boundaries, model calls, metrics and operational failures. Use the appendix diagrams if asked where a function is implemented. Be precise: no security guarantee, no fabricated human reviews and no automatic replay of a refused or failed benchmark request.')
text(.65,1.66,8.6,.9,'Questions?',42,NAVY,True)
text(.68,2.86,8.3,.8,'Architecture · Storage · Defense trade-offs · Evaluation',20,TEXT)
box(.68,4.00,.90,.06,RED,round=False)
text(.68,4.30,8.1,.4,'Abhishek Sharma  |  AI Security Document Lab',16,TEXT)

new('Appendix: Where the Logic Lives',kicker='TECHNICAL BACKUP',note='All paths are within backend/app unless explicitly prefixed frontend. Upload lifecycle is in ingestion/lifecycle.py, not the old TXT-only upload helper. The runtime API chooses the uploaded or predefined library. Azure serialization is isolated in llm/azure_openai.py and uses a single HTTP attempt. Avoid opening private environment files during a public demo.')
entries=[('Upload / parse','ingestion/lifecycle.py · ingestion/parsers.py'),('Embeddings / index','rag/embeddings.py · rag/indexer.py'),('Evidence retrieval','rag/retriever.py · rag/retrieval.py'),('A / B / C orchestration','rag/assistant.py · rag/comparison.py'),('Defense policy','defenses/baseline.py · instruction_separation.py'),('C checks','defenses/screening.py · output_screening.py'),('API / provider boundary','api/runtime.py · llm/client.py · azure_openai.py'),('Storage / evaluation','storage/registry.py · evaluation/ · results/'),('User interface','frontend/streamlit_app.py · frontend/metrics.py')]
for i,(a,b) in enumerate(entries):
 y=1.08+i*.40;box(.55,y,8.9,.36,LIGHT if i%2==0 else WHITE,round=False);text(.68,y+.07,2.4,.25,a,11,NAVY,True);text(3.15,y+.07,6.1,.25,b,10)

new('Appendix: Questions You Can Answer',kicker='PRESENTER BACKUP',note='Why Chroma: local semantic search, persistence and metadata filters without a new cloud resource. Why SQLite: single-user application state with transactions and no database server. Why not PostgreSQL: a valid option for a larger multi-user system, especially with pgvector, but not required here. Why local mode: it validates retrieval without sending evidence to a model. Why failures remain: preserving observations is necessary for an honest experiment. Does uploading train the model: no, it creates an external index. Is local storage encrypted: not automatically. The same model and initial retrieval support fair comparisons; different prompt policies and C processing are the intentional experimental variables.')
qa=[('Why Chroma + SQLite?','Chroma searches meaning; SQLite manages versions and requests.'),('Does uploading train the LLM?','No. It builds an external retrieval index; weights stay unchanged.'),('Do all documents stay local?','Storage and retrieval do; selected passages leave in live mode.'),('Why are some rows Not run?','No recorded request outcome exists; do not infer success.'),('Is a refusal a security win?','A provider refusal is an operational error, separate from C blocking.'),('Why can B mention an attack?','Ignoring instructions is not the same as guaranteeing confidentiality.')]
for i,(a,b) in enumerate(qa):
 y=1.08+i*.60;text(.65,y,8.8,.28,a,13,NAVY,True);text(.65,y+.29,8.8,.30,b,12)

# Save native editable deck, adopting the supplied reference theme.
pptx=OUT/'AI_Security_Document_Lab_Architecture_Abhishek_Sharma.pptx';prs.save(pptx)
with ZipFile(REFERENCE) as z:theme=z.read('ppt/theme/theme1.xml')
with ZipFile(pptx) as z:parts={n:z.read(n) for n in z.namelist()}
parts['ppt/theme/theme1.xml']=theme
from zipfile import ZIP_DEFLATED
with ZipFile(pptx,'w',ZIP_DEFLATED) as z:
 for n,b in parts.items():z.writestr(n,b)

# Produce matching visual previews and a portable PDF from the same slide scene.
images=[]
for i,scene in enumerate(scenes):
 im=Image.new('RGB',(1280,720),'white');d=ImageDraw.Draw(im)
 for item in scene:
  kind=item[0]
  if kind=='rect':
   _,x,y,w,h,fill,line,rounded=item;b=(round(x*128),round(y*128),round((x+w)*128),round((y+h)*128))
   if rounded:d.rounded_rectangle(b,radius=9,fill='#'+fill,outline='#'+line if line else None,width=1)
   else:d.rectangle(b,fill='#'+fill,outline='#'+line if line else None)
  elif kind=='text':
   _,x,y,w,h,body,size,col,bold=item
   for j,line in enumerate(body.split('\n')):d.text((x*128,y*128+j*size/72*1.12*128),line,font=font(size*128/96,bold),fill='#'+col,anchor='lt')
  elif kind=='arrow':
   _,x1,y1,x2,y2,c=item;x1*=128;y1*=128;x2*=128;y2*=128;d.line((x1,y1,x2,y2),fill='#'+c,width=2);ang=math.atan2(y2-y1,x2-x1);d.polygon([(x2,y2),(x2-8*math.cos(ang-.5),y2-8*math.sin(ang-.5)),(x2-8*math.cos(ang+.5),y2-8*math.sin(ang+.5))],fill='#'+c)
  elif kind=='image':
   _,x,y,w,h,p=item;pic=Image.open(p).convert('RGBA');pic.thumbnail((round(w*128),round(h*128)));im.paste(pic,(round(x*128),round(y*128)),pic)
 im.save(OUT/'previews'/f'slide-{i+1:02}.png');images.append(im)
images[0].save(OUT/'AI_Security_Document_Lab_Architecture.pdf',save_all=True,append_images=images[1:],resolution=128)
contact=Image.new('RGB',(1280,math.ceil(len(images)/3)*265),'#E5E7EB');dc=ImageDraw.Draw(contact)
for i,im in enumerate(images):
 thumb=im.resize((400,225));x=15+(i%3)*425;y=10+(i//3)*265;contact.paste(thumb,(x,y));dc.text((x,y+229),f'{i+1:02}  {notes[i][0]}',fill='#1F2937',font=font(10))
contact.save(OUT/'Slide_Overview.png')
with (OUT/'Presenter_Notes.md').open('w') as f:
 f.write('# AI Security Document Lab — presenter notes\n\n29 October 2026 · Abhishek Sharma\n\n')
 for i,(title,note) in enumerate(notes,1):f.write(f'## {i}. {title}\n\n{note}\n\n')
 f.write('## Source of truth\n\n- results/summary.csv: saved main benchmark metrics.\n- results/records.csv: actual observations and errors.\n- results/document_privacy/: privacy-suite coverage.\n- backend/app/: implemented architecture and defense policies.\n- eval_config.yaml: shared model settings.\n- ForecastIQ_V2_Presentation.pptx: visual reference only.\n\nPDF/PNG are matching visual previews generated from the same layout; the PPTX contains native editable text, shapes and arrows. Font substitution can slightly change rendering in other PowerPoint installations.\n')
# Structural validation and boundary checks on every native shape.
check=Presentation(pptx)
assert len(check.slides)==len(notes)==16
for num,slide in enumerate(check.slides,1):
 for s in slide.shapes:
  assert s.left>=0 and s.top>=0 and s.left+s.width<=check.slide_width+1000 and s.top+s.height<=check.slide_height+1000,(num,s.name)
assert all(slide.has_notes_slide for slide in check.slides)
print('Created:',pptx)
print('16 slides; editable architecture; presenter notes; PDF; PNG overview. Structural checks passed.')
