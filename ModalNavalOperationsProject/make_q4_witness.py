"""Ground every original axiom in the exhibited finite countermodel.
This is a separate finite witness check, not an equivalent unbounded search.
The generated problem is propositional and fixes the witness interpretation.
"""
from pathlib import Path
from itertools import product
from check_supplied_tff import load, make_model, evaluate

root=Path(__file__).resolve().parent
source=load(root/'naval_operations_scenario.tff')
model=make_model(nsd_warning=True)
atoms={}


def translate(tree,env=None):
    env={} if env is None else env
    op=tree[0]
    if op=='symbol':return env.get(tree[1],tree[1])
    if op=='call':
        args=tuple(translate(x,env) for x in tree[2])
        name=tree[1]+'__'+'__'.join(args)
        value=bool(model['predicates'][tree[1]](*args))
        if name in atoms:assert atoms[name]==value
        atoms[name]=value
        return name
    if op=='~':return '(not '+translate(tree[1],env)+')'
    if op in ('!','?'):
        variables=tree[1]
        values=[translate(tree[2],env|dict(zip([v for v,t in variables],vs)))
                for vs in product(*(model['domains'][t] for v,t in variables))]
        return '('+('and' if op=='!' else 'or')+' '+' '.join(values)+')'
    if op in ('=','!='):
        value=translate(tree[1],env)==translate(tree[2],env)
        return 'true' if (value if op=='=' else not value) else 'false'
    return '('+{'&':'and','|':'or','=>':'=>','<=>':'='}[op]+' '+translate(tree[1],env)+' '+translate(tree[2],env)+')'

assertions=[]
for name,role,tree in source:
    if role=='axiom':
        assert evaluate(tree,model),name
        assertions.append('; Original axiom '+name+'\n(assert '+translate(tree)+')')
    elif role=='conjecture':
        assert not evaluate(tree,model)
        assertions.append('; Negation of original Q4\n(assert (not '+translate(tree)+'))')

header='''; Finite witness verification for the ORIGINAL 46-axiom naval input.
; Domains are exactly 3 worlds, 3 authorities, 1 agent, and 6 propositions.
; Each quantifier is expanded over that entire finite domain.
; Distinct displayed constants are interpreted as distinct domain elements.
; Every predicate value is fixed to the proved NSD-warning countermodel.
; SAT verifies this specific model of axioms AND negation of Q4.
; This is NOT an equivalent replacement for unrestricted quantified search.
(set-logic QF_UF)
(set-option :timeout 60000)
'''
declarations='\n'.join('(declare-fun '+name+' () Bool)' for name in sorted(atoms))
facts='\n'.join('(assert '+(name if value else '(not '+name+')')+')' for name,value in sorted(atoms.items()))
text=header+declarations+'\n\n; Witness truth table\n'+facts+'\n\n'+'\n\n'.join(assertions)+'\n(check-sat)\n(get-info :all-statistics)\n'
(root/'naval_q4_countermodel_check.smt2').write_text(text)
print(f'Generated all {len(assertions)-1} original axioms plus negated Q4 and {len(atoms)} Boolean witness values.')
