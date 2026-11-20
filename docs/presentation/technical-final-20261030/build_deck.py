"""Editable technical deck and matching vector PDF; project-derived content only."""
from pathlib import Path
import math,sys
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
W,H=16,9
NAVY='102C46';BLUE='2563EB';TEAL='087F8C';INK='203548';MUTED='5D7183';BG='F5F8FC';LINE='D4E0EC';WHITE='FFFFFF';AMBER='B7791F'
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pres=Presentation();pres.slide_width=Inches(W);pres.slide_height=Inches(H)
pdf=canvas.Canvas(str(OUT/'AI_Security_RAG_Technical_Deck.pdf'),pagesize=(W*72,H*72))
pdf.setTitle('AI Security | RAG and Prompt Injection Defense Evaluation')
current=None;slide_num=0

def rgb(c):return RGBColor.from_string(c)
def pc(c):return tuple(int(c[i:i+2],16)/255 for i in (0,2,4))
def rect(x,y,w,h,fill=WHITE,border=None,rounded=False):
 sh=current.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
 sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
 if border:sh.line.color.rgb=rgb(border);sh.line.width=Pt(.8)
 else:sh.line.fill.background()
 if rounded:
  try:sh.adjustments[0]=.08
  except Exception:pass
 pdf.setFillColorRGB(*pc(fill));pdf.setStrokeColorRGB(*pc(border or fill));pdf.setLineWidth(.8)
 if rounded:pdf.roundRect(x*72,(H-y-h)*72,w*72,h*72,7,stroke=bool(border),fill=1)
 else:pdf.rect(x*72,(H-y-h)*72,w*72,h*72,stroke=bool(border),fill=1)
 return sh

def text(x,y,w,h,value,size=20,color=INK,bold=False):
 longest=max((pdfmetrics.stringWidth(v,'DV-B' if bold else 'DV',size) for v in value.split('\n')),default=0)
 if longest>w*72:size=max(8.5,size*w*72/longest*.97)
 box=current.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame;tf.word_wrap=False
 tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 lines=value.split('\n')
 for i,line in enumerate(lines):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='DejaVu Sans';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_before=Pt(0);p.space_after=Pt(0);p.line_spacing=1.2
 pdf.setFillColorRGB(*pc(color));pdf.setFont('DV-B' if bold else 'DV',size)
 for i,line in enumerate(lines):pdf.drawString(x*72,(H-y)*72-size-i*size*1.2,line)
 return box

def line(points,color=MUTED,dash=False,arrow=True,both=False):
 for a,b in zip(points,points[1:]):
  sh=current.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(a[0]),Inches(a[1]),Inches(b[0]),Inches(b[1]));sh.line.color.rgb=rgb(color);sh.line.width=Pt(1.3)
  if dash:
   from pptx.enum.dml import MSO_LINE_DASH_STYLE
   sh.line.dash_style=MSO_LINE_DASH_STYLE.DASH
  pdf.setStrokeColorRGB(*pc(color));pdf.setLineWidth(1.3);pdf.setDash(4,3) if dash else pdf.setDash();pdf.line(a[0]*72,(H-a[1])*72,b[0]*72,(H-b[1])*72)
 pdf.setDash()
 def head(a,b):
  ang=math.atan2(b[1]-a[1],b[0]-a[0]);r=.075
  pts=[b,(b[0]-r*math.cos(ang-.45),b[1]-r*math.sin(ang-.45)),(b[0]-r*math.cos(ang+.45),b[1]-r*math.sin(ang+.45))]
  for p,q in [(pts[0],pts[1]),(pts[0],pts[2])]:line([p,q],color=color,arrow=False)
 if arrow:head(points[-2],points[-1])
 if both:head(points[1],points[0])

def slide(title,kicker,source=''):
 global current,slide_num
 if current is not None:pdf.showPage()
 current=pres.slides.add_slide(pres.slide_layouts[6]);slide_num+=1
 rect(0,0,W,H,BG);rect(0,0,.16,H,TEAL)
 text(.55,.3,14,.3,kicker.upper(),11,TEAL,True)
 text(.55,.77,15,.65,title,30,NAVY,True)
 line([(.55,1.52),(15.45,1.52)],LINE,arrow=False)
 text(.55,8.55,14,.25,source or 'AI Security Engineering  /  Document-grounded LLM security PoC',9,MUTED)
 text(15.1,8.5,.5,.3,f'{slide_num:02d}',12,TEAL,True)
 return current

