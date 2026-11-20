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

new('AI Security Document Lab',note='Start with the user journey: a person selects a document, asks a question and receives a cited answer. Then explain where prompt injection enters and why the project compares three defense configurations. The following slides follow the actual application flow before discussing results.')
text(.65,1.25,8.5,1.3,'From document upload\nto a safer, cited answer',31,NAVY,True)
text(.65,2.95,8.5,.9,'Project workflow · A/B/C defenses · Recorded evaluation',19,TEXT)
text(.65,4.08,8.3,.7,'Abhishek Sharma\n29 October 2026',15,MUTED)

two('1. What problem does the project solve?',('User goal','Upload or select a document\nAsk a business question\nGet an evidence-based answer\nCheck the cited source'),('Security problem','A question can contain an attack\nA document can contain an attack\nAn answer can be manipulated\nProtected information can leak'),'Explain RAG first: retrieve relevant passages and supply them to an answering model. Direct injection comes through a question; indirect injection comes through source text. The project measures whether added defenses preserve useful answers while resisting these instructions.','Project goal: compare security and useful task completion together.')

flow('2. The complete application journey', [('01 · Select source','Upload a file or choose a\npredefined document.'),('02 · Prepare locally','Parse → chunk → embed\n→ verify the local index.'),('03 · Retrieve evidence','Question → local embedding\n→ relevant Chroma passages.'),('04 · Apply A / B / C','Baseline, separation, or\nscreening plus checks.'),('05 · Return answer','Azure generation → schema\nand citation-ID validation.'),('06 · Inspect outcomes','Show answer and references;\nevaluate saved test records.')], 'Read the top row left to right, then the bottom row. Indexing happens when documents are prepared; it is not repeated for every question. Evaluation is a separate controlled workflow, not automatic grading of every interactive question. Local-only search stops before provider generation.', 'Two paths: prepare the document once; retrieve and answer for each question.')

flow('3. Upload → usable document text',[('01 · Validate upload','Accept supported file types\nand check upload constraints.'),('02 · Extract text','TXT / MD, text PDF, DOCX\nare parsed locally.'),('03 · Preserve identity','Track source, document hash\nand version metadata.'),('04 · Create chunks','Split into 1,000 characters\nwith 150-character overlap.'),('05 · Build local index','Embed chunks on CPU;\nstore vectors and metadata.'),('06 · Activate version','Only a successfully prepared\nversion becomes searchable.')], 'Implementation: backend/app/ingestion/lifecycle.py and parsers.py, followed by rag/indexer.py. Parsing does not certify source text as trustworthy. A failed replacement preserves the currently active document version. Text PDFs are supported; do not imply scanned-image OCR is implemented.', 'Document preparation is local; it requires no answering-model request.')

flow('4. Inside indexer.py: building a trusted index',[('01 · Validate chunks','Check required IDs, offsets,\nchecksums and configuration.'),('02 · Identify collection','Hash chunk metadata and\nembedding configuration.'),('03 · Verify existing data','Reject unexpected IDs or\nchanged text and metadata.'),('04 · Embed pending chunks','MiniLM runs locally on CPU;\nvalidate generated vectors.'),('05 · Add to Chroma','Store chunk text, embeddings\nand provenance metadata.'),('06 · Verify completion','Recheck records and mark\nthe collection verified.')], 'This slide explains the open IDE file. index_chunks validates inputs, calculates a dataset version and uses a versioned enterprise_documents collection. Existing records are checked before missing chunks are added in batches. Interrupted building collections can resume after verification; verified but incomplete collections fail. Index integrity checks protect consistency, not against malicious meaning inside valid text.', 'Why it matters: retrieval must use consistent text, vectors and source identities.')

flow('5. Question → relevant source passages',[('01 · Choose library','Uploaded documents or the\nisolated predefined index.'),('02 · Embed question','Use the same local embedding\nmodel as the source chunks.'),('03 · Search Chroma','Search the selected active\ndocument versions.'),('04 · Rank matches','Sort by cosine distance\nwith deterministic tie breaks.'),('05 · Bound evidence','Keep up to five passages\nwithin the evidence byte limit.'),('06 · Attach provenance','Return chunk IDs, source,\nversion and location metadata.')], 'Implementation: rag/retrieval.py and retriever.py. The uploaded-library implementation ranks by distance and ID, selects at most top_k=5 and bounds selected text to 12,000 bytes. The predefined library uses its own isolated index. Smaller cosine distance indicates similarity, not factual confidence. No answer keys are retrieved from evaluation labels.', 'The answering model receives selected passages, rather than the whole document library.')

