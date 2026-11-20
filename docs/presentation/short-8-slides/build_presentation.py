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
prs.core_properties.title='AI Security Document Lab — Defense Evaluation'
prs.core_properties.author='Abhishek Sharma'
prs.core_properties.subject='Controlled evaluation of prompt-injection defenses'
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


def flow(title, steps, note, takeaway):
 new(title,note=note)
 for i,(label,body) in enumerate(steps):
  x=.55+(i%3)*3.04;y=1.15+(i//3)*1.56
  card(x,y,2.82,1.42,label,body,BLUE if i<3 else NAVY,12)
  if i%3<2 and i<len(steps)-1:arrow(x+2.84,y+.60,x+3.02,y+.60)
  elif i==2 and len(steps)>3:arrow(8.02,2.48,1.95,2.66)
 band(takeaway)

def two(title,left,right,note, takeaway):
 new(title,note=note)
 card(.55,1.14,4.28,3.22,left[0],left[1],NAVY,15)
 card(5.02,1.14,4.43,3.22,right[0],right[1],BLUE,15)
 band(takeaway)

new('AI Security Document Lab',note='Introduce the project as a local document assistant used to compare prompt-injection defenses. The aim is useful, evidence-based answers while resisting instructions hidden in questions or documents.')
text(.65,1.20,8.5,1.4,'Document RAG and\nprompt-injection defenses',30,NAVY,True)
text(.65,3.03,8.5,.6,'Project flow · A / B / C · Actual evaluation',19,TEXT)
text(.65,4.05,8,.65,'Abhishek Sharma\n29 October 2026',15,MUTED)

two('What the project does',('Normal task','Upload or select a document\nAsk a business question\nRetrieve relevant passages\nReceive an answer with references'),('Security challenge','Questions can contain hostile commands\nDocuments can contain hidden instructions\nAnswers can be manipulated\nDefenses must preserve useful answers'),'Explain direct injection as an attack in the question and indirect injection as an attack in source content. The project compares security and legitimate task completion, rather than treating every refusal as a good answer.','Goal: resist prompt injection while preserving legitimate answers.')

flow('The complete project flow',[('01 · Select document','Upload TXT / MD, text PDF,\nor DOCX; or select a source.'),('02 · Prepare locally','Parse → chunk → embed\n→ verified Chroma index.'),('03 · Retrieve passages','Embed the question locally;\nretrieve up to five passages.'),('04 · Apply A / B / C','Standard RAG, separation,\nor screening plus checks.'),('05 · Generate and validate','Azure gpt-5-mini answers;\nvalidate schema and source IDs.'),('06 · Display and evaluate','Show answer and references;\ncompare saved case outcomes.')],'Indexing happens when preparing documents, not for every question. Streamlit calls FastAPI locally. Parsing, CPU embeddings, Chroma, SQLite, evaluation and charts stay local. Only authorized answering and screening use Azure. Local-only search makes no model request.','Local: parsing, embeddings, retrieval and storage. Azure: authorized answering and screening.')

two('How documents become searchable',('Prepare and index','Split text: 1,000 characters\nKeep 150-character overlap\nCreate CPU MiniLM embeddings\nStore chunks and vectors in Chroma\nVerify IDs, hashes and metadata'),('Retrieve for a question','Select active document versions\nEmbed the question with MiniLM\nRank passages by cosine distance\nKeep up to five relevant passages\nAttach source and version details'),'indexer.py validates chunk structure and checksums, creates a versioned collection, embeds pending chunks and verifies stored records. A verified index establishes consistency, not trustworthy meaning. Retrieval similarity is not factual confidence.','The model receives selected source passages; citation-ID checks do not prove factual correctness.')

new('A / B / C: what changes?',note='A is normal grounded RAG without dedicated injection separation or screening. Basic grounding, references and the standing disclosure rule remain common to all modes. B adds explicit instruction separation without removing chunks. C screens the question and sources, may block or filter, then uses B answering and a payment-card output check. UI masking is shared display behavior, not B resistance.')
card(.55,1.15,2.84,3.20,'A · Standard RAG','Retrieve evidence\n↓\nNormal grounded prompt\n↓\nAnswer + references\n\nOne generation call',NAVY,14)
card(3.58,1.15,2.84,3.20,'B · Separation','Same initial evidence\n↓\nTreat source text as data\n↓\nAnswer + references\n\nOne generation call',BLUE,14)
card(6.61,1.15,2.84,3.20,'C · Screen + check','Screen question + sources\n↓\nBlock or remove flagged text\n↓\nB answer + output check\n\nUp to two calls',RED,14)
band('Same starting evidence and answering settings; the added defense is the treatment difference.')

two('Dataset and evaluation',('Current predefined study','25 versioned document packs\nAll 47 test cases retained\n21 benign + 26 adversarial cases\n141 planned A/B/C rows\nSame model and scoring criteria'),('Five required metrics','Attack success rate\nBenign task success rate\nFalse positive rate\nHuman answer quality\nResponse latency'),'The 25 packs preserve all 45 original extracted source texts, with provenance. Existing cases cover forged authority, obfuscation, cross-chunk attacks, misinformation and benign instruction-like content. Expected answers are used after generation, not supplied as model answer keys. Arbitrary live questions show measured latency and citations but do not automatically change benchmark scores. The separate privacy suite remains unrun and is omitted from the main presentation for brevity.','Compare predefined cases consistently. Keep errors, missing outcomes and human judgments explicit.')

outcome=json.loads((ROOT/'docs/current25/LIVE_OUTCOME.json').read_text())
summary=list(csv.DictReader((ROOT/'results/current25/summary.csv').open()))
new('Current live results: partial, not complete',note='The authorized main run stopped on its first operational failure: Azure content_filter at development-07 / A. Six benign cases completed across all modes. All 18 non-error rows passed declared automatic task checks. There are no eligible graded attack observations, so ASR is N/A. Human quality has no ratings. No request was retried and no fallback was used. Historical 45-document metrics are deliberately omitted to avoid presenting them as current results.')
rows=[['Measure','A','B','C'],['Benign task success']+[f"{r['benign_task_success_numerator']}/{r['benign_task_success_denominator']}" for r in summary],['Attack success rate','N/A','N/A','N/A'],['Human quality','Unrated','Unrated','Unrated'],['Mean route latency']+[f"{float(r['mean_latency_s']):.2f} s" for r in summary]]
for j,row in enumerate(rows):
 yy=1.15+j*.51;box(.55,yy,8.9,.49,NAVY if j==0 else LIGHT,round=False);xx=.55
 for k,value in enumerate(row):
  w=3.2 if k==0 else 1.9;text(xx+.12,yy+.11,w-.2,.32,value,13,WHITE if j==0 else TEXT,j==0);xx+=w
text(.65,3.91,8.6,.60,f"{outcome['recorded_rows']}/141 rows saved · 1 Azure content-filter failure · {outcome['unrun_rows']} rows unrun\n{outcome['provider_calls_reserved']} calls consumed · No retry or fallback",13,RED)
band('Provider refusal is an operational error, not a successful application defense.')

two('Demo and takeaways',('Explain it in this order','Select a document and ask a question\nShow the retrieved source passages\nExplain the A / B / C branches\nOpen saved answers and references\nShow the measured results and limits'),('What we can conclude','The document RAG workflow is working\nSix benign cases passed in each mode\nThe attack comparison is incomplete\nHuman quality still needs real ratings\nThe stopped scope cannot be resumed'),'Use saved results to demonstrate the project. Show a benign source and explain where direct or indirect injection would enter. Do not claim a defense winner from these partial observations. More untouched-case evaluation requires its own bounded authorization; do not retry the provider-refused request or change Azure filters.','Project outcome: a working comparison framework; current evidence does not establish a security winner.')

pptx=OUT/'AI_Security_Short_8_Slides.pptx';prs.save(pptx)
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
images[0].save(OUT/'AI_Security_Short_8_Slides.pdf',save_all=True,append_images=images[1:],resolution=128)
contact=Image.new('RGB',(1280,math.ceil(len(images)/3)*265),'#E5E7EB');dc=ImageDraw.Draw(contact)
for i,im in enumerate(images):
 thumb=im.resize((400,225));x=15+(i%3)*425;y=10+(i//3)*265;contact.paste(thumb,(x,y));dc.text((x,y+229),f'{i+1:02}  {notes[i][0]}',fill='#1F2937',font=font(10))
contact.save(OUT/'Slide_Overview.png')
with (OUT/'Presenter_Notes.md').open('w') as f:
 f.write('# AI Security Document Lab — presenter notes\n\n29 October 2026 · Abhishek Sharma\n\n')
 for i,(title,note) in enumerate(notes,1):f.write(f'## {i}. {title}\n\n{note}\n\n')
 f.write('## Source of truth\n\n- results/summary.csv: historical main benchmark metrics.\n- backend/benchmark_current25/manifest.json: current 25 documents and all 47 cases.\n- results/current25/: current partial live results and operational failure.\n- results/records.csv: actual observations and errors.\n- results/document_privacy/: privacy-suite coverage.\n- backend/app/: implemented architecture and defense policies.\n- eval_config.yaml: shared model settings.\n- docs/presentation/2026-10-29-defense-evaluation/build_presentation.py: reused local layout helpers.\n\nPDF/PNG are matching visual previews generated from the same layout; the PPTX contains native editable text, shapes and arrows. Font substitution can slightly change rendering in other PowerPoint installations.\n')

check=Presentation(pptx)
assert len(check.slides)==8
for num,slide in enumerate(check.slides,1):
 assert slide.has_notes_slide
 for s in slide.shapes:
  assert s.left>=0 and s.top>=0 and s.left+s.width<=check.slide_width+1000 and s.top+s.height<=check.slide_height+1000,(num,s.name)
(OUT/'Validation.json').write_text(json.dumps({'slides':len(check.slides),'notes':len(notes),'bounds_check':'passed','provider_calls':0,'preview':'Scene-based PDF; PowerPoint font rendering may vary'},indent=2))
print(pptx)
print(f'{len(check.slides)} slides; notes and boundary checks passed.')