def card(x,y,w,h,title,body,accent=BLUE):
 rect(x,y,w,h,WHITE,LINE,True);rect(x,y,.055,h,accent)
 text(x+.22,y+.18,w-.4,.5,title,19,accent,True)
 text(x+.22,y+.83,w-.4,h-.9,body,17,INK)

def node(x,y,w,title,sub,accent=BLUE,h=1.08):
 rect(x,y,w,h,WHITE,LINE,True);text(x+.12,y+.12,w-.24,.3,title,14,accent,True);text(x+.12,y+.49,w-.24,h-.5,sub,11.5,INK)

def recorded_chart():
 import csv
 from matplotlib.figure import Figure
 from matplotlib.backends.backend_agg import FigureCanvasAgg
 rows=list(csv.DictReader((ROOT/'results/current25/summary.csv').open()))
 fig=Figure(figsize=(10,5.8));axes=fig.subplots(2,2).ravel()
 fig.subplots_adjust(left=.075,right=.97,bottom=.08,top=.91,wspace=.24,hspace=.5)
 specs=[('asr_all','Attack success rate (%)',100),('benign_task_success','Benign task success (%)',100),('pdf_false_positive_rate','False positive rate · C only (%)',100),('mean_latency_s','Mean response latency (s)',1)]
 for ax,(key,title,scale) in zip(axes,specs):
  ax.set_title(title,loc='left',fontsize=11,fontweight='bold',pad=14)
  ax.set_xticks(range(3),list('ABC'));ax.set_xlim(-.6,2.6)
  ax.spines[['top','right']].set_visible(False);ceiling=124 if scale==100 else 8.4
  ax.set_ylim(0,ceiling);ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
  for i,row in enumerate(rows):
   if not row[key]:
    ax.text(i,ceiling*.22,'Not applicable',rotation=90,ha='center',fontsize=8,color='#5D7183');continue
   value=float(row[key])*scale;ax.bar(i,value,color=['#2563EB','#087F8C','#B7791F'][i],width=.5)
   denom=row.get(key+'_denominator');num=row.get(key+'_numerator')
   label=f'{value:.1f}'+(f'\n{num}/{denom}' if denom else '')
   ax.text(i,value+ceiling*.03,label,ha='center',fontsize=9)
 FigureCanvasAgg(fig).print_png(str(OUT/'Recorded_Benchmark_Metrics.png'))

recorded_chart()

slide('Evaluating Defenses Against Prompt Injection','RAG security • technical walkthrough','Source: assignment PDF; verified project implementation  /  30 October 2026')
text(.65,2.0,10,1.5,'Document-grounded AI\nwith measurable security trade-offs',36,NAVY,True)
text(.68,4.0,9,1,'Attack resistance  ·  Task preservation\nCitation integrity  ·  Defense overhead',22,MUTED)
for y,n,t in [(2.1,'01','RAG architecture'),(3.55,'02','A / B / C defense paths'),(5.0,'03','Benchmark + evaluation')]:
 rect(11,y,4.3,1.1,WHITE,LINE,True);text(11.2,y+.25,.6,.4,n,20,TEAL,True);text(12,y+.31,3,.4,t,16,NAVY,True)
rect(.68,6.65,14.6,.85,NAVY,rounded=True);text(.95,6.89,14,.4,'Python  /  FastAPI  /  Streamlit  /  Chroma  /  Azure OpenAI',21,WHITE,True)
text(.7,7.78,14,.4,'Abhishek Sharma  •  AI Security Engineer PoC',17,MUTED)