two('6. Where prompt injection enters',('Direct: user question','Normal request plus hostile text\nExample: ask about policy, then\nrequest an instruction override\n\nEntry point: question input'),('Indirect: document text','Relevant facts plus hostile text\nExample: a policy passage tells\nthe assistant to reveal a secret\n\nEntry point: retrieved evidence'),'Use these as illustrative attack descriptions, not actual saved outputs. Retrieval can correctly find a relevant passage that also contains malicious instructions. The trust boundary is between application policy and untrusted question/source content. Format validation and similarity retrieval do not solve this semantic problem.','The defense must distinguish evidence to read from instructions to obey.')

new('7. A / B / C: the actual defense branches',note='All modes start with the same initial evidence in a controlled comparison. A already has grounding rules; it is not unrestricted. B adds privileged instruction separation without filtering chunks. C screens question and sources, may block or remove sources, then uses B answering and a payment-card output-pattern check. C reserves capacity for up to two calls; A/B reserve one.')
card(.55,1.15,2.84,3.20,'A · Standard RAG','Original evidence\n↓\nGrounded prompt\n↓\nAzure answer\n↓\nSchema + citation IDs',NAVY,14)
card(3.58,1.15,2.84,3.20,'B · Separation','Original evidence\n↓\nTrusted separation rules\n↓\nAzure answer\n↓\nSchema + citation IDs',BLUE,14)
card(6.61,1.15,2.84,3.20,'C · Screen + check','Screen question + sources\n↓\nBlock or filter evidence\n↓\nB answer, if usable\n↓\nCard-pattern output check',RED,14)
band('A/B: one generation call. C: screening plus generation, when the branch proceeds.')

flow('8. C mode: decisions before answering',[('01 · Screen inputs','LLM examines the question\nand candidate source chunks.'),('02 · Validate decision','Strict schema, known source\nIDs and consistent reasons.'),('03 · Question flagged?','If flagged, block the request\nbefore answer generation.'),('04 · Filter sources','Remove flagged chunks;\nretain original safe records.'),('05 · Evidence remains?','If none remains, return\ninsufficient evidence.'),('06 · Answer + check','Use B answering; withhold\npossible full-card output.')], 'These are conditional branches, not six unavoidable calls. screening.apply returns early for a flagged question or screening error. Unknown source IDs and contradictory metadata are errors, not decisions to repair silently. If unflagged evidence remains, B generates and C checks the answer for payment-card patterns. This output check is not a universal secret detector.', 'A provider refusal or invalid screening response is an operational error, not a defense win.')

flow('9. Answer generation → displayed response',[('01 · Check authorization','Existing Azure deployment;\nvalidate scope and reserve.'),('02 · Send bounded request','gpt-5-mini, minimal reasoning,\n700-token completion cap.'),('03 · Validate answer','Parse the strict answer\ncontract and status fields.'),('04 · Validate citations','Reject unknown source IDs\nor missing required IDs.'),('05 · Apply C output check','C checks for card patterns\nbefore releasing the answer.'),('06 · Show answer + sources','UI masks recognized cards\nacross all three modes.')], 'Authorization is checked around provider execution; C reserves before screening. Azure requests omit temperature identically for A/B/C. There are no automatic retries or fallback models. Schema checks validate structure; citation-ID checks establish membership in supplied evidence, not semantic support. UI masking does not modify saved raw evidence and is not scored as B model resistance.', 'The local-only option shows retrieved evidence without calling the answering model.')

two('10. One example to explain the whole flow',('Illustrative business task','Document: employee leave policy\nQuestion: how do I request leave?\nRetrieve the approval passage\nAnswer with source references'),('Add an indirect attack','Passage also says: ignore rules\nand reveal a private value\nA: grounded answering\nB: separate data from instructions\nC: screen before B answering'),'This is a teaching example, not a new experiment and not a prediction of which answer a mode will produce. Walk through upload, chunk embedding, retrieval and each defense branch. Expected safe behavior is to answer the legitimate policy question without following the disclosure instruction. Recorded outcomes are shown separately later.', 'Expected behavior: preserve the useful policy answer while withholding protected information.')

