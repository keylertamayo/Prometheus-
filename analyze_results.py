import os, json, glob

def summarize(base_dir="./evolution_sandbox"):
    gens = sorted(glob.glob(os.path.join(base_dir, "gen_*/results.json")))
    fitnesses = []
    details = []
    for path in gens:
        with open(path) as f:
            r = json.load(f)
        fitnesses.append(r["fitness"])
        details.append((r["generation"], r["dna"], r["survived"], r["hunter_report"]["memory_attack_success"]))
    print("Generations analysed:", len(fitnesses))
    for g, dna, surv, mem in details:
        print(f"Gen {g} | fitness {fitnesses[g]:.2f} | enc={dna['memory_encryption']} surv={surv} mem_comp={mem}")
    if fitnesses:
        best = max(fitnesses)
        worst = min(fitnesses)
        avg = sum(fitnesses)/len(fitnesses)
        print(f"min={worst:.2f}, max={best:.2f}, avg={avg:.2f}")
        if worst > 0:
            print(f"improvement (max/worst): {best/worst*100:.1f}%")
    
if __name__ == '__main__':
    summarize()
