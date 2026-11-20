"""Matplotlib PNGs built only from observed data; missing values are never zeros."""
from io import BytesIO
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

COLORS=['#315CCC','#159C87','#D88932']


def png(fig):
    stream=BytesIO();FigureCanvasAgg(fig).print_png(stream)
    return stream.getvalue()


def coverage_chart(summary):
    fig=Figure(figsize=(9,2.8),layout='constrained');ax=fig.subplots()
    rows={r['mode']:r for r in summary}
    series=[('Recorded, non-error','#159C87',lambda r:max(0,r.get('n_recorded',0)-r.get('n_errors',0))),
            ('Operational error','#D88932',lambda r:r.get('n_errors',0)),
            ('Not run','#D8DFEB',lambda r:r.get('n_missing',0))]
    left=[0,0,0]
    for label,color,extract in series:
        values=[extract(rows.get(m,{})) for m in 'ABC']
        bars=ax.barh(list('ABC'),values,left=left,label=label,color=color,height=.52)
        for i,(bar,n) in enumerate(zip(bars,values)):
            if n:ax.text(left[i]+n/2,bar.get_y()+bar.get_height()/2,str(n),ha='center',va='center',fontsize=10)
        left=[a+b for a,b in zip(left,values)]
    ax.set_title('Evaluation coverage by configuration',loc='left',fontweight='bold',pad=14)
    ax.set_xlabel('Case-mode observations');ax.invert_yaxis()
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.27),ncol=3,frameon=False)
    if not any(left):ax.text(.5,.5,'No saved observations',transform=ax.transAxes,ha='center')
    return png(fig)


def metric_chart(summary):
    fig=Figure(figsize=(11,5.7),layout='constrained');axes=fig.subplots(2,3).ravel()
    rows={r['mode']:r for r in summary}
    specs=[('asr_all','Attack success rate','%',100),('benign_task_success','Benign task success','%',100),
           ('pdf_false_positive_rate','False positive rate (C only)','%',100),
           ('mean_quality','Human quality',' / 4',1),('mean_latency_s','Mean route latency',' s',1)]
    for ax,(key,title,unit,scale) in zip(axes,specs):
        values=[rows.get(m,{}).get(key) for m in 'ABC']
        valid=[v for v in values if isinstance(v,(int,float)) and math.isfinite(v)]
        maximum=115 if scale==100 else 4.6 if key=='mean_quality' else max(1.0,max(valid,default=1)*1.35)
        ax.set_ylim(0,maximum);ax.set_xticks(range(3),list('ABC'))
        for i,v in enumerate(values):
            if not isinstance(v,(int,float)) or not math.isfinite(v):
                ax.text(i,maximum*.45,'Not graded' if key=='mean_quality' else 'Unavailable',ha='center',fontsize=8,rotation=90)
                continue
            height=v*scale;ax.bar(i,height,color=COLORS[i],width=.55)
            numerator=rows.get('ABC'[i],{}).get(key+'_numerator')
            denominator=rows.get('ABC'[i],{}).get(key+'_denominator')
            sample=f'\n{numerator}/{denominator}' if denominator is not None else ''
            ax.text(i,height+maximum*.035,f'{height:.1f}{unit}'+sample,ha='center',fontsize=9)
        ax.set_title(title,fontsize=11,loc='left');ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
    axes[-1].axis('off');axes[-1].text(0,.85,'Missing observations stay unavailable.\nErrors do not count as defense wins.\nQuality requires actual human ratings.\nFractions show eligible sample counts.\nLatency includes recorded error routes.',va='top',fontsize=10,linespacing=1.7)
    fig.suptitle('A / B / C · observed metrics',fontweight='bold',x=.02,ha='left')
    return png(fig)


def uploaded_chart(observations):
    fig=Figure(figsize=(8,3),layout='constrained');ax=fig.subplots()
    states=['answered','conflict','insufficient_evidence','policy_blocked']
    states+=sorted({r['status'] for r in observations}-set(states))
    states=[s for s in states if any(r['status']==s for r in observations)]
    if states:
        values=[sum(r['status']==s for r in observations) for s in states]
        ax.barh([s.replace('_',' ') for s in states],values,color='#315CCC')
        ax.set_xlabel('Saved responses');ax.invert_yaxis()
    else:
        ax.text(.5,.5,'No uploaded-document responses recorded yet',ha='center',va='center',transform=ax.transAxes)
        ax.set_xticks([]);ax.set_yticks([])
    ax.set_title('Uploaded-document response outcomes',loc='left',fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    return png(fig)
