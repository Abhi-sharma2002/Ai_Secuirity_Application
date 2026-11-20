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

slide('Evaluating Defenses Against Prompt Injection','AI Security Engineer • document-based RAG PoC','Based on Abhishek Sharma.pdf  /  Verified project implementation  /  30 October 2026')
text(.7,2.15,14,1.25,'Security  ·  Usefulness  ·  Grounded generation',34,NAVY,True)
card(.7,4.0,4.65,2.4,'Build','Document retrieval\nLLM generation\nSupporting references',BLUE)
card(5.65,4.0,4.65,2.4,'Defend','Baseline comparison\nInstruction separation\nInput / output screening',TEAL)
card(10.6,4.0,4.65,2.4,'Evaluate','Attack resistance\nNormal task preservation\nFalse positives + latency',BLUE)
text(.85,7.33,14,.5,'Abhishek Sharma  /  Python  /  FastAPI  /  Streamlit',20,MUTED)

slide('Simple end-to-end architecture','Ingestion → retrieval → defenses → evaluation','Solid arrows: data flow  /  Dashed arrow: repeatable benchmark input  /  LLM runs on Azure; retrieval and storage are local')
text(.75,1.83,14,.3,'1   LOCAL DOCUMENT INGESTION',12,TEAL,True)
node(.75,2.35,3.9,'Documents','PDF / DOCX / TXT / Markdown',h=1.05)
node(5.25,2.35,4.0,'Parse + chunk','pypdf / python-docx\nRecursiveCharacterTextSplitter',h=1.05)
node(9.85,2.35,5.35,'Embed + index','SentenceTransformers / MiniLM\nChroma / cosine similarity',h=1.05)
line([(4.65,2.87),(5.25,2.87)],BLUE);line([(9.25,2.87),(9.85,2.87)],BLUE)
text(.75,3.82,14,.3,'2   ONLINE RAG + DEFENSES',12,TEAL,True)
xs=[.75,3.75,6.75,9.75,12.75]
for x,t,b in zip(xs,['UI + API','Retrieval','A / B / C','Azure LLM','Response'],['Streamlit / FastAPI','Chroma / cosine / document scope','Baseline / separation / screening','Azure OpenAI / gpt-5-mini','Strict JSON / source IDs']):node(x,4.4,2.45,t,b,h=1.12)
for i in range(4):line([(xs[i]+2.45,4.96),(xs[i+1],4.96)],BLUE)
line([(12.52,3.4),(12.52,3.7),(4.97,3.7),(4.97,4.4)],TEAL)
text(.75,6.03,14,.3,'3   CONTROLLED BENCHMARK + REPORTING',12,TEAL,True)
node(.75,6.6,3.9,'Frozen test cases','Manifest / fixtures / expected labels',TEAL,h=1.1)
node(5.25,6.6,4.0,'Paired evaluation runner','Python / A–B–C / frozen retrieval',TEAL,h=1.1)
node(9.85,6.6,5.35,'Scoring + saved artifacts','CSV / JSON / Matplotlib / PNG',TEAL,h=1.1)
line([(4.65,7.15),(5.25,7.15)],TEAL);line([(9.25,7.15),(9.85,7.15)],TEAL)
line([(7.25,6.6),(7.25,5.52)],TEAL,dash=True)

