def parse(lines):
    idx = 0 # pe a cata linie sunt -1 ( indexata de la 0)

    n = int(lines[idx].strip()) ## numar de stari
    idx += 1

    stari = lines[idx].strip().split() ##starile automatului
    idx += 1

    m = int(lines[idx].strip()) ## numarul de tranzitii
    idx += 1

    delta = {} ## procesare de tranzitii
    #delta: {st_plec1 { 'litera1' : ['st_fin1' , 'st_fin2'] , 'litera2' : ['st_fin1', 'st_fin2' ] } st_plec2 .... } si tot asa
    alfabet = set() ## alfabetul pentru bonus
    for _ in range(m):
        parts = lines[idx].strip().split()
        idx += 1
        stare_plecare, stare_finala, simbol = parts[0], parts[1], parts[2] # procesat starile

        if stare_plecare not in delta:
            delta[stare_plecare] = {}
        if simbol not in delta[stare_plecare]:
            delta[stare_plecare][simbol] = [] # procesez stare plecare, simbol --> stare finala
        delta[stare_plecare][simbol].append(stare_finala) # adica practic din fiecare stare unde pot ajunge cu fiecare simbol

        if simbol != 'lambda':
            alfabet.add(simbol) ## alfabet pt bonus

    stare_init = lines[idx].strip() # stare initiala
    idx += 1

    nr_fin = int(lines[idx].strip()) #nr stari finale
    idx += 1

    stari_fin = set(lines[idx].strip().split()) # stari finale
    idx += 1

    nr_cuvinte = int(lines[idx].strip()) # nr cuvinte
    idx += 1

    cuvinte = [] #cuvinte
    for _ in range(nr_cuvinte):
        cuvinte.append(lines[idx].strip())
        idx += 1

    return stari, delta, stare_init, stari_fin, cuvinte, alfabet ## parsare terminata

def run_dfa(tranzitii, stare_init, stari_fin, cuvant):
    stare_curenta = stare_init
    tranzitii_folosite = []

    # Cuvantul gol: verificam doar daca starea initiala e finala
    if cuvant == '':
        return stare_curenta in stari_fin, []

    for simbol in cuvant:
        # Cautam tranzitia (stare_curenta, simbol) -> stare_dest
        if stare_curenta in tranzitii and simbol in tranzitii[stare_curenta]:
            dest = tranzitii[stare_curenta][simbol][0]  # DFA: luam primul (ar trebui sa fie unic)
            tranzitii_folosite.append((stare_curenta, simbol, dest))
            stare_curenta = dest
        else:
            return False, tranzitii_folosite ## refuza cuvantul

    return stare_curenta in stari_fin, tranzitii_folosite


def proc_dfa(fisier_input, fisier_output):
    with open(fisier_input, 'r') as f:
        lines = f.readlines()

    stari, tranzitii, stare_init, stari_fin, cuvinte, alfabet = parse(lines)

    print(f"[DFA] Alfabet: {sorted(alfabet)}")

    rezultate = []
    for cuvant in cuvinte:

        acceptat, tranz_folosite = run_dfa(tranzitii, stare_init, stari_fin, cuvant)
        rezultate.append("DA" if acceptat else "NU")

        if acceptat:
            print(f"[DFA] Cuvant '{cuvant}' ACCEPTAT. Tranzitii: {tranz_folosite}")
        else:
            print(f"[DFA] Cuvant '{cuvant}' RESPINS. ")

    with open(fisier_output, 'w') as f:
        for r in rezultate:
            f.write(r + '\n')

    print(f"[DFA] Rezultate scrise in '{fisier_output}'")


def run_nfa(tranzitii, stare_init, stari_fin, cuvant):

    # Multimea starilor curente - incepem cu starea initiala
    stari_curente = {stare_init}
    tranzitii_folosite = []

    if cuvant == '':
        return bool(stari_curente & stari_fin), []

    for simbol in cuvant:
        stari_noi = set()
        tranz_pas = []

        for stare in stari_curente:
            for dest in tranzitii.get(stare, {}).get(simbol, []):
                stari_noi.add(dest)
                tranz_pas.append((stare, simbol, dest))

        tranzitii_folosite.extend(tranz_pas)
        stari_curente = stari_noi

        if not stari_curente:
            # Nicio stare posibila => respingem
            return False, tranzitii_folosite

    acceptat = bool(stari_curente & stari_fin)
    return acceptat, tranzitii_folosite