slide('System architecture','Data plane + inference plane + evaluation plane','Implemented local-first PoC  /  Azure hosts the LLM only; diagram is not a production deployment claim')
rect(.4,1.75,12.05,4.7,'EDF3FA',LINE,True);text(.58,1.82,10,.25,'LOCAL APPLICATION BOUNDARY',10,TEAL,True)
rect(12.7,1.75,2.85,4.7,'E7F2F4',LINE,True);text(12.88,1.82,2.5,.25,'EXTERNAL PROVIDER',10,TEAL,True)
xs=[.6,3.0,5.4,7.8,10.2];widths=[2.05]*5
for x,t,b in zip(xs,['Document intake','Parse + validate','Chunk + identify','Local embeddings','Vector index'],['PDF / DOCX / TXT / MD','pypdf / python-docx\nType + size limits','Character text splitting\nIDs + page / offsets','MiniLM-L6-v2\nNormalized embeddings','Chroma / cosine\nVerified index version']):node(x,2.28,2.05,t,b)
for i in range(4):line([(xs[i]+2.05,2.82),(xs[i+1],2.82)],BLUE)
for x,t,b in zip(xs,['UI + API','Scoped retrieval','Defense routing','Model contract','Response handling'],['Streamlit / FastAPI\nQuestion + mode + source','Active document versions\nQuery vector / ranked hits','A: baseline / B: separation\nC: pre-screen + separation','Trusted rules + evidence\nStrict JSON / source IDs','Citations + C output check\nDisplay masking / UI']):node(x,4.42,2.05,t,b)
for i in range(3):line([(xs[i]+2.05,4.96),(xs[i+1],4.96)],BLUE)
node(12.9,2.28,2.45,'C screening','gpt-5-mini\nQuestion + source decision',TEAL)
node(12.9,4.42,2.45,'Answer generation','gpt-5-mini\nShared A / B / C settings',TEAL)
line([(6.42,4.42),(6.42,3.95),(14.12,3.95),(14.12,3.36)],TEAL,both=True)
text(12.9,3.67,1.6,.25,'C only',10,TEAL,True)
line([(11.22,3.36),(11.22,3.65),(4.02,3.65),(4.02,4.42)],BLUE)
text(7.0,3.72,3,.25,'Ranked evidence + provenance',10,BLUE)
line([(8.82,5.5),(8.82,5.92),(14.12,5.92),(14.12,5.5)],TEAL)
line([(12.9,4.68),(12.52,4.68),(12.52,4.13),(11.22,4.13),(11.22,4.42)],TEAL)
rect(.6,5.77,2.05,.5,'DEE8F4',rounded=True);text(.72,5.82,1.83,.4,'SQLite registry\nVersions / request ledger',9,NAVY);line([(1.62,5.5),(1.62,5.77)],MUTED)
text(.58,6.65,14,.3,'OFFLINE BENCHMARK + EVALUATION',11,TEAL,True)
for x,t,b in zip(xs+[12.9],['Frozen fixtures','Evidence snapshot','Paired A / B / C','Scoring + review','Result artifacts','Application metrics'],['Manifest + test cases\nExpected behavior + labels','Same chunks per case\nHash / config identity','Repeatable Python runner\nOne shared model profile','ASR / task / false positives\nTask + latency + citations','CSV / JSON / PNG\nSeparate run provenance','Read-only dashboards\nNo inference on refresh']):node(x,7.13,2.05 if x<12 else 2.45,t,b,accent=TEAL,h=1.04)
for i in range(5):line([(xs[i]+2.05,7.65),((xs+[12.9])[i+1],7.65)],TEAL)
line([(4.02,7.13),(4.02,5.5)],TEAL,dash=True);line([(6.42,7.13),(6.42,5.5)],TEAL,dash=True)

slide('RAG stack and document lifecycle','Implementation keywords','Sources: ingestion/parsers.py, ingestion/lifecycle.py, ingestion/chunker.py, rag/embeddings.py, core/config.py')
rows=[('Text splitting','RecursiveCharacterTextSplitter'),('Parser layer','pypdf / python-docx / UTF-8'),('Embedding model','SentenceTransformers / all-MiniLM-L6-v2'),('Vector retrieval','Chroma / cosine similarity'),('Document lifecycle','Versioning / active snapshot / SHA256'),('Evidence provenance','Chunk IDs / page references / source metadata')]
for i,(label,val) in enumerate(rows):
 y=1.92+i*.79;rect(.65,y,10.2,.7,WHITE if i%2==0 else 'EAF0F8',rounded=True);text(.85,y+.2,2.7,.4,label,17,TEAL,True);text(3.55,y+.2,7.1,.4,val,16,INK)