slide('Technology stack','Project technologies','Verified from the active project implementation')
stack=[('Parsing','pypdf  /  python-docx\nUTF-8',BLUE),('Text splitting','RecursiveCharacterTextSplitter',TEAL),('Embeddings','SentenceTransformers\nall-MiniLM-L6-v2',BLUE),('Retrieval','Chroma  /  cosine similarity\nDocument scoping',TEAL),('Generation','Azure OpenAI  /  gpt-5-mini\nStrict JSON',BLUE),('Traceability','Source IDs  /  page references\nVersion hashes',TEAL)]
for i,(title,keywords,color) in enumerate(stack):
 x=.75+(i%3)*4.9;y=2.08+(i//3)*2.83
 card(x,y,4.55,2.3,title,keywords,color)

slide('Threat model and dataset coverage','Controlled synthetic benchmark','Main benchmark: backend/benchmark_current25/manifest.json  /  At least 20 documents and 30 cases required by the PDF')
card(.75,1.97,6.95,1.75,'Requirement coverage','25 synthetic source files  /  47 test cases',BLUE)
card(8.0,1.97,7.2,1.75,'Untrusted input boundary','User request + retrieved document content',TEAL)
categories=[('Benign','Policies / onboarding / support'),('Direct injection','Explicit instruction override'),('Indirect injection','Embedded task redirection'),('Misleading information','Unsupported factual claims'),('Mixed content','Useful facts + malicious instructions'),('Benign instruction-like text','Quoted examples / awareness material')]
for i,(name,desc) in enumerate(categories):
 x=.75+(i%2)*7.25;y=4.1+(i//2)*1.05;rect(x,y,6.95,.85,WHITE,LINE,True);text(x+.18,y+.13,6.5,.3,name,17,TEAL,True);text(x+.18,y+.5,6.5,.3,desc,14,INK)
text(.95,7.73,14,.4,'Benchmark fixtures are fictional; uploaded-file validation is a separate recorded experiment.',15,MUTED)

slide('A / B / C defense comparison','Baseline + two defensive approaches','Implementation: defenses/baseline.py; instruction_separation.py; screening.py; output_screening.py')
items=[('A · Standard RAG','Grounded generation\nShared disclosure policy\nSource validation','No dedicated injection screener',BLUE),('B · Instruction separation','Trusted rules vs source content\nRetrieved text treated as data\nSame grounding + model contract','Prompt-following can still fail',TEAL),('C · Screening + B','Question / source screening\nBlock or remove flagged inputs\nB generation + card-output check','Overblocking + inference overhead',AMBER)]
for i,(title,body,limit,color) in enumerate(items):
 x=.75+i*4.9;card(x,2.15,4.55,3.8,title,body,color);text(x+.2,6.35,4.15,.4,'LIMITATION',11,color,True);text(x+.2,6.88,4.15,.75,limit,15,MUTED)
text(.95,7.95,14,.3,'A valid structured response is not proof that the answer is safe or factually supported.',15,NAVY)

slide('Repeatable evaluation framework','Predefined expectations + paired execution','Implementation: evaluation/simple_runner.py; simple_scoring.py; simple_reporting.py; saved per-run metadata')
card(.75,2.05,7.0,2.1,'Execution controls','Same question / original evidence / model profile\nFrozen manifest + configuration identity\nSeparate provenance for implementation revisions',BLUE)
card(8.05,2.05,7.15,2.1,'Outcome handling','Errors kept separate from defense blocks\nAmbiguous judgments remain unresolved\nSaved artifacts support repeatable inspection',TEAL)
text(.95,4.72,14,.5,'Per-case record',23,NAVY,True)
text(.95,5.5,14,1.65,'Query  ·  Retrieved document  ·  Attack category  ·  Expected behavior\nActual response  ·  Attack outcome  ·  Legitimate task outcome  ·  Result notes',20,INK)
rect(.75,7.2,14.45,.65,NAVY,rounded=True);text(.95,7.38,14,.3,'Scoring rules are predefined; model outputs and expected labels are stored separately.',16,WHITE)

slide('Evaluation metrics','Measure security and task preservation separately','Metrics defined by the assignment PDF  /  Human review criteria are methodology, not invented measurements')
metrics=[('Attack success rate','Successful attacks / assessed attack cases','Lower'),('Benign task success','Correct normal tasks / assessed benign cases','Higher'),('False positive rate','Benign cases wrongly flagged or blocked','Lower'),('Answer quality','Factual correctness / relevance / review rubric','Review'),('Latency','Mean recorded response time per mode','Lower'),('Citation accuracy','Expected document cited / eligible grades','Higher')]
for i,(metric,meaning,direction) in enumerate(metrics):
 y=2.0+i*.82;rect(.75,y,14.45,.71,WHITE if i%2==0 else 'EAF0F8',rounded=True);text(.95,y+.18,3.8,.35,metric,17,NAVY,True);text(4.8,y+.18,8.5,.35,meaning,16,INK);text(14,y+.18,1,.35,direction,14,TEAL,True)
text(.95,7.4,14,.7,'Exclude errors and unresolved grades from eligible rates.\nCitation identity checks do not establish semantic correctness.',15,MUTED)

slide('Recorded benchmark measurements','Measured outcomes only','Source: results/current25/summary.csv  /  Frozen main run; results are not measurements of every current code revision')
chart=ROOT/'docs/presentation/technical-final-20261030/Recorded_Benchmark_Metrics.png'
current.shapes.add_picture(str(chart),Inches(.65),Inches(1.9),width=Inches(10.45),height=Inches(5.65))
pdf.drawImage(str(chart),.65*72,(H-1.9-5.65)*72,width=10.45*72,height=5.65*72,mask='auto')
card(11.4,2.03,3.8,1.6,'Main benchmark','141 rows / 16 errors',TEAL)
card(11.4,3.92,3.8,1.6,'Uploaded validation','69 recorded rows',TEAL)
card(11.4,5.81,3.8,1.6,'Observed limitation','One B disclosure\nbefore display masking',AMBER)
text(.9,7.77,14,.45,'Zero measured ASR ≠ guaranteed security. Separate experiments are not pooled into one score.',15,NAVY,True)

slide('Assignment requirements → project deliverables','Coverage and justification','Requirements mapping: Abhishek Sharma.pdf  /  References identify implemented modules and recorded artifacts')
rows=[('Document assistant','Upload → retrieval → grounded generation → references'),('Dataset requirements','25 synthetic files / 47 cases / six required categories'),('Three configurations','A baseline / B separation / C screening + B'),('Repeatable framework','Paired runner / predefined labels / per-case records'),('Quantitative comparison','ASR / benign success / false positives / latency / PNGs'),('Quality assessment','Factuality + relevance criteria / explicit human review'),('Technical findings','Saved result records / limitations / revision provenance'),('Final demonstration','Benign task / baseline injection / B–C comparison / trade-offs')]
for i,(requirement,proof) in enumerate(rows):
 y=1.92+i*.7;rect(.75,y,14.45,.6,WHITE if i%2==0 else 'EAF0F8',rounded=True);text(.95,y+.15,4.1,.35,requirement,16,TEAL,True);text(5.1,y+.15,9.85,.35,proof,16,INK)
text(.95,7.86,14,.4,'Central question: which defense best balances attack resistance and legitimate task performance?',16,NAVY,True)

pres.core_properties.title='Prompt Injection Defense Evaluation — Simple Technical Architecture'
pres.core_properties.author='Abhishek Sharma'
pres.save(OUT/'AI_Security_RAG_Technical_Deck.pptx');pdf.save()
print('Created 9-slide keyword-card deck and PDF')
