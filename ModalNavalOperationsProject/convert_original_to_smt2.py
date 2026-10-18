"""Translate the typed first-order fragment in the supplied naval input.
Usage: python3 convert_original_to_smt2.py naval_operations_scenario.tff output.smt2
The output checks axioms AND negation of the active conjecture.
"""
import re
import sys
from pathlib import Path

# Parser for the Boolean, equality, and typed-quantifier fragment used here.
class Parser:
    def __init__(self, text):
        self.tokens = re.findall(r'<=>|=>|!=|[A-Za-z_$][A-Za-z0-9_$]*|[!?:(),\[\]&|~=]', text)
        self.i = 0
    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None
    def take(self, expected=None):
        value=self.peek()
        if expected is not None and value != expected: raise ValueError((expected,value))
        self.i+=1
        return value
    def expr(self, minimum=0):
        x=self.primary();priorities={'<=>':1,'=>':2,'|':3,'&':4,'=':5,'!=':5}
        while self.peek() in priorities and priorities[self.peek()]>=minimum:
            op=self.take();y=self.expr(priorities[op]+(0 if op=='=>' else 1));x=(op,x,y)
        return x
    def primary(self):
        tok=self.take()
        if tok=='~':return ('~',self.primary())
        if tok in ('!','?'):
            self.take('[');variables=[]
            while True:
                name=self.take();self.take(':');sort=self.take();variables.append((name,sort))
                if self.peek()!=',':break
                self.take(',')
            self.take(']');self.take(':');return (tok,variables,self.expr(5))
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


def records(text):
    text=re.sub(r'%[^\n]*','',text)
    for match in re.finditer(r'\btff\s*\(',text):
        start=match.end();depth=1;i=start
        while depth:
            depth+=(text[i]=='(')-(text[i]==')');i+=1
        name,role,formula=text[start:i-1].split(',',2)
        yield name.strip(),role.strip(),formula.strip()


def smt(tree):
    op=tree[0]
    if op=='symbol':return tree[1]
    if op=='call':return '('+tree[1]+''.join(' '+smt(x) for x in tree[2])+')'
    if op=='~':return '(not '+smt(tree[1])+')'
    if op in ('!','?'):
        variables=' '.join('('+v+' '+sort+')' for v,sort in tree[1])
        return '('+('forall' if op=='!' else 'exists')+' ('+variables+') '+smt(tree[2])+')'
    a,b=smt(tree[1]),smt(tree[2])
    if op=='!=':return '(not (= '+a+' '+b+'))'
    return '('+{'&':'and','|':'or','=>':'=>','<=>':'=','=':'='}[op]+' '+a+' '+b+')'


def convert(source):
    declarations=[];assertions=[];queries=[]
    for name,role,formula in records(source):
        if role=='type':
            symbol,typ=[x.strip() for x in formula.split(':',1)]
            if typ=='$tType':declarations.append(f'(declare-sort {symbol} 0)')
            elif '>' in typ:
                args,result=typ.split('>');args=' '.join(x.strip() for x in args.strip().strip('()').split('*'))
                result='Bool' if result.strip()=='$o' else result.strip()
                declarations.append(f'(declare-fun {symbol} ({args}) {result})')
            else:declarations.append(f'(declare-fun {symbol} () {typ})')
            continue
        parser=Parser(formula);tree=parser.expr();assert parser.i==len(parser.tokens)
        if role=='axiom':assertions.append('; '+name+'\n(assert (! '+smt(tree)+' :named '+name+'))')
        elif role=='conjecture':queries.append((name,tree))
        else:raise ValueError('Unsupported TFF role '+role)
    assert len(queries)==1,'Select exactly one active conjecture.'
    name,tree=queries[0]
    header='''; Exact translation of the active naval_operations_scenario.tff input.
; 46 axioms. No domain closure or priority constraints have been added.
; A theorem test asserts axioms AND the negation of the active conjecture.
; The active conjecture is NOT unresolvable_conflict(w0).
; Thus SAT here is a counterexample to the claimed absence of unresolved conflict.
; Timeout is 600000 milliseconds = 600 seconds per check.
(set-logic UF)
(set-option :produce-models true)
(set-option :timeout 600000)
'''
    footer='; Negation of active conjecture '+name+'\n(assert (! (not '+smt(tree)+') :named negated_conjecture))\n(check-sat)\n(get-info :all-statistics)\n'
    return header+'\n'.join(declarations)+'\n\n'+'\n\n'.join(assertions)+'\n\n'+footer

if __name__=='__main__':
    source,destination=map(Path,sys.argv[1:3])
    destination.write_text(convert(source.read_text()))
    print('Converted all active axioms and the negated active conjecture to',destination)