def proc_nfa(fisier_input, fisier_output):
    with open(fisier_input, 'r') as f:
        lines = f.readlines()

    stari, tranzitii, stare_init, stari_fin, cuvinte, alfabet = parse(lines)

    print(f"[NFA] Alfabet: {sorted(alfabet)}")

    rezultate = []
    for cuvant in cuvinte:
        acceptat, tranz_folosite = run_nfa(tranzitii, stare_init, stari_fin, cuvant)
        rezultate.append("DA" if acceptat else "NU")

        # BONUS: afisam tranzitiile folosite pentru cuvintele acceptate
        if acceptat:
            print(f"[NFA] Cuvant '{cuvant}' ACCEPTAT. Tranzitii: {tranz_folosite}")
        else:
            print(f"[DFA] Cuvant '{cuvant}' RESPINS.")

    with open(fisier_output, 'w') as f:
        for r in rezultate:
            f.write(r + '\n')

    print(f"[NFA] Rezultate scrise in '{fisier_output}'")


def lambda_closure(stari_initiale, tranzitii):

    inchidere = set(stari_initiale)
    stiva = list(stari_initiale)

    while stiva:
        stare_curenta = stiva.pop()
        for stare_urmatoare in tranzitii.get(stare_curenta, {}).get('lambda', []):
            if stare_urmatoare not in inchidere:
                inchidere.add(stare_urmatoare)
                stiva.append(stare_urmatoare)

    return inchidere


def run_nfa_lambda(tranzitii, stare_init, stari_fin, cuvant):

    # Pasul initial: lambda-closure al starii initiale
    stari_curente = lambda_closure({stare_init}, tranzitii)
    tranzitii_folosite = []

    if cuvant == '':
        return bool(stari_curente & stari_fin), []

    for simbol in cuvant:
        stari_dupa_simbol = set()
        tranz_pas = []

        # Urmeaza tranzitia pe simbol din fiecare stare curenta
        for stare in stari_curente:
            if stare in tranzitii and simbol in tranzitii[stare]:
                for dest in tranzitii[stare][simbol]:
                    stari_dupa_simbol.add(dest)
                    tranz_pas.append((stare, simbol, dest))

        # Aplica lambda-closure dupa tranzitia pe simbol
        stari_curente = lambda_closure(stari_dupa_simbol, tranzitii)
        tranzitii_folosite.extend(tranz_pas)

        # Adauga si tranzitiile lambda efectuate
        for s in stari_dupa_simbol:
            for dest in lambda_closure(s, tranzitii):
                if dest != s:
                    tranzitii_folosite.append((s, 'lambda', dest))

        if not stari_curente:
            return False, tranzitii_folosite

    acceptat = bool(stari_curente & stari_fin)
    return acceptat, tranzitii_folosite


def proc_nfa_lambda(fisier_input, fisier_output):
    with open(fisier_input, 'r') as f:
        lines = f.readlines()

    stari, tranzitii, stare_init, stari_fin, cuvinte, alfabet = parse(lines)

    print(f"[NFA-λ] Alfabet: {sorted(alfabet)}")

    rezultate = []
    for cuvant in cuvinte:
        acceptat, tranz_folosite = run_nfa_lambda(tranzitii, stare_init, stari_fin, cuvant)
        rezultate.append("DA" if acceptat else "NU")

        # BONUS: afisam tranzitiile folosite pentru cuvintele acceptate
        if acceptat:
            print(f"[NFA-λ] Cuvant '{cuvant}' ACCEPTAT. Tranzitii: {tranz_folosite}")
        else:
            print(f"[DFA] Cuvant '{cuvant}' RESPINS.")

    with open(fisier_output, 'w') as f:
        for r in rezultate:
            f.write(r + '\n')

    print(f"[NFA-λ] Rezultate scrise in '{fisier_output}'")



proc_nfa('nfa_input.txt', 'nfa_output.txt')
print('\n')
proc_dfa('dfa_input.txt', 'dfa_output.txt')
print('\n')
proc_nfa('nfa_input.txt', 'nfa_output.txt')
