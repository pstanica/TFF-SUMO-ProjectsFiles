"""Parse and evaluate the supplied TFF fragment in explicit finite structures.
This is a finite-interpretation checker, not a theorem prover or full TFF parser.
"""
import re
from itertools import product
from pathlib import Path

class Parser:
    def __init__(self, text):
        self.tokens = re.findall(r'<=>|=>|!=|[A-Za-z_$][A-Za-z0-9_$]*|[!?:(),\[\]&|~=]', text)
        self.i = 0
    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None
    def take(self, expected=None):
        value=self.peek()
        if expected is not None and value != expected:
            raise ValueError((expected,value,self.tokens[max(0,self.i-5):self.i+10]))
        self.i+=1
        return value
    def expr(self, minimum=0):
        x=self.primary()
        priorities={'<=>':1, '=>':2, '|':3, '&':4, '=':5, '!=':5}
        while self.peek() in priorities and priorities[self.peek()] >= minimum:
            op=self.take(); y=self.expr(priorities[op]+(0 if op=='=>' else 1))
            x=(op,x,y)
        return x
    def primary(self):
        tok=self.take()
        if tok=='~': return ('~',self.primary())
        if tok in ('!','?'):
            self.take('['); variables=[]
            while True:
                name=self.take();self.take(':');sort=self.take();variables.append((name,sort))
                if self.peek()!=',':break
                self.take(',')
            self.take(']');self.take(':')
            return (tok,variables,self.expr())
        if tok=='(':
            x=self.expr();self.take(')');return x
        if self.peek()=='(':
            self.take('(');args=[]
            if self.peek()!=')':
                while True:
                    args.append(self.expr())
                    if self.peek()!=',':break
                    self.take(',')
            self.take(')');return ('call',tok,args)
        return ('symbol',tok)


def load(path):
    text=re.sub(r'%[^\n]*','',Path(path).read_text())
    clauses=[]
    for match in re.finditer(r'\btff\s*\(',text):
        start=match.end();depth=1;i=start
        while depth:
            depth+=(text[i]=='(')-(text[i]==')');i+=1
        body=text[start:i-1]
        name,role,formula=body.split(',',2)
        if role.strip()=='type':continue
        parser=Parser(formula);tree=parser.expr()
        assert parser.i==len(parser.tokens),(name,parser.tokens[parser.i:])
        clauses.append((name.strip(),role.strip(),tree))
    return clauses


def evaluate(tree, model, env=None):
    env={} if env is None else env
    op=tree[0]
    if op=='symbol':
        name=tree[1]
        return env[name] if name in env else model['constants'][name]
    if op=='call':return model['predicates'][tree[1]](*(evaluate(x,model,env) for x in tree[2]))
    if op=='~':return not evaluate(tree[1],model,env)
    if op in ('!','?'):
        variables,body=tree[1:]
        vals=(evaluate(body,model,env|dict(zip([v for v,t in variables],vs)))
              for vs in product(*(model['domains'][t] for v,t in variables)))
        return all(vals) if op=='!' else any(vals)
    a=evaluate(tree[1],model,env);b=evaluate(tree[2],model,env)
    return {'&':lambda:a and b,'|':lambda:a or b,'=>':lambda:not a or b,
            '<=>':lambda:a==b,'=':lambda:a==b,'!=':lambda:a!=b}[op]()


def make_model(extra=False, nsd_warning=False):
    worlds=('w0','w1','w2')
    auths=('unclos','roe','nsd')+(('inactive_source',) if extra else ())
    props=('issue_warning','immediate_action','protect_asset','threat_detected',
           'in_territorial_waters','strategic_asset_nearby')
    constants={x:x for x in worlds+auths+props+('commander',)}
    def holds(p,w):
        if p=='issue_warning':return w=='w0'
        if p=='immediate_action':return w=='w2'
        if p=='in_territorial_waters':return w!='w1'
        return True
    def active(h,w):return h in ('roe','nsd') or (h=='unclos' and w!='w1')
    def o(h,w,u):
        return (h=='unclos' and u=='w0') or (h=='roe' and u=='w2') or (h=='nsd' and u==('w0' if nsd_warning else 'w2'))
    def obligatory(h,p,w):return all(holds(p,u) for u in worlds if o(h,w,u))
    def priority(h,k,w):return w=='w0' and h=='unclos' and k in ('roe','nsd')
    def incompatible(p,q):return all(not holds(p,u) or not holds(q,u) for u in worlds)
    def conflict(p,q,w):
        return incompatible(p,q) and any(h!=k and obligatory(h,p,w) and obligatory(k,q,w)
                                       for h in auths for k in auths)
    def unresolvable(w):
        return any(conflict(p,q,w) and obligatory(h,p,w) and obligatory(k,q,w)
                   and not priority(h,k,w) and not priority(k,h,w)
                   for p in props for q in props for h in auths for k in auths)
    predicates={'holds':holds,'active':active,'o_accessible':o,
                'k_accessible':lambda a,w,u:True,'b_accessible':lambda a,w,u:True,
                'knows':lambda a,p,w:all(holds(p,u) for u in worlds),
                'believes':lambda a,p,w:all(holds(p,u) for u in worlds),
                'obligatory':obligatory,'auth_priority':priority,'conflict':conflict,
                'effective_obligation':lambda p,w:p=='immediate_action' and w=='w0','unresolvable_conflict':unresolvable}
    return {'constants':constants,'domains':{'world':worlds,'agent':('commander',),
            'authority':auths,'prop':props},'predicates':predicates}