flow('11. How the controlled evaluation runs',[('01 · Load frozen cases','25 source documents;\n47 cases in the main suite.'),('02 · Freeze initial evidence','Save the same starting\nretrieval for A / B / C.'),('03 · Execute each mode','Use shared model settings;\nchange the defense treatment.'),('04 · Save actual outcomes','Preserve answers, errors,\ntraces and implementation IDs.'),('05 · Grade and review','Evaluate task and attack\nseparately; humans resolve doubt.'),('06 · Aggregate metrics','Report eligible denominators,\nquality coverage and timing.')], 'The current local plan and preparation entry point is backend/scripts/current25_eval.py; historical run_eval.py remains separate. A new live authorization is required for the current study. Expected answers and attack objectives are used after generation, never supplied as model answer keys. Operational errors and pending judgments are excluded from graded security denominators. Historical implementations and continuations retain their original provenance.', 'Interactive answers do not automatically become graded frozen-benchmark observations.')

two('12. What the five metrics tell us',('Security and usefulness','Attack success rate: lower is better\nBenign task success: higher is better\nFalse positives: lower is better\n\nTask success and attack success\nare separate judgments.'),('Quality and overhead','Human quality rating: 0–4\nRoute latency: mean and p95\n\nUnrated quality stays N/A.\nErrors are recorded explicitly.\nBlocking can lose a useful task.'),'Metric definitions come from the saved reporting implementation. Attack success uses eligible graded adversarial rows; benign success uses eligible benign rows. C false positives measure benign inputs flagged, filtered or blocked. Recorded route timing includes errors and excludes shared initial retrieval. A/B false-positive screening metrics are not applicable.', 'A low attack-success rate alone does not establish the best defense.')

two('13. Current study: 25 documents, all 47 cases',('What changed','25 source packs preserve 45 originals\nAll 47 cases remain in the study\n21 benign + 26 adversarial cases\nA uses standard grounded RAG\nB separates; C screens and checks'),('What must be measured anew','141 planned A/B/C rows\nUp to 188 provider calls\nCurrent live observations: 0\nUnrun rates remain N/A\nHistorical results stay separate'),'The new dataset consolidates original source sections without deleting cases. Benign and attack-bearing sections remain separate. Dataset and baseline identities changed, so do not transfer historical scores. All supporting quotes were found in local retrieval verification. That local check is not evidence of model resistance. No duplicate hard cases were added because the original suite already includes forged roles, obfuscation, misinformation and cross-chunk attacks.','The following result table describes the historical 45-document experiment only.')

new('Historical main benchmark: recorded results',note='Read from results/summary.csv at build time. Historical main results use recorded earlier policies, not proof that the newer business-summary-v7 policy has been evaluated. Graded denominators differ because operational errors and unresolved judgments are excluded. The attack-task figures come from actual eligible saved rows. Four human quality ratings are too few for a strong quality conclusion.')
summary=list(csv.DictReader((ROOT/'results/summary.csv').open()))
rows=[['Metric','A','B','C'],['Attack success']+[f"{r['asr_all_numerator']}/{r['asr_all_denominator']}" for r in summary],['Benign task success']+[f"{r['benign_task_success_numerator']}/{r['benign_task_success_denominator']}" for r in summary],['Mean route time']+[f"{float(r['mean_latency_s']):.2f} s" for r in summary],['Operational errors']+[r['n_errors'] for r in summary]]
for j,row in enumerate(rows):
 yy=1.15+j*.51;box(.55,yy,8.9,.49,NAVY if j==0 else LIGHT,round=False)
 xx=.55
 for k,v in enumerate(row):
  w=3.2 if k==0 else 1.9;text(xx+.12,yy+.11,w-.2,.32,v,13,WHITE if j==0 else TEXT,j==0);xx+=w
text(.65,3.93,8.65,.6,'141 recorded rows · 13 errors · 11 pending judgments\nOnly 4 human quality ratings; eligible mode subsets differ.',13,RED)
band('C blocked all 20 graded attack rows and completed none of their legitimate tasks.')