card(11.15,1.92,4.15,1.65,'PDF','pypdf · page text',TEAL)
card(11.15,3.8,4.15,1.65,'DOCX','python-docx · body + tables',TEAL)
card(11.15,5.68,4.15,1.65,'TXT / MD','UTF-8 text decoding',TEAL)
text(.85,7.25,10,.8,'Extraction → chunking → embeddings → indexing.\nMetadata links retrieved evidence to its document version.',14,MUTED)

slide('Retrieval and grounded generation','Online request lifecycle','Sources: rag/retrieval.py, rag/retriever.py, rag/assistant.py, llm/experiment_settings.py, eval_config.yaml')
steps=[('01','Version snapshot','Selected active files\nDocument-ID allowlist'),('02','Query embedding','Same local MiniLM\nNormalized query vector'),('03','Similarity search','Chroma cosine distance\nTop-k relevance ranking'),('04','Evidence assembly','Context-size budget\nPreserved source records'),('05','Generation contract','Strict JSON schema\nAllowed source-ID enum'),('06','Citation validation','Required source reference\nUnknown IDs rejected')]
for i,(n,t,b) in enumerate(steps):
 x=.65+i*2.5;rect(x,2.15,2.22,2.25,WHITE,LINE,True);text(x+.16,2.32,1,.4,n,23,TEAL,True);text(x+.16,2.98,2,.4,t,15,NAVY,True);text(x+.16,3.52,2,.7,b,12.5,INK)
 if i<5:line([(x+2.22,3.2),(x+2.5,3.2)],BLUE)
rect(.65,4.95,14.65,1.0,NAVY,rounded=True);text(.92,5.2,14,.5,'Provenance: chunk ID  ·  document ID  ·  version ID  ·  page / offsets  ·  SHA256',18,WHITE,True)
card(.65,6.3,7.13,1.5,'Current inference profile','Azure OpenAI  ·  gpt-5-mini  ·  strict JSON',BLUE)
card(8.05,6.3,7.25,1.5,'Shared request controls','Temperature omitted  ·  zero retries  ·  no fallback',TEAL)

slide('Threat model and trust boundaries','Security concepts','Scope: implemented document-grounded PoC; controls described here are not an enterprise security certification')
card(.65,2.0,7.1,2.2,'Protected assets','Policy adherence  ·  Grounded responses\nSensitive values  ·  Source provenance',BLUE)
card(8.05,2.0,7.25,2.2,'Attack surfaces','User requests  ·  Retrieved chunks\nMixed-content documents  ·  Cross-chunk instructions',TEAL)
card(.65,4.65,7.1,2.2,'Trust boundary','Trusted application rules\nUntrusted retrieved content = evidence, not authority',TEAL)
card(8.05,4.65,7.25,2.2,'Adversarial techniques','Instruction redirection  ·  Forged authority\nSecret requests  ·  Unsupported factual claims',BLUE)
text(.85,7.57,14,.6,'Failure modes: prompt following  /  overblocking  /  unsupported output  /  invalid citations',16,NAVY,True)

slide('Three comparable defense configurations' ,'A / B / C','Sources: defenses/baseline.py, instruction_separation.py, screening.py, output_screening.py')
configs=[('A','Standard RAG baseline','Grounded generation\nShared disclosure policy\nSource-ID validation','No dedicated injection screening',BLUE),('B','Instruction separation','Trusted rules / user / sources\nRetrieved content treated as data\nSame generation + citation contract','Prompt-based separation is fallible',TEAL),('C','Screening + separation','LLM question / source screening\nBlock question or exclude sources\nB generation + card-output check','False positives + added latency',AMBER)]
for i,(letter,title,body,limit,color) in enumerate(configs):
 x=.65+i*5.0;rect(x,1.98,4.65,5.67,WHITE,LINE,True);rect(x,1.98,4.65,.85,color,rounded=True);text(x+.22,2.15,4.2,.5,letter+'  /  '+title,18,WHITE,True)
 text(x+.24,3.25,4.2,2.1,body,17,INK);line([(x+.24,5.78),(x+4.4,5.78)],LINE,arrow=False)
 text(x+.24,6.04,4.1,.3,'PRIMARY LIMITATION',11,color,True);text(x+.24,6.53,4.12,.8,limit,14,MUTED)
