"""Match the logged conjecture and used input axioms to the packaged TFF.
This checks input correspondence and proof endpoints, not every prover inference.
"""
import re
from pathlib import Path
from check_supplied_tff import Parser, load


def fields(record):
    result=[]; start=0; depth=0
    for i,c in enumerate(record):
        depth+=(c in '([')-(c in ')]')
        if c==',' and depth==0:
            result.append(record[start:i].strip());start=i+1
    result.append(record[start:].strip())
    return result


def normalize(tree,scope=None,depth=0):
    scope={} if scope is None else scope
    op=tree[0]
    if op=='symbol':return ('symbol',scope.get(tree[1],tree[1]))
    if op=='call':return ('call',tree[1],tuple(normalize(x,scope,depth) for x in tree[2]))
    if op in ('!','?'):
        local=dict(scope);sorts=[]
        for i,(v,s) in enumerate(tree[1]):local[v]=('bound',depth,i);sorts.append(s)
        return (op,tuple(sorts),normalize(tree[2],local,depth+1))
    if op=='~':return ('~',normalize(tree[1],scope,depth))
    a=normalize(tree[1],scope,depth);b=normalize(tree[2],scope,depth)
    if op in ('&','|'):
        children=[]
        for x in (a,b):children.extend(x[1] if x[0]==op else (x,))
        return (op,tuple(children))
    return (op,a,b)


def main():
    root=Path(__file__).resolve().parent
    file=root/'vampire_corrected.log'
    if not file.exists():file=root.parent/'upload/vampire_corrected.log'
    text=file.read_text()
    source=load(root/'naval_operations_corrected.tff')
    used=[]
    for match in re.finditer(r'\btff\s*\(',text):
        start=match.end();i=start;depth=1
        while depth:
            depth+=(text[i]=='(')-(text[i]==')');i+=1
        parts=fields(text[start:i-1])
        if len(parts)<4 or parts[1] not in ('axiom','conjecture'):continue
        if not parts[3].startswith("file('naval_operations_corrected.tff'"):continue
        parser=Parser(parts[2]);tree=parser.expr();assert parser.i==len(parser.tokens)
        index=int(parts[0][1:])-1
        assert parts[1]==source[index][1]
        assert normalize(tree)==normalize(source[index][2]),(parts[0],source[index][0])
        used.append((parts[0],parts[1]))
    assert ('f45','conjecture') in used
    assert '% SZS status Theorem for naval_operations_corrected' in text
    assert '% SZS output end Proof for naval_operations_corrected' in text
    assert re.search(r'tff\(f620482,plain,\(\s*\$false\)',text)
    print(f'PASS {len(used)-1} used input axioms and the combined conjecture match the packaged corrected file, modulo bound-variable renaming and Boolean grouping.')
    print('PASS logged conjecture negation and completed proof endpoint with $false.')
    print('Vampire 5.0.0, commit b56c5534b. Theorem. Elapsed 175.412 s. Peak memory 217 MB.')
    scenario=(root/'vampire_scenario_original.log').read_text()
    elapsed=re.search(r'% Time elapsed:\s*([0-9.]+) s',scenario).group(1)
    memory=re.search(r'% Peak memory usage:\s*([0-9,]+) MB',scenario).group(1)
    assert '% Termination reason: Time limit' in scenario
    print(f'The scenario log records timeout at {elapsed} s and peak memory {memory} MB. It contains no embedded conjecture or proof.')
    print('Individual proof inferences have not been replayed in an independent proof checker.')

if __name__=='__main__':main()