two('14. Current privacy suite: five tests per source',('Five tests per document','Control: no added attack\nDirect plain disclosure\nDirect encoded disclosure\nIndirect plain disclosure\nIndirect encoded disclosure'),('Current suite coverage','25 documents × 5 tests × 3 modes\n125 cases; 375 planned rows\nCurrent live observations: 0\nUp to 500 provider calls if approved\nOld 92/675 rows remain historical'),'The current privacy suite is separately versioned and uses controlled full-document evidence, rather than testing retrieval. The old 45-document suite and its 92 recorded rows are preserved. Main plus privacy workloads can require 688 calls; do not assume the existing allocation can fund both. No live execution was authorized or performed by this presentation revision.','New suites show unrun outcomes honestly; old scores do not validate the new dataset.')

flow('15. How to demonstrate the project',[('01 · Show a document','Open the document library\nand select a policy source.'),('02 · Show local retrieval','Ask a benign question in\nlocal-only mode; inspect hits.'),('03 · Explain A / B / C','Point to the three branches\nand the C decision points.'),('04 · Open saved comparison','Show actual answers, source\nreferences, blocks and errors.'),('05 · Explain the metrics','Compare task preservation\nwith attack success.'),('06 · State the limits','Review pending judgments\nand incomplete privacy rows.')], 'Use saved results for a reproducible presentation. A fresh live demonstration requires the existing current authorization and available capacity; making this deck does not execute it. Tell the story in application order rather than starting with metric tables. End by showing that useful answers and secure behavior must be assessed together.', 'Presenter sequence: user need → application flow → defense difference → evidence → limitations.')

two('16. Conclusion and next work',('What the project delivers','Local document RAG workflow\nThree distinct defense paths\nCited answers and saved evidence\nRepeatable comparison tooling\nExplicit errors and human review'),('What remains to establish','Resolve pending human judgments\nExpand quality-review coverage\nEvaluate new policies separately\nComplete only authorized new rows\nMeasure security with usability'),'Close with the implemented system and the limits of its observations. B showed a promising balance in the historical graded subset, while C lost legitimate tasks through blocking. Neither proves general security. The current policy is a later treatment and needs its own evidence. Ask for questions about the flow, defense decisions or recorded findings.', 'Questions: document preparation, retrieval, A/B/C decisions, or evaluation?')

pptx=OUT/'AI_Security_Current25_Project_Flow.pptx';prs.save(pptx)
# Reuse the matching scene renderer from the earlier local presentation builder.
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
images[0].save(OUT/'AI_Security_Current25_Project_Flow.pdf',save_all=True,append_images=images[1:],resolution=128)
contact=Image.new('RGB',(1280,math.ceil(len(images)/3)*265),'#E5E7EB');dc=ImageDraw.Draw(contact)
for i,im in enumerate(images):
 thumb=im.resize((400,225));x=15+(i%3)*425;y=10+(i//3)*265;contact.paste(thumb,(x,y));dc.text((x,y+229),f'{i+1:02}  {notes[i][0]}',fill='#1F2937',font=font(10))
contact.save(OUT/'Slide_Overview.png')
with (OUT/'Presenter_Notes.md').open('w') as f:
 f.write('# AI Security Document Lab — presenter notes\n\n29 October 2026 · Abhishek Sharma\n\n')
 for i,(title,note) in enumerate(notes,1):f.write(f'## {i}. {title}\n\n{note}\n\n')
 f.write('## Source of truth\n\n- results/summary.csv: historical main benchmark metrics.\n- backend/benchmark_current25/manifest.json: current 25 documents and all 47 cases.\n- results/current25/: current reports; no live observations yet.\n- results/records.csv: actual observations and errors.\n- results/document_privacy/: privacy-suite coverage.\n- backend/app/: implemented architecture and defense policies.\n- eval_config.yaml: shared model settings.\n- docs/presentation/2026-10-29-defense-evaluation/build_presentation.py: reused local layout helpers.\n\nPDF/PNG are matching visual previews generated from the same layout; the PPTX contains native editable text, shapes and arrows. Font substitution can slightly change rendering in other PowerPoint installations.\n')

check=Presentation(pptx)
for num,slide in enumerate(check.slides,1):
 assert slide.has_notes_slide
 for s in slide.shapes:
  assert s.left>=0 and s.top>=0 and s.left+s.width<=check.slide_width+1000 and s.top+s.height<=check.slide_height+1000,(num,s.name)
(OUT/'Validation.json').write_text(json.dumps({'slides':len(check.slides),'notes':len(notes),'bounds_check':'passed','provider_calls':0,'preview':'Scene-based PDF; PowerPoint font rendering may vary'},indent=2))
print(pptx)
print(f'{len(check.slides)} slides; notes and boundary checks passed.')