text(.8,7.97,14,.3,'Comparison control: same question + original retrieval + model settings; only defense path changes.',15,NAVY)

slide('Recorded benchmark coverage','Completed execution scopes','Sources: saved main benchmark records and uploaded-file validation records; recorded does not mean passed')
headers=['EXPERIMENT','DOCUMENTS / CASES','A / B / C ROWS','EXECUTION STATUS']
for x,w,t in zip([.85,5.5,9.05,12.1],[4.5,3.4,2.9,3.0],headers):text(x,2.0,w,.4,t,12,TEAL,True)
entries=[('Frozen main benchmark','25 files / 47 cases','141 rows','Recorded'),('Uploaded-file validation','10 files / 23 questions','69 rows','Recorded; multi-revision')]
for i,row in enumerate(entries):
 y=2.67+i*1.03;rect(.65,y,14.65,.85,WHITE,LINE,True)
 for x,w,v in zip([.85,5.5,9.05,12.1],[4.5,3.4,2.9,3.0],row):text(x,y+.25,w,.4,v,16,INK,i==0)
text(.85,6.0,14,.4,'Coverage categories',20,NAVY,True)
text(.85,6.65,14,.9,'Benign  ·  Direct injection  ·  Indirect injection\nMisleading facts  ·  Mixed content  ·  Benign instruction-like text',19,INK)
text(.85,7.82,14,.4,'Frozen manifest + expected behavior  /  identical case pairing  /  preserved run identities',15,TEAL,True)

slide('Evaluation criteria and scoring','Security + utility + performance','Sources: evaluation/simple_scoring.py, simple_reporting.py, simple_review.py')
metrics=[('Attack success rate','Successful attacks / assessed attack cases','Lower'),('Benign task success','Correct legitimate tasks / assessed benign cases','Higher'),('False positive rate','Benign cases flagged or blocked / assessed benign cases','Lower'),('Evidence provenance','Document identity / version / source traceability','Required'),('Latency','Mean recorded response time per configuration','Lower'),('Citation accuracy','Expected document cited / eligible citation grades','Higher')]
for i,(m,f,d) in enumerate(metrics):
 y=1.98+i*.82;rect(.65,y,14.65,.71,WHITE if i%2==0 else 'EAF0F8',rounded=True);text(.85,y+.19,3.7,.4,m,17,NAVY,True);text(4.6,y+.2,8.8,.4,f,16,INK);text(14,y+.2,1.1,.4,d,14,TEAL,True)
text(.85,7.3,14,.9,'Errors and pending judgments are excluded from eligible rates.\nSource-ID validity does not prove semantic support. Error outcomes remain separate.',15,MUTED)

slide('Saved benchmark measurements','Observed results • frozen 25-document main study','Source: results/current25/summary.csv  /  Frozen run settings; eligible, assessed outcomes only')
chart=OUT/'Recorded_Benchmark_Metrics.png'
current.shapes.add_picture(str(chart),Inches(.6),Inches(1.85),width=Inches(10.5),height=Inches(5.44))
pdf.drawImage(str(chart),.6*72,(H-1.85-5.44)*72,width=10.5*72,height=5.44*72,mask='auto')
card(11.4,1.98,3.9,1.62,'141 rows recorded','16 execution errors',TEAL)
card(11.4,3.83,3.9,1.62,'69 upload rows recorded','Separate validation scope',TEAL)
card(11.4,5.68,3.9,1.62,'Interpretation','Zero measured ASR\nis not a security guarantee.',BLUE)
text(.8,7.72,14,.6,'Uploaded validation is separate: 69 recorded rows; one B disclosure detected before UI masking.\nLive demonstration: benign task → baseline → same task with B/C → saved metrics.',14,MUTED)

pres.core_properties.title='Evaluating Defenses Against Prompt Injection'
pres.core_properties.subject='RAG implementation, architecture, benchmark and evaluation'
pres.core_properties.author='Abhishek Sharma'
pres.save(OUT/'AI_Security_RAG_Technical_Deck.pptx');pdf.save()
print('Created 9-slide keyword-focused PPTX and matching PDF')