def main():
    path=Path(__file__).resolve().parent/'naval_operations_scenario.tff'
    if not path.exists():path=Path(__file__).resolve().parents[1]/'upload/naval_operations_scenario.tff'
    clauses=load(path)
    axioms=[c for c in clauses if c[1]=='axiom'];queries=[c for c in clauses if c[1]=='conjecture']
    print(f'Parsed {len(axioms)} active axioms and {len(queries)} active conjecture in the supported TFF fragment.')
    for extra,nsd_warning in ((False,False),(False,True),(True,False)):
        model=make_model(extra,nsd_warning)
        failures=[name for name,role,tree in axioms if not evaluate(tree,model)]
        assert not failures,failures
        print(f'PASS every supplied axiom with {len(model["domains"]["authority"])} authorities, NSD warning requirement {nsd_warning}.')
        for name,role,tree in queries:
            print(f'  {name}: {evaluate(tree,model)}')
        p=model['predicates']
        assert p['unresolvable_conflict']('w0')==(extra or nsd_warning)
        assert not p['knows']('commander','issue_warning','w0')
    print('Two three-authority models of the same active axioms disagree on Q4. Neither Q4 nor its negation is entailed, even if the displayed finite domains are closed.')
    print('NSD may additionally require a warning while requiring asset protection. The compatibility witness for action and protection does not constrain this additional normative requirement.')
    print('The extra inactive source has empty normative successors and vacuously requires every named proposition. The unresolved definition can use it twice because its own source variables need not be distinct.')

if __name__=='__main__':main()

# The corrected finite model uses warning as the negative response alternative.
def corrected_model():
    model=make_model()
    pr=model['predicates'];worlds=model['domains']['world'];auths=model['domains']['authority']
    def holds(p,w):
        if p=='immediate_action':return w=='w2'
        if p=='issue_warning':return w!='w2'
        if p=='in_territorial_waters':return w!='w1'
        return True
    d=lambda h,w,u:(h=='roe' and u=='w2') or (h=='unclos' and u=='w1') or h=='nsd'
    active=lambda h,w:h!='unclos' or w!='w1'
    priority=lambda h,j,w:h=='unclos' and j in ('roe','nsd')
    obligatory=lambda h,p,w:active(h,w) and all(holds(p,u) for u in worlds if d(h,w,u))
    weak=lambda h,p,w:active(h,w) and not all(not holds(p,u) for u in worlds if d(h,w,u))
    pos=lambda h,w:obligatory(h,'immediate_action',w)
    neg=lambda h,w:obligatory(h,'issue_warning',w)
    relevant=lambda h,w:pos(h,w) or neg(h,w)
    maximal=lambda h,w:relevant(h,w) and not any(relevant(j,w) and priority(h,j,w) for j in auths)
    ep=lambda w:any(maximal(h,w) for h in auths) and all(not maximal(h,w) or pos(h,w) for h in auths)
    en=lambda w:any(maximal(h,w) for h in auths) and all(not maximal(h,w) or neg(h,w) for h in auths)
    unresolved=lambda w:any(maximal(h,w) and pos(h,w) for h in auths) and any(maximal(h,w) and neg(h,w) for h in auths)
    pr.update({'holds':holds,'o_accessible':d,'active':active,'auth_priority':priority,
               'obligatory':obligatory,'weak_permitted':weak,
               'pos':pos,'neg':neg,'relevant':relevant,'maximal':maximal,
               'defeated':lambda h,w:relevant(h,w) and not maximal(h,w),
               'effective_pos':ep,'effective_neg':en,'unresolved':unresolved,
               'issued_conflict':lambda w:any(h!=j and pos(h,w) and neg(j,w) for h in auths for j in auths),
               'requires_mediation':unresolved,
               'weak_pos':lambda h,w:weak(h,'immediate_action',w),
               'weak_neg':lambda h,w:weak(h,'issue_warning',w),
               'effective_obligation':lambda p,w:(p=='immediate_action' and ep(w)) or (p=='issue_warning' and en(w)),
               'unresolvable_conflict':unresolved,
               'territorial':lambda w:w!='w1','threat_present':lambda w:True,'asset_nearby':lambda w:True,
               'knows':lambda a,p,w:all(holds(p,u) for u in worlds),
               'believes':lambda a,p,w:all(holds(p,u) for u in worlds)})
    return model

if __name__=='__main__':
    path=Path(__file__).resolve().parent/'naval_operations_corrected.tff'
    clauses=load(path);model=corrected_model()
    failures=[name for name,role,tree in clauses if not evaluate(tree,model)]
    assert not failures,failures
    print(f'PASS every one of {len(clauses)-1} corrected finite-instance axioms and its combined policy conjecture.')
